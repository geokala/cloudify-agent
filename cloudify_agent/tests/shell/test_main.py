#########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
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

import logging

import click

from cloudify_agent.tests.shell.commands import BaseCommandLineTestCase


class TestCommandLine(BaseCommandLineTestCase):

    def test_debug_command_line(self):

        @click.command()
        def log():
            pass

        from cloudify_agent.shell.main import main
        main.add_command(log, 'log')
        self._run('cfy-agent --debug log')

        # assert all loggers are now at debug level
        from cloudify_agent.api.utils import logger
        self.assertEqual(logger.level, logging.DEBUG)