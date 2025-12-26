from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from app.api import auth, news, comments, users
from app.core.logging import configure_logging
from app.services.metrics import REQUEST_COUNT, REQUEST_LATENCY
import json
from datetime import datetime

logger = configure_logging()

app = FastAPI(title="News API")

app.include_router(auth.router)
app.include_router(news.router)
app.include_router(comments.router)
app.include_router(users.router)


def write_metrics_log(payload: dict) -> None:
    with open("metrics.jsonl", "a", encoding="utf-8") as file:
        file.write(json.dumps(payload) + "\n")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    with REQUEST_LATENCY.labels(path=request.url.path).time():
        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001
            logger.error("request_error", path=request.url.path, error=str(exc))
            raise
    REQUEST_COUNT.labels(method=request.method, path=request.url.path, status=response.status_code).inc()
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
    )
    write_metrics_log(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
        }
    )
    return response


@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    logger.error("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal error"})


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
