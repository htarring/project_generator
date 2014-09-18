# Copyright 2014 0xc0170
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
from os.path import basename, join, relpath
from exporter import Exporter
from iar_definitions import IARDefinitions
import copy
import logging

from builder import Builder
import subprocess
import user_settings

class IARExporter(Exporter):

    def __init__(self):
        self.definitions = IARDefinitions()

    source_files_dic = ['source_files_c', 'source_files_s',
                        'source_files_cpp', 'source_files_obj', 'source_files_lib']
    core_dic = {
        "cortex-m0": 34,
        "cortex-m0+": 35,
        "cortex-m3": 38,
        "cortex-m4": 39,
        "cortex-m4f": 40,
    }

    def expand_data(self, old_data, new_data, attribute, group):
        """ Groups expansion for Sources. """
        if group == 'Sources':
            old_group = None
        else:
            old_group = group
        for file in old_data[old_group]:
            if file:
                new_data['groups'][group].append(file)

    def iterate(self, data, expanded_data):
        """ Iterate through all data, store the result expansion in extended dictionary. """
        for attribute in self.source_files_dic:
            for dic in data[attribute]:
                for k, v in dic.items():
                    if k == None:
                        group = 'Sources'
                    else:
                        group = k
                    self.expand_data(dic, expanded_data, attribute, group)

    def get_groups(self, data):
        """ Get all groups defined. """
        groups = []
        for attribute in self.source_files_dic:
            for dic in data[attribute]:
                for k, v in dic.items():
                    if k == None:
                        k = 'Sources'
                    if k not in groups:
                        groups.append(k)
        return groups

    def find_target_core(self, data):
        """ Sets Target core. """
        for k, v in self.core_dic.items():
            if k == data['core']:
                return v
        return core_dic['cortex-m0']  # def cortex-m0 if not defined otherwise

    def parse_specific_options(self, data):
        """ Parse all IAR specific setttings. """
        data['iar_settings'].update(copy.deepcopy(
            self.definitions.iar_settings))  # set specific options to default values
        for dic in data['misc']:
            # for k,v in dic.items():
            self.set_specific_settings(dic, data)

    def set_specific_settings(self, value_list, data):
        for k, v in value_list.items():
            if v[0] == 'enable':
                v[0] = 1
            elif v[0] == 'disable':
                v[0] = 0
            data['iar_settings'][k]['state'] = v[0]

    def generate(self, data):
        """ Processes groups and misc options specific for IAR, and run generator """
        expanded_dic = data.copy()

        groups = self.get_groups(data)
        expanded_dic['groups'] = {}
        for group in groups:
            expanded_dic['groups'][group] = []
        self.iterate(data, expanded_dic)

        expanded_dic['iar_settings'] = {}
        self.parse_specific_options(expanded_dic)
        expanded_dic['iar_settings'].update(
            self.definitions.get_mcu_definition(expanded_dic['mcu']))

        self.gen_file('iar.ewp.tmpl', expanded_dic, '%s.ewp' %
                      data['name'], "iar")
        self.gen_file('iar.eww.tmpl', expanded_dic, '%s.eww' %
                      data['name'], "iar")


class IARBuilder(Builder):

    def build_project(self, project, project_path):
        # > IarBuild [project_path] -build [project_name]
        path = join(self.root_path, project_path, ("iar_" + project), "%s.ewp" % project)
        logging.debug("Building IAR project: %s" % path)

        args = [user_settings.IARBUILD, path, '-build', project]

        try:
            ret_code = None
            ret_code = subprocess.call(args)
        except:
            logging.error("Error whilst calling IarBuild. Please check IARBUILD path in the user_settings.py file.")
        else:
            # no IAR doc describes errors from IarBuild
            logging.info("Build completed.")
