"""Authentication API routes."""
from __future__ import annotations
import json
import uuid
import traceback
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Form
from pydantic import BaseModel

from core.waves_api_wrapper import call_login, call_refresh_token
from core.logger import logger

router = APIRouter()


class LoginRequest(BaseModel):
    mobile: str
    code: str
    did: Optional[str] = ""


class LoginResponse(BaseModel):
    success: bool
    msg: str = ""
    token: str = ""
    did: str = ""
    uid: str = ""


class RefreshBatRequest(BaseModel):
    uid: str
    token: str
    did: str


class RefreshBatResponse(BaseModel):
    success: bool
    bat: str = ""


@router.post("/send-code")
async def send_sms_code(request: Request):
    """Proxy SMS code sending to Kuro API."""
    import aiohttp
    from core.api.request_util import get_base_header, get_community_header

    # Parse request body
    content_type = request.headers.get("content-type", "")
    logger.info(f"[send-code] content-type={content_type}")

    if "application/json" in content_type:
        body = await request.json()
        mobile = body.get("mobile", "")
        gee_test_data = body.get("geeTestData", "")
        logger.info(f"[send-code] JSON body: mobile={mobile}, has_geeTest={bool(gee_test_data)}")
    else:
        form = await request.form()
        mobile = form.get("mobile", "")
        gee_test_data = form.get("geeTestData", "")
        logger.info(f"[send-code] Form body: mobile={mobile}, has_geeTest={bool(gee_test_data)}")
        if gee_test_data:
            logger.info(f"[send-code] geeTestData first 100 chars: {str(gee_test_data)[:100]}")

    if not mobile:
        return {"success": False, "msg": "手机号不能为空"}

    # Use community header (source=h5) matching the browser
    header = await get_community_header()
    header["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"

    # Build data - geeTestData should be sent as a JSON string, not nested
    data = {"mobile": mobile}
    if gee_test_data:
        # The geeTestData from browser is already a JSON string
        data["geeTestData"] = str(gee_test_data)

    logger.info(f"[send-code] Requesting Kuro API: url=https://api.kurobbs.com/user/getSmsCodeForH5")
    logger.info(f"[send-code] Headers: {json.dumps({k: v for k, v in header.items() if k != 'devCode'}, ensure_ascii=False)}")
    logger.info(f"[send-code] Data keys: {list(data.keys())}")

    try:
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(connector=connector, trust_env=False) as session:
            async with session.post(
                "https://api.kurobbs.com/user/getSmsCodeForH5",
                headers=header,
                data=data,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                raw_text = await resp.text()
                logger.info(f"[send-code] Kuro response: status={resp.status}, body={raw_text[:500]}")

                try:
                    result = json.loads(raw_text)
                except json.JSONDecodeError:
                    logger.error(f"[send-code] Failed to parse response as JSON")
                    return {"success": False, "msg": "服务器响应异常"}

                code = result.get("code", -1)
                msg = result.get("msg", "")
                logger.info(f"[send-code] Kuro result: code={code}, msg={msg}")

                if code in (0, 200):
                    return {"success": True, "msg": "验证码已发送"}
                return {"success": False, "msg": msg or "发送验证码失败"}
    except Exception as e:
        logger.error(f"[send-code] Exception: {e}\n{traceback.format_exc()}")
        return {"success": False, "msg": "网络异常，请稍后重试"}


@router.post("/verify", response_model=LoginResponse)
async def login_verify(req: LoginRequest):
    """Login with phone + SMS verification code."""
    did = req.did or str(uuid.uuid4()).upper()

    result = await call_login(req.mobile, req.code, did)

    if not result.success:
        msg = result.msg or "登录失败"
        return LoginResponse(success=False, msg=msg)

    if not result.data or not isinstance(result.data, dict):
        return LoginResponse(success=False, msg="登录失败：未注册库街区账号")

    token = result.data.get("token", "")
    if not token:
        return LoginResponse(success=False, msg="登录失败：无效的凭证")

    return LoginResponse(
        success=True,
        msg="登录成功",
        token=token,
        did=did,
    )


@router.post("/refresh-bat", response_model=RefreshBatResponse)
async def refresh_bat(req: RefreshBatRequest):
    """Refresh BAT access token."""
    success, access_token = await call_refresh_token(req.uid, req.token, req.did)
    if success:
        return RefreshBatResponse(success=True, bat=access_token)
    return RefreshBatResponse(success=False)
