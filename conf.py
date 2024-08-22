import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

ENV = os.environ.get("ENV", "dev")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")
