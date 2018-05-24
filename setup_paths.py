import os
import sys


def setup_paths():
    try:
        rogue_2_8_3 = os.environ["ROGUE_2.8.3"]
        rogue_home = os.environ["ROGUE_HOME"]
        rogue_python = os.environ["ROGUE_PYTHON"]
        ac_python = os.environ["AC_PYTHON"]
        cryo_det_common = os.environ["CRYO_DET_COMMON"]
        cryo_det_surf_python = os.environ["CRYO_DET_SURF_PYTHON"]
        cryo_det_dsp_core_lib = os.environ["CRYO_DET_DSP_CORE_LIB"]
    except KeyError as error:
        print("You must set up the appropriate environment variables. Exception: {0}".format(error))

    sys.path.insert(1, cryo_det_dsp_core_lib)
    sys.path.insert(1, cryo_det_surf_python)
    sys.path.insert(1, cryo_det_common)
    sys.path.insert(1, ac_python)
    sys.path.insert(1, rogue_python)
    sys.path.insert(1, rogue_home)
    sys.path.insert(1, rogue_2_8_3)

