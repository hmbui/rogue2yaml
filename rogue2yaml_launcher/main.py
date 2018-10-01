# Convert a PyRogue class to YAML

import sys
import os
import shutil
import json
import traceback

from pydoc import locate, ErrorDuringImport

import rogue2yaml
from rogue2yaml.arg_parser import ArgParser

from version import CPSW_YAML_SCHEMA_VERSION

from rogue2yaml.converter_logging import logging
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting a new conversion session...\n")
    logger.info(''.join(['-' * 80, '\n']))

    # Parsing command arguments
    args = _parse_arguments()

    rogue_dir = vars(args)["rogue_collection_dir"]
    sys.path.insert(1, os.path.expandvars(os.path.expanduser(rogue_dir)))

    rogue_python_file_dir = vars(args)["rogue_python_file_dir"]
    sys.path.insert(1, os.path.expandvars(os.path.expanduser(rogue_python_file_dir)))
    output_file_dir = _process_output_file_dir(vars(args).get("output_file_dir", None))

    # Records to keep track of successfully converted and unsuccessfully converted (and skipped) files
    success_files = []
    with open(os.path.join("settings", "exclusions.json"), 'r') as exclusion_file:
        failure_files = json.load(exclusion_file)

    exclusion_list = []
    for k, _ in failure_files.items():
        exclusion_list.append(k)

    # Copy all the Rogue Python files scattered across the Rogue directories to one single input location
    _collect_rogue_files(rogue_python_file_dir, exclusion_list)

    # Convert the files
    _convert_files(output_file_dir, success_files, failure_files)

    # Conversion summary
    _summarize(success_files, failure_files)


def _parse_arguments():
    """
    Parse the command arguments.

    Returns
    -------
    The command arguments as a dictionary : dict
    """
    parser = ArgParser(description="Convert a PyRogue class definition file to a CSPW YAML file.")
    parser.add_argument("rogue_collection_dir", help="The name of the Python Rogue directory.")
    parser.add_argument("rogue_python_file_dir", help="The directory that contains the Python Rogue file to convert to "
                                                      "CPSW YAML.")
    parser.add_argument("output_file_dir", nargs='?', default="",
                        help="The directory that contains the output CPSW YAML files.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--version", action="version", version=rogue2yaml.__version__)
    group.add_argument("--cpsw-schema-version", action="version", version=CPSW_YAML_SCHEMA_VERSION)

    args = parser.parse_args()
    return args


def _process_output_file_dir(output_file_dir):
    """
    Expand the output directory, or use the default value if the user does not specify the output directory name.

    Parameters
    ----------
    output_file_dir : str
        The name of the directory to output all the CPSW YAML files.

    Returns
    -------
        The processed output directory : str

    """
    if not output_file_dir:
        output_file_dir = "output"
    else:
        output_file_dir = os.path.expandvars(os.path.expanduser(output_file_dir))

    if not os.path.exists(output_file_dir):
        try:
            os.makedirs(output_file_dir)
        except os.error as err:
            # It's OK if the output directory exists. This is to be compatible with Python 2.7
            if err.errno != os.errno.EEXIST:
                raise err
    return output_file_dir


def _collect_rogue_files(rogue_python_file_dir, exclusion_list):
    """
    Collect all the input files to a common location for the batch conversion.

    Parameters
    ----------
    rogue_python_file_dir : str
        The name of the directory containing the files to be converted

    exclusion_list : list
        A list of names of the files to be excluded from being converted
    """
    try:
        os.makedirs("input")
    except os.error as err:
        # It's OK if the "input" directory exists. This is to be compatible with Python 2.7
        if err.errno != os.errno.EEXIST:
            raise err

    for root, directories, filenames in os.walk(os.path.expanduser(rogue_python_file_dir)):
        for filename in filenames:
            if filename[-3:] == ".py" and filename[:-3] not in exclusion_list:
                shutil.copyfile(os.path.join(root, filename), os.path.join("input", filename))


def _convert_files(output_file_dir, success_files, failure_files):
    """
    Convert the Rogue Python files into CPSW YAML files.

    First, check if the YAML file is already available in the output directory. If so, log and skip the file from
    converting it.

    Next, convert the Rogue Python file if its corresponding YAML file is not in the output directory. If the
    conversion fails, retry the conversion by varying capitalization of the filename.

    A successful conversion will add the filename into the success file list. A failed conversion will add to the
    failure file list.

    Parameters
    ----------
    output_file_dir : str
        The directory to output the converted files
    success_files : list
        A name list of files that are successfully converted
    failure_files : list
        A name list of files that are unsuccessfully converted, and files that are skipped from being converted
    """
    from rogue2yaml.yaml_converter import YamlConverter

    for _, _, filenames in os.walk("input"):
        for filename in filenames:
            output_file_found = False

            # Check if the file is already converted. If found, skip that file
            for _, _, output_files in os.walk(output_file_dir):
                output_filename = filename[:-3] + ".yaml"
                if output_filename in output_files:
                    failure_message = "Skipping file '{0}' as its converted file '{1}' is found in the output " \
                                      "directory '{2}'.".format(filename, output_filename, output_file_dir)
                    failure_files[output_filename] = failure_message
                    logger.info(failure_message)
                    output_file_found = True

            if not output_file_found and filename.endswith(".py"):
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
                    # Instantiate the Rogue device
                    pyrogue_device = class_rep()

                    # Instantiate the YAML Converter
                    converter = YamlConverter(pyrogue_device)

                    # Convert to YAML and save to the output file
                    converter.convert('.'.join([filename, "yaml"]), export_dirname=output_file_dir)
                    success_files.append(filename)
                except (TypeError, AttributeError, SyntaxError, NameError, ErrorDuringImport) as error:
                    failure_files[filename] = '. '.join(["Make sure the file name and the class name are the same",
                                                         str(type(error)), str(error)])
                    logger.error("Cannot instantiate the object of type '{0}'. Make sure the file name and the class "
                                 "name are the same (case-sensitive). Exception Type: {1}. Exception: {2}"
                                 .format(filename, type(error), error))
                except Exception as e:
                    logger.error("Unexpected exception during the conversion of file '{0}'. Exception type: {1}. "
                                 "Exception: {2}".format(filename, type(e), e))


def _summarize(success_files, failure_files):
    """
    Log the summary of the conversions.

    Print out the number of files successfully converted, and not. Also print out the names of such files. For failure
    files, print out the reasons why the files could not be converted, and any applicable errors and potential reasons.

    Parameters
    ----------
    success_files : list
        A name list of files that are successfully converted
    failure_files : list
        A name list of files that are unsuccessfully converted, and files that are skipped from being converted
    """
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
        traceback.print_exc()
