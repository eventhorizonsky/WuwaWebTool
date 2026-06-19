"""Game data API routes."""
import asyncio
from typing import Any, Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.waves_api_wrapper import call_api_with_token, call_role_detail
from core.logger import logger

router = APIRouter()


class UserAuth(BaseModel):
    uid: str
    token: str
    did: str = ""
    bat: str = ""


class RoleDetailBatchRequest(BaseModel):
    uid: str
    token: str
    did: str = ""
    bat: str = ""
    char_ids: List[str]


class RoleListResponse(BaseModel):
    success: bool
    msg: str = ""
    data: Any = None


@router.post("/refresh", response_model=RoleListResponse)
async def refresh_data(auth: UserAuth):
    """Refresh player data on Kuro servers."""
    result = await call_api_with_token(
        auth.uid, auth.token, auth.did, auth.bat, method="refresh"
    )
    raw = result.data
    if isinstance(raw, (dict, list)):
        safe = raw
    elif raw is not None:
        safe = {"raw": str(raw)}
    else:
        safe = None
    return RoleListResponse(
        success=result.success,
        msg=result.msg or "",
        data=safe,
    )


@router.post("/role-list", response_model=RoleListResponse)
async def get_role_list(auth: UserAuth):
    """Get bound game roles for the account."""
    result = await call_api_with_token(
        auth.uid, auth.token, auth.did, auth.bat, method="role_list"
    )
    raw = result.data
    if isinstance(raw, (dict, list)):
        safe = raw
    elif raw is not None:
        safe = {"raw": str(raw)}
    else:
        safe = None
    return RoleListResponse(
        success=result.success,
        msg=result.msg or "",
        data=safe,
    )


@router.post("/base-data", response_model=RoleListResponse)
async def get_base_data(auth: UserAuth):
    """Get all characters summary (level, chain, weapon)."""
    result = await call_api_with_token(
        auth.uid, auth.token, auth.did, auth.bat, method="base_info"
    )
    raw = result.data
    if isinstance(raw, (dict, list)):
        safe = raw
    elif raw is not None:
        safe = {"raw": str(raw)}
    else:
        safe = None
    return RoleListResponse(
        success=result.success,
        msg=result.msg or "",
        data=safe,
    )


@router.post("/role-data", response_model=RoleListResponse)
async def get_role_data(auth: UserAuth):
    """Get detailed character data (echoes, weapons, chains)."""
    result = await call_api_with_token(
        auth.uid, auth.token, auth.did, auth.bat, method="role_data"
    )
    raw = result.data
    if isinstance(raw, (dict, list)):
        safe = raw
    elif raw is not None:
        safe = {"raw": str(raw)}
    else:
        safe = None
    return RoleListResponse(
        success=result.success,
        msg=result.msg or "",
        data=safe,
    )


@router.post("/role-detail/{char_id}", response_model=RoleListResponse)
async def get_role_detail(char_id: str, auth: UserAuth):
    """Get single character full details."""
    result = await call_role_detail(
        auth.uid, auth.token, char_id, auth.did, auth.bat
    )
    raw = result.data
    if isinstance(raw, (dict, list)):
        safe = raw
    elif raw is not None:
        safe = {"raw": str(raw)}
    else:
        safe = None
    return RoleListResponse(
        success=result.success,
        msg=result.msg or "",
        data=safe,
    )


@router.post("/calabash", response_model=RoleListResponse)
async def get_calabash(auth: UserAuth):
    """Get echo data bank info."""
    result = await call_api_with_token(
        auth.uid, auth.token, auth.did, auth.bat, method="calabash"
    )
    raw = result.data
    if isinstance(raw, (dict, list)):
        safe = raw
    elif raw is not None:
        safe = {"raw": str(raw)}
    else:
        safe = None
    return RoleListResponse(
        success=result.success,
        msg=result.msg or "",
        data=safe,
    )


@router.post("/role-detail-batch", response_model=RoleListResponse)
async def get_role_detail_batch(req: RoleDetailBatchRequest):
    """Get full details for multiple characters in one request."""
    async def fetch_one(cid: str):
        try:
            result = await call_role_detail(req.uid, req.token, cid, req.did, req.bat)
            if result.success and result.data:
                return (cid, result.data)
            return (cid, None)
        except Exception as e:
            logger.warning(f"[WuwaWeb] role-detail-batch failed for {cid}: {e}")
            return (cid, None)

    tasks = [fetch_one(cid) for cid in req.char_ids]
    results = await asyncio.gather(*tasks)
    data = {cid: detail for cid, detail in results if detail is not None}

    return RoleListResponse(
        success=len(data) > 0,
        msg=f"Fetched {len(data)}/{len(req.char_ids)} character details",
        data=data,
    )


@router.post("/daily", response_model=RoleListResponse)
async def get_daily(auth: UserAuth):
    """Get daily dashboard data."""
    result = await call_api_with_token(
        auth.uid, auth.token, auth.did, auth.bat, method="daily"
    )
    raw = result.data
    if isinstance(raw, (dict, list)):
        safe = raw
    elif raw is not None:
        safe = {"raw": str(raw)}
    else:
        safe = None
    return RoleListResponse(
        success=result.success,
        msg=result.msg or "",
        data=safe,
    )
