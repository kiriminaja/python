from __future__ import annotations

from dataclasses import dataclass, field
import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        pass

import httpx


class Env(StrEnum):
    SANDBOX = "sandbox"
    PRODUCTION = "production"


KA_ENV_URL: dict[Env, str] = {
    Env.SANDBOX: "https://tdev.kiriminaja.com",
    Env.PRODUCTION: "https://client.kiriminaja.com",
}


@dataclass(slots=True)
class Config:
    env: Env = Env.SANDBOX
    api_key: str = ""
    base_url: str = ""
    http_client: httpx.Client | None = field(default=None, repr=False)
    async_http_client: httpx.AsyncClient | None = field(default=None, repr=False)

    def resolved_base_url(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")
        return KA_ENV_URL.get(self.env, KA_ENV_URL[Env.SANDBOX]).rstrip("/")
