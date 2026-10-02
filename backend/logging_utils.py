import json
import logging
from datetime import datetime, timezone

from flask import g, request

logger = logging.getLogger("tyvon")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def log_event(level, event, **fields):
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "request_id": getattr(g, "request_id", None),
        "method": request.method if request else None,
        "path": request.path if request else None,
        **fields,
    }
    getattr(logger, level, logger.info)(json.dumps(payload, ensure_ascii=False, default=str))
