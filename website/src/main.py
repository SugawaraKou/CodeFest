# -*- coding:utf-8 -*-

import warnings
import logging
from datetime import datetime
from pytz import timezone
import traceback
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import sys

import config



warnings.filterwarnings('ignore', category=FutureWarning)
logging.getLogger('httpx').setLevel(logging.WARNING)
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.disabled = config.UvicornLogsOff


class CustomLogFormatter(logging.Formatter):
    def __init__(self, service_name="СЕРВИС"):
        super().__init__()
        self.service_name = service_name

    def format(self, record):
        timestamp = datetime.now(timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")
        if record.levelname == "ERROR":
            event_type = "(ОШИБКА)"
            source = "STDERR"
        elif "GET" in record.getMessage() or "POST" in record.getMessage():
            event_type = "(ЗАПРОС)"
            source = record.name.upper()
        else:
            event_type = "(СОБЫТИЕ)"
            source = record.name.upper()
        formatted_message = f"{self.service_name} {timestamp} [{source}] {event_type} | {record.getMessage()}"
        return formatted_message


# перенаправление предупреждений в логгер
def log_warning(message, category, filename, lineno, file=None, line=None):
    logger = logging.getLogger("custom.warning")
    logger.warning(f"{filename}:{lineno}: {category.__name__}: {message}")


warnings.showwarning = log_warning  # перехват всех предупреждений


async def log(message: str, level: str = "info"):
    logger = logging.getLogger("custom.access")
    log_method = getattr(logger, level, logger.info)
    log_method(message)


# Middleware для логирования запросов
class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        log_message = (f"{request.client.host}:{request.client.port} - \"{request.method} {request.url.path} "
                       f"HTTP/{request.scope['http_version']}\" {response.status_code}")
        await log(log_message)
        return response


# Middleware для логирования ошибок
class ErrorLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            error_message = f"Произошла ошибка: {trace}"
            await log(error_message, level="error")
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# Настройка логирования
service_name = "CodeFest"
formatter = CustomLogFormatter(f'[{service_name}]')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

logging.getLogger().handlers.clear()
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

for logger_name in ["custom.access", "custom.error", "custom.stdout", "custom.warning"]:
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


# для логирования print-сообщений
def custom_print(message: str):
    logger = logging.getLogger("custom.stdout")
    logger.info(message)


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=8)
app.add_middleware(AccessLogMiddleware)
app.add_middleware(ErrorLogMiddleware)

app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web")


@app.get("/", response_class=HTMLResponse)
async def render_main(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


async def main():
    uvicorn.run(app='main:app', host=config.UvicornHost, port=config.UvicornPort, reload=config.UvicornReload,
                workers=config.UvicornWorkers)


if __name__ == "__main__":
    asyncio.run(main())