import httpx
from fastapi import HTTPException

from app.config import settings


class KeycloakClient:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def get_user_info(self, token: str) -> dict:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(settings.userinfo_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid token")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

    async def get_user_info_optional(self, token: str) -> dict | None:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(settings.userinfo_url, headers=headers)
            if response.status_code != 200:
                return None
            return response.json()
        except Exception as e:
            print(e)
            return None

    async def get_tokens(self, code: str) -> dict:
        try:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.redirect_uri,
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = await self.client.post(
                settings.token_url, data=data, headers=headers
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get tokens")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def close(self):
        await self.client.aclose()
