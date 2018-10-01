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
    # Default values as required by the CPSW YAML specs
    MMIO_DEVICE_CLASS = "MMIODev"
    CONFIG_PRIO_VALUE = 1
    ROOT_DEVICE_SIZE = 8
    SEQUENCE_COMMAND_OFFSET = 0
    CHILD_DEVICE_CLASS = "IntField"
    SEQUENCE_COMMAND_CLASS = "SequenceCommand"
    CHILD_DEVICE_BYTE_ORDER = "BE"

    def __init__(self, pyrogue_device):
        """
        Initialize the Converter.

        Parameters
        ----------
        pyrogue_device : Device
            The Rogue device object, from which its CPSW YAML representation is to be formed.
        """
        self._pyrogue_device = pyrogue_device
        self._serialized_data = OrderedDict()

    def convert(self, export_filename, export_dirname="output"):
        """
        Perform the conversion, i.e. dumping the Rogue device object's data into a YAML-formatted file.

        The output file will be saved into the output/ directory, which is under the working directory.

        Parameters
        ----------
        export_filename : str
            The name of the output file
        export_dirname : str
            The name of the output directory
        """
        self._serialize_rogue_data()
        self._export_to_yaml(export_filename, export_dirname)

    def _serialize_rogue_data(self):
        """
        Serialize the Rogue device object.
        """
        self._serialized_data = OrderedDict()

        if hasattr(self._pyrogue_device, "name"):
            name = self._pyrogue_device.name
            self._serialized_data[name] = ''.join(['&', name])

        self._serialized_data["__root__"] = OrderedDict()

        if hasattr(self._pyrogue_device, "description"):
            self._serialized_data["__root__"]["description"] = self._pyrogue_device.description

        self._serialized_data["__root__"]["configPrio"] = YamlConverter.CONFIG_PRIO_VALUE
        self._serialized_data["__root__"]["class"] = YamlConverter.MMIO_DEVICE_CLASS
        self._serialized_data["__root__"]["size"] = hex(YamlConverter.ROOT_DEVICE_SIZE)

        replica_count = 0
        if hasattr(self._pyrogue_device, "_numBuffers"):
            replica_count = self._pyrogue_device._numBuffers

        if replica_count:
            self._serialized_data["__root__"]["metadata"] = OrderedDict()
            self._serialized_data["__root__"]["metadata"]["numBuffers"] = ' '.join(['&numBuffers', str(replica_count)])

        self._serialized_data["__root__"]["children"] = OrderedDict()
        self._serialize_children(self._pyrogue_device, replica_count)

    def _serialize_children(self, device, replica_count):
        """
        Serialize the Rogue device's children, i.e. remote variables and commands. Potentially recursive (if needed)
        if a remote variable can contain children.

        Parameters
        ----------
        device : pr.Device
            A Rogue device whose children are to be serialized

        """
        # Serialize Remote Variables
        if hasattr(device, "getNodes"):
            remote_variables = device.getNodes(pr.RemoteVariable)
            self._serialize_remote_variables(remote_variables, replica_count)

        # Serialize devices
        if hasattr(device, "devices"):
            devices = device.devices
            self._serialize_devices(devices)

        # Serialize Commands
        if hasattr(device, "commands"):
            commands = device.commands
            self._serialize_commands(commands)

    def _serialize_remote_variables(self, remote_variables, replica_count):
        """
        Serialize just the remote variables.

        Parameters
        ----------
        remote_variables : OrderedDict
            An ordered dictionary of remote variables for a Rogue device.
        """
        if remote_variables and len(remote_variables):
            for key, remote_var in remote_variables.items():
                remote_var_name = remote_var.name
                search_index = remote_var_name.find('[')
                if search_index >= 0:
                    remote_var_name = remote_var_name[0:search_index]
                    if key[search_index:search_index + 3] != "[0]" and not replica_count:
                        current_node_count = child_data[remote_var_name].get("nelms", None)
                        if current_node_count is None:
                            self._serialized_data["__root__"]["children"][remote_var_name]["at"]["nelms"] = 2
                        else:
                            self._serialized_data["__root__"]["children"][remote_var_name]["at"]["nelms"] = \
                                current_node_count + 1
                        continue

                child_data = OrderedDict()
                child_data['#'] = '#' * 20
                child_data[remote_var_name] = OrderedDict()

                child_data[remote_var_name]["at"] = OrderedDict()
                child_data[remote_var_name]["at"]["offset"] = hex(remote_var.offset)
                if replica_count:
                    child_data[remote_var_name]["at"]["nelms"] = "*numBuffers"
                child_data[remote_var_name]["at"]["byteOrder"] = YamlConverter.CHILD_DEVICE_BYTE_ORDER

                child_data[remote_var_name]["description"] = remote_var.description
                child_data[remote_var_name]["class"] = YamlConverter.CHILD_DEVICE_CLASS
                child_data[remote_var_name]["sizeBits"] = remote_var.varBytes * 8

                # Must adjust so that the value falls within the CPSW range -- [0..7]
                ls_bit = remote_var.bitOffset[-1] if remote_var.bitOffset[-1] < 8 else remote_var.bitOffset[-1] % 8
                if ls_bit:
                    # Since the default value is 0, only output if the ls_bit value is larger than 0
                    child_data[remote_var_name]["lsBit"] = ls_bit

                child_data[remote_var_name]["mode"] = remote_var.mode
                child_data[remote_var_name]['##'] = '#' * 20

                self._serialized_data["__root__"]["children"].update(child_data)

    def _serialize_devices(self, devices):
        """
        Serialize the child devices.

        Parameters
        ----------
        devices : OrderedDict
            The child device record.

        """
        if devices and len(devices):
            for key, v in devices.items():
                device_name = key
                search_index = device_name.find('[')
                if search_index >= 0:
                    device_name = device_name[0:search_index]
                    if key[search_index:search_index + 3] != "[0]":
                        # Do not output duplicate remote var names with different subscripts
                        current_node_count = child_data[device_name].get("nelms", None)
                        if current_node_count is None:
                            self._serialized_data["__root__"]["children"][device_name]["at"]["nelms"] = 2
                        else:
                            self._serialized_data["__root__"]["children"][device_name]["at"]["nelms"] = \
                                current_node_count + 1
                        continue

                child_data = OrderedDict()
                child_data['#'] = '#' * 20
                child_data[device_name] = OrderedDict()
                child_data[device_name]["<<"] = ''.join(['*', device_name])
                child_data[device_name]["at"] = OrderedDict()
                if hasattr(devices[key], "offset"):
                    child_data[device_name]["at"]["offset"] = hex(devices[key].offset)
                child_data[device_name]['##'] = '#' * 20

                self._serialized_data["__root__"]["children"].update(child_data)

    def _serialize_commands(self, commands):
        """
        Serialize just the commands.

        Parameters
        ----------
        commands : OrderedDict
            An ordered dictionary of commands for a Rogue device.
        """
        if commands and len(commands):
            for _, command in commands.items():
                command_name = command.name

                child_data = OrderedDict()
                child_data['#'] = '#' * 20
                child_data[command_name] = OrderedDict()
                child_data[command_name]["at"] = OrderedDict()
                child_data[command_name]["at"]["offset"] = hex(command.offset) if hasattr(command, "offset") else \
                    hex(YamlConverter.SEQUENCE_COMMAND_OFFSET)

                child_data[command_name]["name"] = command_name
                child_data[command_name]["description"] = command.description
                child_data[command_name]["class"] = YamlConverter.SEQUENCE_COMMAND_CLASS
                child_data[command_name]['##'] = '#' * 20

                self._serialized_data["__root__"]["children"].update(child_data)

    def _export_to_yaml(self, filename, dirname="output"):
        """
        Post-process the YAML contents before writing into the final output file.

        This is accomplished by first writing into a temporary file, then read the temporary file and process certain
        lines, i.e. adding headers, then write to the official output line. Finally, automatically delete the temporary
        line.

        Parameters
        ----------
        filename : str
            The user-provided output data file name.
        dirname : str
            The name of the output directory
        """
        with open(os.path.join(dirname, '.'.join([filename, "tmp"])), 'w') as temp_yaml_file:
            contents = YamlConverter.ordered_dump(self._serialized_data, dumper=yaml.SafeDumper,
                                                  default_flow_style=False)
            contents = contents.replace("__root__:\n", "")
            temp_yaml_file.write(contents)
        with open(os.path.join(dirname, filename), 'w') as yaml_file:
            YamlConverter._insert_heading(yaml_file, filename)
            with open(os.path.join(dirname, '.'.join([filename, "tmp"])), 'r') as temp_yaml_file:
                lines = temp_yaml_file.readlines()
                for line in lines:
                    line = YamlConverter._post_process_line(line)
                    yaml_file.write(line)

        os.remove(os.path.join(dirname, '.'.join([filename, "tmp"])))

    @staticmethod
    def _post_process_line(line):
        """
        Decorate an output line.

        Parameters
        ----------
        line : str
            An output line to be decorated.

        Returns : str
        -------
            The decorated output line
        """
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
        return line

    @staticmethod
    def _insert_heading(yaml_file, filename):
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

        Returns : str
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
