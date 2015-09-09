#########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

from functools import wraps

from cloudify import ctx
from cloudify import context

from cloudify_agent.installer.config.attributes import AGENT_ATTRIBUTES


def attribute(name):

    def decorator(function):

        @wraps(function)
        def wrapper(cloudify_agent):

            # if the property was given in the invocation, use it.
            # inputs are first in precedence order
            if name in cloudify_agent:
                return

            if ctx.type == context.NODE_INSTANCE:

                # if the property is inside a runtime property, use it.
                # runtime properties are second in precedence order
                runtime_properties = ctx.instance.runtime_properties.get(
                    'cloudify_agent', {})
                if name in runtime_properties:
                    cloudify_agent[name] = runtime_properties[name]
                    return

                # if the property is declared on the node, use it
                # node properties are third in precedence order
                node_properties = ctx.node.properties['cloudify_agent']
                if name in node_properties:
                    cloudify_agent[name] = node_properties[name]
                    return

            # if the property is inside the bootstrap context,
            # and its value is not None, use it
            # bootstrap_context is forth in precedence order
            attr = AGENT_ATTRIBUTES.get(name)
            if attr is None:
                raise RuntimeError('{0} is not an agent attribute'
                                   .format(name))
            bs_context = ctx.bootstrap_context
            try:
                agent_context = vars(bs_context.cloudify_agent)
            except TypeError:
                # On 2.7.4 vars may fail with a TypeError, use
                # old _asdict approach (obsolete in 3)
                agent_context = bs_context.cloudify_agent._asdict()
            context_attribute = attr.get('context_attribute', name)
            if context_attribute in agent_context:
                value = agent_context.get(context_attribute)
                if value is not None:
                    cloudify_agent[name] = value
                    return

            # apply the function itself
            ctx.logger.debug('Applying function:{0} on Attribute '
                             '<{1}>'.format(function.__name__, name))
            value = function(cloudify_agent)
            if value is not None:
                ctx.logger.debug('{0} set by function:{1}'
                                 .format(name, value))
                cloudify_agent[name] = value
                return

            # set default value
            default = attr.get('default')
            if default is not None:
                ctx.logger.debug('{0} set by default value'
                                 .format(name, value))
                cloudify_agent[name] = default
                return

        return wrapper

    return decorator


def group(name):

    def decorator(group_function):

        @wraps(group_function)
        def wrapper(cloudify_agent, *args, **kwargs):

            # collect all attributes belonging to that group
            group_attributes = {}
            for attr_name, attr_value in AGENT_ATTRIBUTES.iteritems():
                if attr_value.get('group') == name:
                    group_attributes[attr_name] = attr_value

            for group_attr_name in group_attributes.iterkeys():
                # iterate and try to set all the attributes of the group as
                # defined in the heuristics of @attribute.
                @attribute(group_attr_name)
                def setter(_):
                    pass

                setter(cloudify_agent)

            # when we are done, invoke the group function to
            # apply group logic
            group_function(cloudify_agent, *args, **kwargs)

        return wrapper

    return decorator
