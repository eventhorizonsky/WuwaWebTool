from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import aiohttp
from core.logger import logger
from pydantic import BaseModel

from .api import NET_SERVER_ID_MAP, SERVER_ID_NET
from .model import (
    AccountBaseInfo,
    BattlePassData,
    Box,
    EnergyData,
    GachaLog,
    LivenessData,
)
from .request_util import KuroApiResp

# ===== 端点 =====================================================
SDK_BASE_URL = "https://sdkapi.kurogame-service.com/sdkcom/v2"
SDK_LOGIN_EMAIL_URL = f"{SDK_BASE_URL}/login/emailPwd.lg"
SDK_LOGIN_AUTO_URL = f"{SDK_BASE_URL}/login/auto.lg"
SDK_AUTH_TOKEN_URL = f"{SDK_BASE_URL}/auth/getToken.lg"
SDK_OAUTH_CODE_URL = f"{SDK_BASE_URL}/user/oauth/code/generate.lg"

LAUNCHER_BASE_URL = "https://pc-launcher-sdk-api.kurogame.net/game"
LAUNCHER_PLAYER_INFO_URL = f"{LAUNCHER_BASE_URL}/queryPlayerInfo"
LAUNCHER_ROLE_INFO_URL = f"{LAUNCHER_BASE_URL}/queryRole"

SDK_GACHA_LOG_URL = "https://gmserver-api.aki-game2.net/gacha/record/query"

# ===== 内部凭据 =================================================
_KR_CLIENT_ID = "7rxmydkibzzsf12om5asjnoo"
_KR_PRODUCT_KEY = "5c063821193f41e09f1c4fdd7567dda3"
_KR_APP_KEY = "32gh5r0p35ullmxrzzwk40ly"
_KR_PROJECT_ID = "G153"
_KR_PRODUCT_LOGIN = "A1730"  # 登录态使用
_KR_PRODUCT_TOKEN = "A1725"  # token / oauth 使用
_KR_SDK_VERSION = "2.6.1"

# 签名后置位互换
_SIGN_SWAPS = ((1, 13), (5, 17), (7, 23))

_DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=10)


# ===== 加密 / 签名 ==============================================
def _gen_device_no() -> str:
    """生成大写 UUID4 设备号。"""
    return str(uuid.uuid4()).upper()


