# Convert a PyRogue class to YAML

import sys
import os
import shutil
import json
from collections import OrderedDict

from pydoc import locate, ErrorDuringImport
from arg_parser import ArgParser

from version import VERSION, CPSW_YAML_SCHEMA_VERSION

from converter_logging import logging
logger = logging.getLogger(__name__)

from setup_paths import setup_paths
setup_paths()

from yaml_converter import YamlConverter


def parse_arguments():
    parser = ArgParser(description="Convert a PyRogue class definition file to a CSPW YAML file.")
    parser.add_argument("rogue_collection_dir", help="The name of the Python Rogue directory.")
    parser.add_argument("rogue_python_file_dir", help="The directory that contains the Python Rogue file to convert to "
                                                      "CPSW YAML.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--version", action="version", version=VERSION)
    group.add_argument("--cpsw-schema-version", action="version", version=CPSW_YAML_SCHEMA_VERSION)

    args = parser.parse_args()
    return args


def main():
    logger.info("Starting a new conversion session...\n")
    logger.info(''.join(['-' * 80, '\n']))

    args = parse_arguments()

    rogue_dir = vars(args)["rogue_collection_dir"]
    sys.path.insert(1, os.path.expandvars(os.path.expanduser(rogue_dir)))

    rogue_python_file_dir = vars(args)["rogue_python_file_dir"]
    sys.path.insert(1, os.path.expandvars(os.path.expanduser(rogue_python_file_dir)))

    success_files = []
    with open (os.path.join("settings", "exclusions.json"), 'r') as exclusion_file:
        failure_files = json.load(exclusion_file)

    exclusion_list = []
    for k, _ in failure_files.items():
        exclusion_list.append(k)

    for root, directories, filenames in os.walk(os.path.expanduser(rogue_python_file_dir)):
        for filename in filenames:
            if filename[-3:] == ".py" and filename[:-3] not in exclusion_list:
                shutil.copyfile(os.path.join(root, filename), os.path.join("input", filename))

    for _, _, filenames in os.walk("input"):
        for filename in filenames:
            logger.info("Converting file '{0}'...".format(filename))
            filename = filename[:-3]
            class_name = filename

            if class_name[0] == '_':
                class_name = class_name[1:]

            class_rep = None
            trial_count = 0

            original_class_name = class_name
            output = _generate_class_name_variations(original_class_name)

            while not class_rep and trial_count < 2 ** len(class_name):
                class_name = next(output)
                logger.debug("Trying class name variation '{0}'...".format(class_name))

                class_rep = locate('.'.join(["input", filename, class_name]))
                if not class_rep:
                    trial_count += 1
            try:
                pyrogue_device = class_rep()

                converter = YamlConverter(pyrogue_device)
                converter.convert('.'.join([filename, "yaml"]))
                success_files.append(filename)
            except (TypeError, AttributeError, SyntaxError, NameError, ErrorDuringImport) as error:
                failure_files[filename] = '. '.join(["Make sure the file name and the class name are the same",
                                                     str(type(error)), str(error)])
                logger.error("Cannot instantiate the object of type '{0}'. Make sure the file name and the class name ."
                             "are the same (case-sensitive). Exception Type: {1}. Exception: {2}"
                             .format(filename, type(error), error))
            except Exception as e:
                logger.error("Unexpected exception during the conversion of file '{0}'. Exception type: {1}. "
                             "Exception: {2}".format(filename, type(e), e))

    success_count = len(success_files)
    failure_count = len(failure_files)

    logger.info(''.join(['\n', "-" * 80, '\n']))
    logger.info("Number of files successfully converted: {0}".format(success_count))
    logger.info("Number of files unsuccessfully converted: {0}".format(failure_count))

    if success_count:
        logger.info(''.join(['\n', "-" * 80]))
        logger.info("\nSuccessfully converted files:\n ")
        for f in success_files:
            logger.info(f)
    if failure_count:
        logger.info(''.join(['\n', "-" * 80]))
        logger.info("\nUnsuccessfully converted files:\n ")
        for k, v in failure_files.items():
            logger.info(''.join([k, ' ' * (30 - len(k)), '=>', ' ' * 5, v]))
    logger.info(''.join(['\n', "#" * 80, '\n']))


def _generate_class_name_variations(class_name):
    """
    Attempt to guess the class name by varying the capitalization of character combos in the class name string.

    Parameters
    ----------
    class_name : str
        The name of a Python Rogue class

    Yields : str
    -------
        The next name with the next capitalization variation
    """
    if class_name is not None:
        class_name_length = len(class_name)
        for value in range(0, 2 ** class_name_length):
            bit_pattern = [value >> i & 1 for i in range(class_name_length - 1, -1, -1)]
            set_bit_indices = []
            for i in range(0, len(bit_pattern)):
                if bit_pattern[i]:
                    set_bit_indices.append(i)
            processed_name = class_name
            for set_bit_index in set_bit_indices:
                processed_name = ''.join([processed_name[:set_bit_index], processed_name[set_bit_index].upper(),
                                          processed_name[set_bit_index + 1:]])
            yield processed_name


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logger.error("Unexpected exception during the conversion process. Exception type: {0}. Exception: {1}"
                     .format(type(error), error))
