from __future__ import annotations
"""Stub database models for web version (tokens managed by frontend)."""
from typing import Optional


class WavesUser:
    """Stub WavesUser - in web version, tokens come from frontend localStorage."""
    cookie: str = ""
    uid: str = ""
    bat: str = ""
    did: str = ""
    status: str = ""
    is_login: bool = False
    game_id: int = 2
    last_used_time: int = 0

    @staticmethod
    async def select_data_by_cookie_and_uid(cookie="", uid="", game_id=None):
        return None

    @staticmethod
    async def select_data_by_cookie(cookie=""):
        return None

    @staticmethod
    async def select_waves_user(uid="", user_id="", bot_id="", game_id=None):
        return None

    @staticmethod
    async def get_waves_all_user():
        return []

    @staticmethod
    async def cookie_validate(uid=""):
        return False

    @staticmethod
    async def mark_cookie_invalid(uid="", cookie="", status=""):
        pass

    @staticmethod
    async def update_data_by_data(select_data=None, update_data=None):
        pass

    @staticmethod
    async def update_last_used_time(uid="", user_id="", bot_id="", game_id=None):
        pass

    @staticmethod
    async def get_user_by_attr(user_id="", bot_id="", attr="", value="", game_id=None):
        return None


class WavesBind:
    """Stub WavesBind."""

    @staticmethod
    async def insert_waves_uid(user_id="", bot_id="", uid="", group_id="", lenth_limit=9):
        return 0

    @staticmethod
    async def switch_uid_by_game(user_id="", bot_id="", uid=""):
        pass


# Migration commands (empty in web version)
exec_list = []
