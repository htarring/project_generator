# Copyright 2014-2015 0xc0170
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import logging

from ..workspace import PgenWorkspace

help = 'Clean generated projects'


def run(args):
    if os.path.exists(args.file):
        workspace = PgenWorkspace(args.file, os.getcwd())

        if args.project:
            return workspace.clean_project(args.project, args.tool)
        else:
            return workspace.clean_projects(args.tool)
    else:
        # not project known by pgen
        logging.warning("%s not found." % args.file)
        return -1

def setup(subparser):
    subparser.add_argument("-f", "--file", help="YAML projects file", default='projects.yaml')
    subparser.add_argument("-p", "--project", help="Specify which project to be removed")
    subparser.add_argument(
        "-t", "--tool", help="Clean project files for specified tool (uvision by default)")
