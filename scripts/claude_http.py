"""Anthropic API를 표준 라이브러리(urllib)로 부르는 작은 도구. 외부 패키지 없음(저장소 규칙).

키는 환경 변수 `API`에서만 읽는다. 키를 출력·저장하지 않는다(공개 저장소).
"""
from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.request

BASE = "https://api.anthropic.com"
VERSION = "2026-10-21"
_CA = "/root/.ccr/ca-bundle.crt"


def _ctx():
    return ssl.create_default_context(cafile=_CA) if os.path.exists(_CA) else ssl.create_default_context()


def call(method: str, path: str, body: dict | None = None, raw: bool = False, retries: int = 4, beta: str | None = None):
    headers = {"x-api-key": os.environ["API"], "anthropic-version": VERSION, "content-type": "application/json"}
    if beta:
        headers["anthropic-beta"] = beta
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries + 1):
        req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, context=_ctx(), timeout=600) as r:
                payload = r.read()
                return payload if raw else json.loads(payload)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:2000]
            if e.code in (429, 500, 502, 503, 504, 529) and attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {msg}") from None
        except urllib.error.URLError:
            if attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            raise


# 가격 (달러 / 100만 토큰). claude-opus-5-5 정가. 배치는 절반.
PRICE = {"claude-opus-5-5": {"in": 4.0, "out": 20.0, "cache_read": 0.20, "cache_write_5m": 5.0}}


def cost(usage: dict, model: str = "claude-opus-5-5", batch: bool = False) -> float:
    p = PRICE[model]
    c = (usage.get("input_tokens", 0) * p["in"] + usage.get("output_tokens", 0) * p["out"]
         + usage.get("cache_read_input_tokens", 0) * p["cache_read"]
         + usage.get("cache_creation_input_tokens", 0) * p["cache_write_5m"]) / 1e6
    return c / 2 if batch else c
