import logging
import logging.config
import yaml
from pathlib import Path

def setup_logging(config_path="logging.yaml"):
    Path("logs").mkdir(exist_ok=True)

    if Path(config_path).exists():
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)

