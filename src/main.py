from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict
import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware import Middleware

from src.logging import info
from src.db.migration import upgrade_db
from src.auth import ApikeyMiddleware


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncGenerator[None, None]:
    info("Upgrading DB")

    await upgrade_db()

    yield


app = FastAPI(
    lifespan=lifespan,
    title="Kinetix",
    version="0.1.0",
    description="Kinetix's targets service API",
    docs_url=None,
    middleware=[Middleware(ApikeyMiddleware)],
)


origins_regex = re.compile(
    (
        r"https?:\/\/"  # http:// or https://
        r"(localhost(:[0-9]*)?|"  # localhost, localhost:$PORT or ...
        r"[\w\.-]*(megaredhand|fedecolangelo)\.cloud\.okteto\.net)"  # okteto
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origins_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------
# Subrouting
# ----------


def add_subrouters(app: FastAPI) -> None:
    """Set up subrouters"""
    from src.api.targets import router as targets_router
    from src.api.reports import router as reports_router

    app.include_router(targets_router)
    app.include_router(reports_router)


add_subrouters(app)


# -----------------
# Utility endpoints
# -----------------


@app.get("/health", include_in_schema=False)
def health_check() -> Dict[str, str]:
    """Check if server is responsive"""
    return {"status": "Alive and kicking!"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse("favicon.ico")


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title,
        swagger_favicon_url="favicon.ico",
    )
