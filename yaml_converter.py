# Convert a Rogue Python file into a CPSW YAML file

import os
from collections import OrderedDict
import yaml

import pyrogue as pr
from version import CPSW_YAML_SCHEMA_VERSION


class YamlConverter:
    """
    Convert a rogue Python device object into CPSW YAML, and write the YAML into a file.
    """
    def __init__(self, pyrogue_device):
        """
        Initialize the Converter.

        Parameters
        ----------
        pyrogue_device : Device
            The Rogue device object, from which its CPSW YAML representation is to be formed.
        """
        self._pyrogue_device = pyrogue_device

    @staticmethod
    def ordered_dump(data, stream=None, dumper=yaml.Dumper, **kwds):
        """
        Overriding PyYAML generation to support OrderedDict.

        Reference: https://stackoverflow.com/a/21912744

        Parameters
        ----------
        data : OrderedDict
            The ordered data structure
        stream : stream
            In this context, the file to dump the YAML contents
        dumper : yaml.Dumper
            The YAML dumping object
        kwds : args
            Additional arguments as supported by PyYAML.

        Returns
        -------
        A string containing the entire YAML contents.
        """
        class OrderedDumper(dumper):
            pass

        def _dict_representer(dumper, data):
            return dumper.represent_mapping(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                data.items())

        OrderedDumper.add_representer(OrderedDict, _dict_representer)
        return yaml.dump(data, stream, OrderedDumper, **kwds)

    def convert(self, export_filename):
        """
        Perform the conversion, i.e. dumping the Rogue device object's data into a YAML-formatted file.

        The output file will be saved into the output/ directory, which is under the working directory.

        Parameters
        ----------
        export_filename : str
            The name of the output file
        """
        serialized_data = self._serialize_rogue_data()
        self._export_to_yaml(serialized_data, export_filename)

    def _export_to_yaml(self, serialized_data, filename):
        """
        Post-process the YAML contents before writing into the final output file.

        This is accomplished by first writing into a temporary file, then read the temporary file and process certain
        lines, i.e. adding headers, then write to the official output line. Finally, automatically delete the temporary
        line.

        Parameters
        ----------
        serialized_data : OrderedDict
            The Rogue object's data after being serialized.

        filename : str
            The user-provided output data file name.
        """
        with open(os.path.join("output", '.'.join([filename, "tmp"])), 'w') as temp_yaml_file:
            contents = YamlConverter.ordered_dump(serialized_data, dumper=yaml.SafeDumper, default_flow_style=False)
            contents = contents.replace("__root__:\n", "")
            temp_yaml_file.write(contents)

        with open(os.path.join("output", filename), 'w') as yaml_file:
            self._insert_heading(yaml_file, filename)

            with open(os.path.join("output", '.'.join([filename, "tmp"])), 'r') as temp_yaml_file:
                lines = temp_yaml_file.readlines()
                for line in lines:
                    # Add headers to separate sections in the YAML file
                    if any(keyword in line for keyword in ("children:", "\'#\'", "\'##\'")):
                        space_count = len(line) - len(line.lstrip())
                        if "children:" in line:
                            markings = ''.join([' ' * space_count, '#' * 10, '\n'])
                            line = markings + line + markings
                        elif "\'#\'" in line:
                            line = ''.join([' ' * space_count, '#' * 80, '\n'])
                        elif "\'##'" in line:
                            space_count -= 2
                            line = ''.join([' ' * space_count, '#' * 80, '\n'])
                    elif "\'" in line:
                        # Remove single quotes surrounding strings as they're not in the CPSW YAML specs
                        line = line.replace("\'", '')
                    yaml_file.write(line)

        os.remove(os.path.join("output", '.'.join([filename, "tmp"])))

    def _serialize_rogue_data(self):
        """
        Serialize the Rogue device object.

        Returns
        -------
        A nested OrderedDict containing the data required for CPSW YAML.
        """
        # Default values as required by the CPSW YAML specs
        MMIO_DEVICE_CLASS = "MMIODev"
        CONFIG_PRIO_VALUE = 1
        ROOT_DEVICE_SIZE = 0x8
        CHILD_DEVICE_CLASS = "IntField"
        CHILD_DEVICE_BYTE_ORDER = "BE"

        serialized_data = OrderedDict()

        name = self._pyrogue_device.name
        serialized_data[name] = ''.join(['&', name])
        serialized_data["__root__"] = OrderedDict()
        serialized_data["__root__"]["description"] = self._pyrogue_device.description
        serialized_data["__root__"]["configPrio"] = CONFIG_PRIO_VALUE
        serialized_data["__root__"]["class"] = MMIO_DEVICE_CLASS
        serialized_data["__root__"]["size"] = ROOT_DEVICE_SIZE
        serialized_data["__root__"]["children"] = dict()

        remote_variables = self._pyrogue_device.getNodes(pr.RemoteVariable)
        for _, remote_var in remote_variables.items():
            child_data = OrderedDict()
            child_data['#'] = '#' * 20
            child_data[remote_var.name] = OrderedDict()

            child_data[remote_var.name]["at"] = OrderedDict()
            child_data[remote_var.name]["at"]["offset"] = hex(remote_var.offset)
            child_data[remote_var.name]["at"]["byteOrder"] = CHILD_DEVICE_BYTE_ORDER

            child_data[remote_var.name]["description"] = remote_var.description
            child_data[remote_var.name]["class"] = CHILD_DEVICE_CLASS
            child_data[remote_var.name]["sizeBits"] = remote_var.varBytes * 8
            child_data[remote_var.name]["mode"] = remote_var.mode
            child_data[remote_var.name]['##'] = '#' * 20

            serialized_data["__root__"]["children"].update(child_data)

        return serialized_data

    def _insert_heading(self, yaml_file, filename):
        yaml_file.write("##############################################################################\n")
        yaml_file.write("## This file is part of 'SLAC Firmware Standard Library'.\n")
        yaml_file.write("## It is subject to the license terms in the LICENSE.txt file found in the \n")
        yaml_file.write("## top-level directory of this distribution and at: \n")
        yaml_file.write("##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. \n")
        yaml_file.write("## No part of 'SLAC Firmware Standard Library', including this file, \n")
        yaml_file.write("## may be copied, modified, propagated, or distributed except according to \n")
        yaml_file.write("## the terms contained in the LICENSE.txt file. \n")
        yaml_file.write("############################################################################## \n")
        yaml_file.write(' '.join(["#schemaversion", CPSW_YAML_SCHEMA_VERSION, '\n']))
        yaml_file.write(' '.join(["#once", filename, '\n\n\n']))
