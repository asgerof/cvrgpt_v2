import structlog
import logging
import sys
import json
import time


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.StreamHandler(sys.stdout)],
        format="%(message)s",
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger("cvrgpt")


logger = logging.getLogger("cvrgpt")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


async def access_log_mw(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    took_ms = int((time.perf_counter() - start) * 1000)
    payload = {
        "event": "http_access",
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "took_ms": took_ms,
        "request_id": getattr(request.state, "request_id", None),
    }
    logger.info(json.dumps(payload))
    return response
