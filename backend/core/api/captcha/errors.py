from __future__ import annotations
class CaptchaError(Exception):
    pass


class CaptchaLoadError(CaptchaError):
    pass


class CaptchaVerifyError(CaptchaError):
    pass
