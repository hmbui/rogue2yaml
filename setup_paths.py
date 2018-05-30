import os
import sys

import logging
logger = logging.getLogger(__name__)


def setup_paths():
    try:
        rogue_2_8_3 = os.environ["ROGUE2YAML_ROGUE_2_8_3"]
        ac_python = os.environ["ROGUE2YAML_AMC_PYTHON"]
        cryo_det_surf_python = os.environ["ROGUE2YAML_CRYO_DET_SURF_PYTHON"]
        cryo_det_dsp_core_lib = os.environ["ROGUE2YAML_CRYO_DET_DSP_CORE_LIB"]
    except KeyError as error:
        logger.error("You must set up the appropriate environment variables. Missing env var: {0}".format(error))
        return

    sys.path.insert(1, cryo_det_dsp_core_lib)
    sys.path.insert(1, cryo_det_surf_python)
    sys.path.insert(1, ac_python)
    sys.path.insert(1, rogue_2_8_3)

