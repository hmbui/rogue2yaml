import os
import sys

from converter_logging import logging
logger = logging.getLogger(__name__)


def setup_paths():
    try:
        rogue_2_8_3 = os.environ["ROGUE2YAML_ROGUE_2_8_3"]
    except KeyError as error:
        logger.error("You must set up the appropriate environment variables. Missing env var: {0}".format(error))
        return

    sys.path.insert(1, rogue_2_8_3)

