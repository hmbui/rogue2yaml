import argparse
import sys

import logging
logger = logging.getLogger("PyRogueParser")


class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        logger.error("Argument parsing error: {0}".format(message))
        self.print_help()
        sys.exit(2)
