from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.dependensies.auth_dep import get_current_user_from_cookie_optional

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def index(
    request: Request, user: dict = Depends(get_current_user_from_cookie_optional)
):
    if user is None:
        return templates.TemplateResponse("index.html", {"request": request})
    return RedirectResponse(url="/protected")


@router.get("/protected", response_class=HTMLResponse)
async def protected_page(
    request: Request, user: dict = Depends(get_current_user_from_cookie_optional)
):
    if user is None:
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        "protected.html", {"request": request, "user": user}
    )
