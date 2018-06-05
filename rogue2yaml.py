# Convert a PyRogue class to YAML

import sys
import os
import shutil
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
    failure_files = OrderedDict()
    failure_files["TopLevel"] = "Default commType == 'pcie-rssi-interleaved', which triggered a connection attempt."
    failure_files["FpgaTopLevel"] = "Default commType == 'pcie-rssi-interleaved', which triggered a connection attempt."
    failure_files["TopLevel"] = "Default commType == 'pcie-rssi-interleaved', which triggered a connection attempt."
    failure_files["_spiCryo"] = "Default commType == 'pcie-rssi-interleaved', which triggered a connection attempt."
    failure_files["_spiMax"] = "Default commType == 'pcie-rssi-interleaved', which triggered a connection attempt."

    for root, directories, filenames in os.walk(os.path.expanduser(rogue_python_file_dir)):
        for filename in filenames:
            if filename[-3:] == ".py" and filename[:-3] not in (
                    "__init__",
                    "TopLevel",
                    "FpgaTopLevel",
                    "_spiCryo",
                    "_spiMax",
            ):
                shutil.copyfile(os.path.join(root, filename), os.path.join("input", filename))

    for _, _, filenames in os.walk("input"):
        for filename in filenames:
            logger.info("Converting file '{0}'...".format(filename))
            filename = filename[:-3]
            class_name = filename

            if class_name[0] == '_':
                class_name = class_name[1:]
            class_rep = locate('.'.join(["input", filename, class_name]))
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


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logger.error("Unexpected exception during the conversion process. Exception type: {0}. Exception: {1}"
                     .format(type(error), error))


