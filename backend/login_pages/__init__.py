"""Login page routes - serves the HTML login templates from the original bot."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

router = APIRouter()

TEMPLATE_DIR = Path(__file__).parent / "templates"
templates = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Phone + SMS code login page (with Geetest CAPTCHA)."""
    return templates.get_template("index.html").render(
        server_url=str(request.base_url).rstrip("/"),
        auth="",
        userId="",
        kuro_url="https://api.kurobbs.com",
    )


@router.get("/login/email", response_class=HTMLResponse)
async def login_email_page(request: Request):
    """Email + password login page (for international servers)."""
    return templates.get_template("index_email.html").render(
        server_url=str(request.base_url).rstrip("/"),
        auth="",
        userId="",
        kuro_url="https://api.kurobbs.com",
    )


@router.get("/login/404", response_class=HTMLResponse)
async def login_404():
    """Login expired / not found page."""
    try:
        return templates.get_template("404.html").render()
    except Exception:
        return HTMLResponse("<h1>404 - 登录会话已过期</h1>", status_code=404)
