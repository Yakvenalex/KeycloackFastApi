from fastapi import HTTPException, Request

from app.dependensies.keycloak_client import KeycloakClient

keycloak_client = KeycloakClient()


async def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await keycloak_client.get_user_info(token)


async def get_current_user_from_cookie_optional(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    return await keycloak_client.get_user_info_optional(token)
