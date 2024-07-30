import sys
from pathlib import Path


def pytest_configure(config):
    project_root = Path(config.rootdir)
    sys.path.insert(0, str(project_root))
