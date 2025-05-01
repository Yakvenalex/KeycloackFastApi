from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from loguru import logger

from app.config import settings
from app.dependensies.auth_dep import keycloak_client

router = APIRouter()


@router.get("/login")
async def login():
    return RedirectResponse(
        f"{settings.auth_url}"
        f"?client_id={settings.CLIENT_ID}"
        f"&response_type=code"
        f"&scope=openid"
        f"&redirect_uri={settings.redirect_uri}"
    )


@router.get("/login/callback")
async def login_callback(
    code: str,
):
    try:
        token_data = await keycloak_client.get_tokens(code)
        access_token = token_data.get("access_token")

        response = RedirectResponse(url="/protected")
        response.set_cookie(
            key="access_token",
            value=access_token,  # type: ignore
            httponly=True,
            secure=True,  # Только для HTTPS
            samesite="lax",
        )
        return response
    except Exception as e:
        logger.error(f"Login callback error: {str(e)}")
        raise HTTPException(status_code=400, detail="Authentication failed")


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")

    params = {
        "client_id": settings.CLIENT_ID,
        "post_logout_redirect_uri": settings.BASE_URL,
    }

    keycloak_logout_url = f"{settings.logout_url}?{urlencode(params)}"
    return RedirectResponse(url=keycloak_logout_url)
