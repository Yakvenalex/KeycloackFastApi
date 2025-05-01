from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import router as api_router
from app.config import settings
from app.services.keycloak_client import KeycloakClient
from app.pages.router import router as pages_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 👉 Создаем и сохраняем shared httpx клиент
    http_client = httpx.AsyncClient()
    app.state.keycloak_client = KeycloakClient(http_client)

    # 👉 Подключаем роутеры и статику
    app.include_router(pages_router)
    app.include_router(api_router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    yield

    # 👉 Закрываем httpx клиент
    await http_client.aclose()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(
            f"{settings.auth_url}"
            f"?client_id={settings.CLIENT_ID}"
            f"&response_type=code"
            f"&scope=openid"
            f"&redirect_uri={settings.redirect_uri}"
        )
    raise exc


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
