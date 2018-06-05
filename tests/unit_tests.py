import pytest

import os
import sys
from pydoc import locate
import difflib

from rogue2yaml import _generate_class_name_variations
from yaml_converter import YamlConverter


@pytest.mark.parametrize("rogue_filename, class_name", [
    ("_AxiVersion", "AxiVersion"),
    ("_AmcCryoDemoCore", "AmcCryoDemoCore"),
])
def test_rogue2yaml_conversion(rogue_filename, class_name):
    rogue_dir = "~/local/dev/rogue"
    sys.path.insert(1, os.path.expandvars(os.path.expanduser(rogue_dir)))

    rogue_python_file_dir = \
        "~/local/dev/rogue/MicrowaveMuxBpEth-0x00000010-20180501114559-mdewart-d81f9f40.python/python"
    sys.path.insert(1, os.path.expandvars(os.path.expanduser(rogue_python_file_dir)))

    class_rep = locate('.'.join(["input", rogue_filename, class_name]))
    pyrogue_device = class_rep()

    converter = YamlConverter(pyrogue_device)
    converter.convert('.'.join([rogue_filename, "yaml"]), os.path.join("tests", "results"))

    with open(os.path.join("output", rogue_filename + ".yaml")) as core_converted_file:
        with open(os.path.join("tests", "results", rogue_filename + ".yaml")) as unit_test_converted_file:
            diffs = difflib.unified_diff(
                core_converted_file.readlines(),
                unit_test_converted_file.readlines(),
                fromfile='core_converted_file',
                tofile='unit_test_converted_file',
            )
            diff_lines = []
            for line in diffs:
                diff_lines.append(line)

            assert len(diff_lines) == 0


@pytest.mark.parametrize("class_name", [
    "",
    "ab",
    "abc",
    "abcd",
    "abcde",
    "ABcDE",
    "ABCDE",
])
def test_generate_class_name_variations(class_name):
    output = _generate_class_name_variations(class_name)
    print('\n')
    try:
        for i in range(0, 2 ** len(class_name)):
            # As long as we can print out all the expected variations, we're OK
            print(next(output))
    except Exception:
        assert False
    assert True
