import os
import logging.config
import pathlib

import yaml


def configure_logging():
    # TODO:
    #     TITLE: LOGGING_CONFIG_PATH
    #     AUTHOR: frndlytm
    #     DESCRIPTION:
    #         Right now, assuming this env var is configured is VERY hairy.
    #         It would be better to assume CONFIG_PATH and then get logging
    #         config if it exists.
    #
    if (path := pathlib.Path(os.environ.get("LOGGING_CONFIG_PATH"))).exists():
        configs = yaml.safe_load(path.read_text())
        logging.config.dictConfig(configs)

    else:
        logging.basicConfig()
