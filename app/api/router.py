from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import AddNote, AddNoteWithUserId, AddUser, SUserId
from app.config import settings
from app.dao.dao import NotesDAO, UsersDAO
from app.services.auth_dep import get_current_user, get_keycloak_client
from app.services.dao_dep import (
    get_session_with_commit,
    get_session_without_commit,
)
from app.services.keycloak_client import KeycloakClient

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/login/callback", include_in_schema=False)
async def login_callback(
    code: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    session: AsyncSession = Depends(get_session_with_commit),
    keycloak: KeycloakClient = Depends(get_keycloak_client),
) -> RedirectResponse:
    """
    Обрабатывает callback после авторизации в Keycloak.
    Получает токен, информацию о пользователе, сохраняет пользователя в БД (если нужно)
    и устанавливает cookie с токенами. Обрабатывает ошибки от Keycloak.
    """
    if error:
        logger.error(f"Keycloak error: {error}, description: {error_description}")
        raise HTTPException(status_code=401, detail="Authorization code is required")

    if not code:
        raise HTTPException(status_code=401, detail="Authorization code is required")

    try:
        # Получение токенов от Keycloak
        token_data = await keycloak.get_tokens(code)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        id_token = token_data.get("id_token")

        if not access_token:
            raise HTTPException(status_code=401, detail="Токен доступа не найден")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token не найден")
        if not id_token:
            raise HTTPException(status_code=401, detail="ID token не найден")

        # Получение информации о пользователе
        user_info = await keycloak.get_user_info(access_token)
        user_id = user_info.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="ID пользователя не найден")

        # Проверка существования пользователя, создание нового при необходимости
        users_dao = UsersDAO(session)
        user = await users_dao.find_one_or_none_by_id(user_id)
        if not user and isinstance(user_info, dict):
            user_info["id"] = user_info.pop("sub")
            await users_dao.add(AddUser(**user_info))

        # Установка cookie с токенами и редирект
        response = RedirectResponse(url="/protected")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
            max_age=token_data.get("expires_in", 3600),
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
            max_age=token_data.get("refresh_expires_in", 2592000),
        )
        response.set_cookie(
            key="id_token",
            value=id_token,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
            max_age=token_data.get("expires_in", 3600),
        )
        logger.info(f"User {user_id} logged in successfully")
        return response

    except Exception as e:
        logger.error(f"Ошибка обработки callback'а логина: {str(e)}")
        raise HTTPException(status_code=401, detail="Ошибка авторизации")


@router.get("/logout", include_in_schema=False)
async def logout(request: Request):
    id_token = request.cookies.get("id_token")
    params = {
        "client_id": settings.CLIENT_ID,
        "post_logout_redirect_uri": settings.BASE_URL,
    }
    if id_token:
        params["id_token_hint"] = id_token

    keycloak_logout_url = f"{settings.logout_url}?{urlencode(params)}"
    response = RedirectResponse(url=keycloak_logout_url)
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    response.delete_cookie(
        key="id_token",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    return response


@router.post("/notes")
async def add_note(
    note: AddNote,
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
):
    notes_dao = NotesDAO(session)
    await notes_dao.add(AddNoteWithUserId(user_id=user["sub"], **note.model_dump()))
    return {"status": "ok", "message": "Note added successfully", "note": note}


@router.get("/notes")
async def get_notes(
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_without_commit),
):
    notes_dao = NotesDAO(session)
    notes = await notes_dao.find_all(SUserId(user_id=user["sub"]))
    return {"status": "ok", "notes": notes}


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: str,
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
):
    notes_dao = NotesDAO(session)
    note = await notes_dao.find_one_or_none_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    if note.user_id != user["sub"]:
        raise HTTPException(
            status_code=403, detail="У вас нет прав на удаление этой заметки"
        )
    await session.delete(note)
    return {"status": "ok", "message": "Заметка успешно удалена"}


@router.put("/notes/{note_id}")
async def update_note(
    note_id: int,
    note: AddNote,
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
):
    notes_dao = NotesDAO(session)
    existing_note = await notes_dao.find_one_or_none_by_id(note_id)
    if not existing_note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    if existing_note.user_id != user["sub"]:
        raise HTTPException(
            status_code=403, detail="У вас нет прав на обновление этой заметки"
        )
    existing_note.title = note.title
    existing_note.content = note.content
    return {"status": "ok", "message": "Заметка успешно обновлена", "note": note}
