import os
import logging.config

import yaml


def configure_logging():
    with open(os.environ["LOGGING_CONFIG_PATH"], "r") as fh:
        configs = yaml.safe_load(fh)
    logging.config.dictConfig(configs)


configure_logging()
