import os
from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Lakehouse paths
DATA_DIR = BASE_DIR / "data"

class Config:
    def __init__(self, data_root: Path = DATA_DIR):
        self.data_root = data_root
        self.raw_dir = self.data_root / "raw"
        self.bronze_dir = self.data_root / "bronze"
        self.silver_dir = self.data_root / "silver"
        self.gold_dir = self.data_root / "gold"
        self.quarantine_dir = self.data_root / "quarantine"

    def ensure_directories(self):
        """Creates the physical directories in the file system if they do not exist."""
        for path in [
            self.raw_dir,
            self.bronze_dir,
            self.silver_dir,
            self.gold_dir,
            self.quarantine_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

# Instantiate a default config
default_config = Config()
