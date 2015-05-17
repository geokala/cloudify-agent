#########
# Copyright (c) 2013 GigaSpaces Technologies Ltd. All rights reserved
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

import click

from cloudify_agent.api.plugins.installer import PluginInstaller
from cloudify_agent.shell.decorators import handle_failures


@click.command()
@click.option('--source',
              help='URL to the plugin source code',
              required=True)
@click.option('--args',
              help='Custom installation arguments passed to the pip command',
              default='')
@handle_failures
def install(source, args):

    """
    Install a cloudify plugin into the agent virtualenv
    """

    click.echo('Installing plugin from {0}'.format(source))
    installer = PluginInstaller()
    name = installer.install(source, args)
    click.echo('Successfully installed plugin: {0}'.format(name))