def _md5_hex(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _sign_payload(payload: Dict[str, Any]) -> str:
    """计算请求签名。

    流程：剔除 ``sign`` / ``market`` 与空值字段后，按 key 字典序拼接
    ``key=value&`` 并追加 app_key 取 32 位 MD5（小写），再交换若干位置上的字符。
    """
    skip = {"sign", "market"}
    pairs = "".join(
        f"{k}={payload[k]}&"
        for k in sorted(payload)
        if k not in skip and payload[k] is not None
    )
    digest = _md5_hex(pairs + _KR_APP_KEY).lower()
    buf = bytearray(digest.encode("ascii"))
    for i, j in _SIGN_SWAPS:
        buf[i], buf[j] = buf[j], buf[i]
    return buf.decode("ascii")


def _scramble_password(password: str) -> str:
    """混淆登录密码：base64 后做两轮 4 步长邻位互换。"""
    if not password:
        return ""

    chars = list(base64.b64encode(password.encode("utf-8")).decode("ascii"))
    n = len(chars)
    for offset in (0, 1):
        i = offset
        while i + 2 < n:
            chars[i], chars[i + 2] = chars[i + 2], chars[i]
            if i + 6 >= n:
                break
            i += 4
    return "".join(chars)


# ===== 工具 =====================================================
def _resolve_server_id(role_id: Union[int, str], server_id: Optional[str] = None) -> str:
    if server_id:
        return server_id
    try:
        prefix = int(role_id) // 100000000
    except (TypeError, ValueError):
        return SERVER_ID_NET
    return NET_SERVER_ID_MAP.get(prefix, SERVER_ID_NET)


def _to_ts(value: Any) -> Optional[int]:
    """ISO 字符串 / 数字时间转秒级 unix 时间戳。

    国际服 API 返回的是 ISO 字符串（参见 kuro_py 的 EnergyRecoverTime / CreatTime
    字段），下游 ``datetime.fromtimestamp`` 期望秒。对数值型输入做毫秒→秒的兜底
    （>1e12 视为毫秒）。
    """
    if value in (None, ""):
        return None
    try:
        if isinstance(value, (int, float)):
            v = int(value)
            return v // 1000 if v > 10**12 else v
        return int(datetime.fromisoformat(str(value)).timestamp())
    except Exception:
        return None


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


_SENSITIVE_KEYS = {
    "password",
    "access_token",
    "auto_token",
    "token",
    "code",
    "client_secret",
    "roleToken",
}


def _mask_sensitive(payload: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """调试日志里给敏感字段打码，便于贴出来不泄密。"""
    if not isinstance(payload, dict):
        return payload
    masked: Dict[str, Any] = {}
    for k, v in payload.items():
        if k in _SENSITIVE_KEYS and isinstance(v, str) and v:
            masked[k] = f"<{v[:4]}…{v[-4:]} len={len(v)}>" if len(v) > 8 else "<…>"
        else:
            masked[k] = v
    return masked


def _normalize_resp(raw: Any) -> Dict[str, Any]:
    """统一外层字段。

    SDK 端点（emailPwd / getToken / auto / heartbeat / oauth code）的响应是扁平的：
    状态码放在 ``codes``，业务字段散落在顶层（其中 ``code`` 是授权码字符串）。
    这里把状态码迁到 ``code``，剩余业务字段打包为 ``data``，让下游统一按
    ``KuroApiResp`` 的 ``{code, msg, data}`` 结构消费。

    launcher 端点（queryPlayerInfo / queryRole）已经是标准结构，仅做 ``message``
    → ``msg`` 的字段名兼容。
    """
    if not isinstance(raw, dict):
        return {"code": -999, "msg": "响应格式异常", "data": None}

    if "codes" in raw:
        flat = dict(raw)
        status = flat.pop("codes")
        msg = flat.pop("msg", flat.pop("message", ""))
        return {"code": status, "msg": msg, "data": flat or None}

    norm = dict(raw)
    if "msg" not in norm and "message" in norm:
        norm["msg"] = norm.pop("message")
    return norm


# ===== 角色面板适配 =============================================
def _adapt_account_base(base: Dict[str, Any]) -> AccountBaseInfo:
    """launcher ``Base`` 段 -> ``AccountBaseInfo``。"""
    boxes = base.get("Boxes")
    box_list: Optional[List[Box]] = None
    if isinstance(boxes, dict) and boxes:
        box_list = [Box(boxName=str(k), num=_safe_int(v)) for k, v in boxes.items()]

    return AccountBaseInfo(
        name=str(base.get("Name", "")),
        id=_safe_int(base.get("Id")),
        creatTime=_to_ts(base.get("CreatTime")),
        activeDays=base.get("ActiveDays"),
        level=base.get("Level"),
        worldLevel=base.get("WorldLevel"),
        roleNum=base.get("RoleNum"),
        boxList=box_list,
        weeklyInstCount=base.get("WeeklyInstCount"),
        storeEnergy=base.get("StoreEnergy"),
        storeEnergyLimit=base.get("MaxStoreEnergy"),
    )


def _adapt_energy(base: Dict[str, Any]) -> EnergyData:
    return EnergyData(
        name="结晶波片",
        img="",
        refreshTimeStamp=_to_ts(base.get("EnergyRecoverTime")) or 0,
        cur=_safe_int(base.get("Energy")),
        total=_safe_int(base.get("MaxEnergy")),
    )


def _adapt_liveness(base: Dict[str, Any]) -> LivenessData:
    return LivenessData(
        name="活跃度",
        img="",
        cur=_safe_int(base.get("Liveness")),
        total=_safe_int(base.get("LivenessMaxCount")),
    )


def _adapt_battle_pass(bp: Dict[str, Any]) -> BattlePassData:
    # 国际服直接读 Level（先约电台等级）；Exp/ExpLimit 是经验值，本插件不使用。
    # 下游仅消费 cur，total 无人引用，置 0 占位。
    return BattlePassData(
        name="电台",
        cur=_safe_int(bp.get("Level")),
        total=0,
    )


# ===== 适配后的精简响应 =========================================
class SdkLoginResult(BaseModel):
    """登录返回"""

    user_id: int
    username: str
    auto_token: str
    code: str
    is_first: bool = False


class SdkAccessToken(BaseModel):
    access_token: str
    expires_in: int


class PlayerPanelData(BaseModel):

    base: AccountBaseInfo
    energy: EnergyData
    liveness: LivenessData
    battlePass: BattlePassData


class LauncherRoleSummary(BaseModel):

    region: str
    role_id: str
    role_name: str
    level: int = 0


# ===== 客户端 ===================================================
class WavesLauncherApi:

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    # ---- session ----
    async def _session_get(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=_DEFAULT_TIMEOUT)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    # ---- 通用请求 ----
    async def _do_request(
        self,
        url: str,
        *,
        method: str = "POST",
        form: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> KuroApiResp[Any]:
        # debug_body: Any = json_body if json_body is not None else _mask_sensitive(form)
        # logger.debug(
            # f"[鸣潮·SDK] >>> {method} {url} body={debug_body} headers={headers} params={params}"
        # )

        try:
            sess = await self._session_get()
            async with sess.request(
                method,
                url,
                data=form,
                json=json_body,
                params=params,
                headers=headers,
            ) as resp:
                # status = resp.status
                try:
                    raw = await resp.json(content_type=None)
                except Exception:
                    raw_text = await resp.text()
                    # logger.debug(f"[鸣潮·SDK] <<< {url} status={status} non-json body={raw_text!r}")
                    raw = {"code": -999, "msg": raw_text}
        except aiohttp.ClientError as e:
            logger.warning(f"[鸣潮·SDK] 请求异常 url={url} err={e}")
            return KuroApiResp.err(f"网络异常: {e}")
        except Exception as e:
            logger.warning(f"[鸣潮·SDK] 未知异常 url={url} err={e}")
            return KuroApiResp.err(f"未知异常: {e}")

        # logger.debug(f"[鸣潮·SDK] <<< {url} status={status} raw={raw}")
        normalized = _normalize_resp(raw)
        # logger.debug(f"[鸣潮·SDK] <<< {url} normalized={normalized}")
        return KuroApiResp[Any].model_validate(normalized)

    async def _retry_launcher(
        self,
        url: str,
        body: Dict[str, Any],
        max_retry: int,
    ) -> KuroApiResp[Any]:
        """launcher 端点 code=1005 retrying 的退避重试。

        服务端用 1005 表示数据正在异步准备，间隔从 0.8s 起递增到 ~3s。
        """
        attempts = max(max_retry, 1)
        delay = 0.5
        resp: Optional[KuroApiResp[Any]] = None
        for i in range(attempts):
            resp = await self._do_request(url, json_body=body)
            # logger.debug(
            #     f"[鸣潮·SDK] launcher retry {i + 1}/{attempts} url={url} "
            #     f"code={resp.code} msg={resp.msg!r} data={resp.data!r}"
            # )
            if resp.code != 1005:
                return resp
            if i + 1 < attempts:
                await asyncio.sleep(delay)
                delay = min(delay * 1.6, 2.0)
        logger.warning(
            f"[鸣潮·SDK] launcher 1005 重试 {attempts} 次仍未就绪 url={url} body={body}"
        )
        assert resp is not None
        return resp

    # ================================================================
    # 1. 认证
    # ================================================================
    async def email_login(
        self,
        email: str,
        password: str,
        *,
        device_no: Optional[str] = None,
        captcha: Optional[Dict[str, str]] = None,
    ) -> KuroApiResp[SdkLoginResult]:
        """邮箱密码登录账号"""
        device_no = device_no or _gen_device_no()
        body: Dict[str, Any] = {
            "__e__": 1,
            "email": email,
            "password": _scramble_password(password),
            "deviceNum": device_no,
            "client_id": _KR_CLIENT_ID,
            "platform": "PC",
            "productId": _KR_PRODUCT_LOGIN,
            "productKey": _KR_PRODUCT_KEY,
            "projectId": _KR_PROJECT_ID,
            "redirect_uri": 1,
            "response_type": "code",
            "sdkVersion": _KR_SDK_VERSION,
            "channelId": "240",
        }
        body["sign"] = _sign_payload(body)
        if captcha:
            body.update(captcha)

        resp = await self._do_request(SDK_LOGIN_EMAIL_URL, form=body)
        return self._wrap_login(resp)

    async def auto_login(
        self,
        auto_token: str,
        *,
        device_no: Optional[str] = None,
    ) -> KuroApiResp[SdkLoginResult]:
        """凭 auto_token 静默续登。"""
        device_no = device_no or _gen_device_no()
        body: Dict[str, Any] = {
            "token": auto_token,
            "client_id": _KR_CLIENT_ID,
            "deviceNum": device_no,
            "sdkVersion": _KR_SDK_VERSION,
            "productId": _KR_PRODUCT_LOGIN,
            "projectId": _KR_PROJECT_ID,
            "redirect_uri": 1,
            "response_type": "code",
            "channelId": "171",
        }
        body["sign"] = _sign_payload(body)
        resp = await self._do_request(SDK_LOGIN_AUTO_URL, form=body)
        return self._wrap_login(resp)

    @staticmethod
    def _wrap_login(resp: KuroApiResp[Any]) -> KuroApiResp[SdkLoginResult]:
        if not resp.success or not isinstance(resp.data, dict):
            return KuroApiResp[SdkLoginResult](
                code=resp.code, msg=resp.msg, data=None
            )
        d = resp.data
        return KuroApiResp[SdkLoginResult].ok(
            SdkLoginResult(
                user_id=_safe_int(d.get("id")),
                username=str(d.get("username", "")),
                auto_token=str(d.get("autoToken") or d.get("auto_token") or ""),
                code=str(d.get("code", "")),
                is_first=bool(d.get("firstLgn", False)),
            )
        )

    async def exchange_access_token(
        self,
        login_code: str,
        *,
        device_no: Optional[str] = None,
    ) -> KuroApiResp[SdkAccessToken]:
        """用登录返回的 code 换取 access_token。"""
        device_no = device_no or _gen_device_no()
        body: Dict[str, Any] = {
            "client_id": _KR_CLIENT_ID,
            "client_secret": _KR_APP_KEY,
            "code": login_code,
            "deviceNum": device_no,
            "grant_type": "authorization_code",
            "productId": _KR_PRODUCT_TOKEN,
            "projectId": _KR_PROJECT_ID,
            "redirect_uri": 1,
        }
        body["sign"] = _sign_payload(body)
        resp = await self._do_request(SDK_AUTH_TOKEN_URL, form=body)
        if not resp.success or not isinstance(resp.data, dict):
            return KuroApiResp[SdkAccessToken](
                code=resp.code, msg=resp.msg, data=None
            )
        d = resp.data
        return KuroApiResp[SdkAccessToken].ok(
            SdkAccessToken(
                access_token=str(d.get("access_token", "")),
                expires_in=_safe_int(d.get("expires_in")),
            )
        )

    async def make_oauth_code(
        self,
        access_token: str,
        *,
        device_no: Optional[str] = None,
        scope: str = "launcher",
    ) -> KuroApiResp[str]:
        """颁发用于 launcher 接口的 OAuth Code。"""
        device_no = device_no or _gen_device_no()
        body: Dict[str, Any] = {
            "access_token": access_token,
            "client_id": _KR_CLIENT_ID,
            "client_secret": _KR_APP_KEY,
            "deviceNum": device_no,
            "productId": _KR_PRODUCT_TOKEN,
            "projectId": _KR_PROJECT_ID,
            "redirect_uri": 1,
            "scope": scope,
        }
        resp = await self._do_request(SDK_OAUTH_CODE_URL, form=body)
        if not resp.success or not isinstance(resp.data, dict):
            return KuroApiResp[str](code=resp.code, msg=resp.msg, data=None)
        return KuroApiResp[str].ok(str(resp.data.get("oauthCode", "")))

    # ================================================================
    # 2. 玩家信息 / 角色面板
    # ================================================================
    async def query_player_brief(
        self,
        oauth_code: str,
        *,
        max_retry: int = 4,
    ) -> KuroApiResp[List[LauncherRoleSummary]]:
        """launcher 接口 queryPlayerInfo：返回该账号下各区服的角色摘要。

        服务端会异步生成数据，未就绪时返回 code=1005 msg=retrying，
        因此对 1005 做带退避的重试，直到拿到真数据或重试上限。
        """
        body = {"oauthCode": oauth_code}
        resp = await self._retry_launcher(LAUNCHER_PLAYER_INFO_URL, body, max_retry)

        if not resp.success or not isinstance(resp.data, dict):
            return KuroApiResp[List[LauncherRoleSummary]](
                code=resp.code, msg=resp.msg, data=None
            )

        roles: List[LauncherRoleSummary] = []
        for region, payload in resp.data.items():
            try:
                info = json.loads(payload) if isinstance(payload, str) else payload
            except Exception:
                continue
            if not isinstance(info, dict):
                continue

            uid = _safe_int(info.get("roleId"))
            if not uid:
                continue
            roles.append(
                LauncherRoleSummary(
                    region=str(region),
                    role_id=str(uid),
                    role_name=str(info.get("roleName", "")),
                    level=_safe_int(info.get("level")),
                )
            )
        return KuroApiResp[List[LauncherRoleSummary]].ok(roles)

    async def query_player_panel(
        self,
        oauth_code: str,
        role_id: Union[int, str],
        region: str,
        *,
        max_retry: int = 4,
    ) -> KuroApiResp[PlayerPanelData]:
        """launcher 接口 queryRole"""
        body: Dict[str, Any] = {
            "oauthCode": oauth_code,
            "playerId": _safe_int(role_id),
            "region": region,
        }
        resp = await self._retry_launcher(LAUNCHER_ROLE_INFO_URL, body, max_retry)

        if not resp.success or not isinstance(resp.data, dict):
            return KuroApiResp[PlayerPanelData](
                code=resp.code, msg=resp.msg, data=None
            )

        raw = resp.data.get(region, "")
        try:
            payload = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            return KuroApiResp[PlayerPanelData].err("角色面板解析失败")

        if not isinstance(payload, dict):
            return KuroApiResp[PlayerPanelData].err("角色面板格式异常")

        base = payload.get("Base") or {}
        bp = payload.get("BattlePass") or {}
        return KuroApiResp[PlayerPanelData].ok(
            PlayerPanelData(
                base=_adapt_account_base(base),
                energy=_adapt_energy(base),
                liveness=_adapt_liveness(base),
                battlePass=_adapt_battle_pass(bp),
            )
        )

    # ================================================================
    # 3. 抽卡
    # ================================================================
    async def get_gacha_log(
        self,
        role_id: Union[int, str],
        record_id: str,
        card_pool_type: Union[str, int],
        *,
        server_id: Optional[str] = None,
        lang: str = "zh-Hans",
    ) -> KuroApiResp[List[GachaLog]]:
        """抽卡记录查询。返回值已映射为 :class:GachaLog 列表。先不启用，暂时统一用导入抽卡连接的接口，主要是我还没抽上"""
        body = {
            "playerId": str(role_id),
            "languageCode": lang,
            "cardPoolType": _safe_int(card_pool_type),
            "recordId": record_id,
            "serverId": _resolve_server_id(role_id, server_id),
            "cardPoolId": "",
        }
        resp = await self._do_request(
            SDK_GACHA_LOG_URL,
            json_body=body,
            headers={"Content-Type": "application/json;charset=UTF-8"},
        )

        if not resp.success or not isinstance(resp.data, list):
            return KuroApiResp[List[GachaLog]](
                code=resp.code, msg=resp.msg, data=None
            )

        items: List[GachaLog] = []
        pool_type = str(card_pool_type)
        for record in resp.data:
            if not isinstance(record, dict):
                continue
            items.append(
                GachaLog(
                    cardPoolType=pool_type,
                    resourceId=_safe_int(record.get("resourceId")),
                    qualityLevel=_safe_int(record.get("qualityLevel")),
                    resourceType=str(record.get("resourceType", "")),
                    name=str(record.get("name", "")),
                    count=_safe_int(record.get("count"), 1),
                    time=str(record.get("time", "")),
                )
            )
        return KuroApiResp[List[GachaLog]].ok(items)


launcher_sdk = WavesLauncherApi()


__all__ = [
    "LauncherRoleSummary",
    "PlayerPanelData",
    "SdkAccessToken",
    "SdkLoginResult",
    "WavesLauncherApi",
    "launcher_sdk",
]
