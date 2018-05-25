# Convert a PyRogue class to YAML

import logging
logger = logging.getLogger(__name__)

from pydoc import locate
from arg_parser import ArgParser

from version import VERSION, CPSW_YAML_SCHEMA_VERSION

from setup_paths import setup_paths
setup_paths()

from yaml_converter import YamlConverter


def parse_arguments():
    parser = ArgParser(description="Convert a PyRogue class definition file to a CSPW YAML file.")
    parser.add_argument("class_name", help="The name of the Python class to convert to CSPW YAML.")
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--cpsw-schema-version", action="version", version=CPSW_YAML_SCHEMA_VERSION)

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    class_name = vars(args)["class_name"]
    class_rep = locate('.'.join(["input", class_name, class_name]))

    try:
        pyrogue_device = class_rep()
    except TypeError as error:
        logger.error("Cannot instantiate the object of type '{0}'. Make sure you provide the correct class name and "
                     "the right Rogue Python file in the 'input' directory. Exception: {1}".format(class_name, error))
        return

    converter = YamlConverter(pyrogue_device)
    converter.convert('.'.join([class_name, "yaml"]))


if __name__ == "__main__":
    main()
