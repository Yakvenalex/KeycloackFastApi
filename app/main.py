from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.api.router import router as api_router
from app.dependensies.auth_dep import keycloak_client
from app.pages.router import router as pages_router

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте приложения
    app.include_router(pages_router)
    app.include_router(api_router)
    yield
    # При остановке приложения
    await keycloak_client.close()


app = FastAPI(lifespan=lifespan)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
