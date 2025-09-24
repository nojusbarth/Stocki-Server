import logging.config
import yaml
from pathlib import Path

def setup_logging(config_path="logging.yaml"):
    Path("logs").mkdir(exist_ok=True)    
    path = Path(config_path)
    if path.exists():
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)
