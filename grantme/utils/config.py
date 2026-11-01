import configparser
from pathlib import Path


DEFAULT_SECTION = "default"
DEFAULT_DATA_DIR = "/scratch/grantme"


def read_data_dir(conf_file: Path, hostname: str) -> Path:
    """
    Read `data_dir` from the section named after `hostname`, falling back to the
    `default` section and then to DEFAULT_DATA_DIR. A missing file is fine.
    """
    parser = configparser.ConfigParser()
    parser.read(str(conf_file))
    for section in (hostname, DEFAULT_SECTION):
        if parser.has_option(section, "data_dir"):
            return Path(parser.get(section, "data_dir"))
    return Path(DEFAULT_DATA_DIR)
