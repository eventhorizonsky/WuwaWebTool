from __future__ import annotations
"""Stateless API wrapper for web version - tokens come from frontend, not database."""
from typing import Optional, Dict, Any, Tuple
from .api.requests import WavesApi
from .api.request_util import get_base_header, KuroApiResp

# Re-export the singleton
waves_api = WavesApi()


async def call_api_with_token(
    uid: str,
    token: str,
    did: str = "",
    bat: str = "",
    method: str = "base_info"
) -> KuroApiResp:
    """Make a stateless API call using tokens from the frontend.

    Args:
        uid: Game role ID
        token: JWT cookie from login
        did: Device ID
        bat: BAT access token
        method: Which data to fetch
    """
    # Monkey-patch WavesUser access for this call
    # The WavesApi methods need token/bat/did in headers
    # We can bypass the database by directly calling the low-level _waves_request

    header = await get_base_header()

    # role_list doesn't need uid — it's used to discover the uid itself
    if method == "role_list":
        data = {"gameId": 3}
        header["devCode"] = did
        header["token"] = token  # role_list needs token
        from .api.api import ROLE_LIST_URL
        return await waves_api._waves_request(ROLE_LIST_URL, "POST", header, data=data)

    # All other methods need a valid UID
    if not uid or not str(uid).strip():
        from .api.request_util import RespCode
        return KuroApiResp(code=RespCode.ERROR, msg="游戏角色ID(uid)不能为空")

    # Game data APIs need did + b-at, but NOT token (token causes "参数错误")
    header.update({
        "did": did,
        "b-at": bat,
    })

    if method == "base_info":
        data = {
            "gameId": 3,
            "serverId": waves_api.get_server_id(uid),
            "roleId": uid,
        }
        from .api.api import BASE_DATA_URL
        return await waves_api._waves_request(BASE_DATA_URL, "POST", header, data=data)
    elif method == "role_data":
        data = {
            "gameId": 3,
            "serverId": waves_api.get_server_id(uid),
            "roleId": uid,
        }
        from .api.api import ROLE_DATA_URL
        return await waves_api._waves_request(ROLE_DATA_URL, "POST", header, data=data)
    elif method == "refresh":
        data = {
            "gameId": 3,
            "serverId": waves_api.get_server_id(uid),
            "roleId": uid,
        }
        from .api.api import REFRESH_URL
        return await waves_api._waves_request(REFRESH_URL, "POST", header, data=data)
    elif method == "calabash":
        data = {
            "gameId": 3,
            "serverId": waves_api.get_server_id(uid),
            "roleId": uid,
        }
        from .api.api import CALABASH_DATA_URL
        return await waves_api._waves_request(CALABASH_DATA_URL, "POST", header, data=data)
    elif method == "role_detail":
        # caller must provide char_id in the data
        raise ValueError("Use call_role_detail instead")
    elif method == "daily":
        data = {
            "type": "2",
            "sizeType": "1",
            "gameId": 3,
            "serverId": waves_api.get_server_id(uid),
            "roleId": uid,
        }
        header["token"] = token  # daily_info needs token
        from .api.api import GAME_DATA_URL
        return await waves_api._waves_request(GAME_DATA_URL, "POST", header, data=data)
    else:
        raise ValueError(f"Unknown method: {method}")


async def call_role_detail(uid: str, token: str, char_id: str,
                           did: str = "", bat: str = "") -> KuroApiResp:
    """Fetch role detail for a specific character."""
    header = await get_base_header()
    # role_detail needs did + b-at, NOT token
    header.update({
        "did": did,
        "b-at": bat,
    })

    data = {
        "gameId": 3,
        "serverId": waves_api.get_server_id(uid),
        "roleId": uid,
        "channelId": "19",
        "countryCode": "1",
        "id": char_id,
    }
    from .api.api import ROLE_DETAIL_URL
    return await waves_api._waves_request(ROLE_DETAIL_URL, "POST", header, data=data)


async def call_login(mobile: str, code: str, did: str) -> KuroApiResp:
    """Login with phone + SMS code. Returns token on success."""
    header = await get_base_header()
    data = {
        "mobile": mobile,
        "code": code,
        "devCode": did,
    }
    from .api.api import LOGIN_URL
    return await waves_api._waves_request(LOGIN_URL, "POST", header, data=data)


async def call_refresh_token(uid: str, token: str, did: str) -> Tuple[bool, str]:
    """Refresh BAT token. Returns (success, access_token)."""
    header = await get_base_header()
    header.update({
        "token": token,
        "did": did,
        "b-at": "",
    })

    data = {
        "serverId": waves_api.get_server_id(uid),
        "roleId": uid,
    }
    from .api.api import REQUEST_TOKEN
    raw_data = await waves_api._waves_request(REQUEST_TOKEN, "POST", header, data=data)
    if raw_data.success and isinstance(raw_data.data, dict):
        if accessToken := raw_data.data.get("accessToken", ""):
            return True, accessToken
    return False, ""
