import json
import logging
from typing import Any, Dict, Optional


class StructuredLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _log(self, level: str, message: str, values: Optional[Dict[str, Any]] = None):
        log_data = {"message": message, "values": values or {}}
        self.logger.log(getattr(logging, level), json.dumps(log_data, indent=2, sort_keys=True))

    def debug(self, message: str, values: Optional[Dict[str, Any]] = None):
        self._log("DEBUG", message, values)

    def info(self, message: str, values: Optional[Dict[str, Any]] = None):
        self._log("INFO", message, values)

    def warning(self, message: str, values: Optional[Dict[str, Any]] = None):
        self._log("WARNING", message, values)

    def error(self, message: str, values: Optional[Dict[str, Any]] = None):
        self._log("ERROR", message, values)

    def critical(self, message: str, values: Optional[Dict[str, Any]] = None):
        self._log("CRITICAL", message, values)


logger = StructuredLogger()
