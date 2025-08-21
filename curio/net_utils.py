# curio/net_utils.py
import logging
import requests
from dataclasses import dataclass, field
from typing import Dict, Optional

log = logging.getLogger(__name__)

@dataclass
class HttpConfig:
    """HTTP session configuration for CURIO API calls."""
    timeout_seconds: int = 20
    headers: Dict[str, str] = field(default_factory=lambda: {
        "User-Agent": "curio/1.0 (+https://github.com/curio)"
    })

    @property
    def timeout(self) -> int:
        """Expose timeout under .timeout (compatibility fix)."""
        return self.timeout_seconds


def make_session(cfg: Optional[HttpConfig] = None) -> requests.Session:
    cfg = cfg or HttpConfig()
    sess = requests.Session()
    sess.headers.update(cfg.headers)
    return sess


def _check_response(resp: requests.Response) -> None:
    """Raise for bad HTTP status codes with logging."""
    if not resp.ok:
        log.error("HTTP %s %s -> %s", resp.request.method, resp.url, resp.status_code)
        resp.raise_for_status()


def get_json(url: str,
             params: Optional[dict] = None,
             session: Optional[requests.Session] = None,
             cfg: Optional[HttpConfig] = None,
             method: str = "GET",
             json: Optional[dict] = None) -> dict:
    """Generic JSON fetcher with error handling and timeout support."""
    cfg = cfg or HttpConfig()
    sess = session or make_session(cfg)

    if method.upper() == "POST":
        resp = sess.post(url, json=json, params=params,
                         timeout=cfg.timeout, headers=cfg.headers)
    else:
        resp = sess.get(url, params=params,
                        timeout=cfg.timeout, headers=cfg.headers)

    _check_response(resp)
    try:
        return resp.json()
    except Exception as e:
        log.exception("Failed to parse JSON from %s", url)
        raise e


def get_text(url: str,
             params: Optional[dict] = None,
             session: Optional[requests.Session] = None,
             cfg: Optional[HttpConfig] = None,
             method: str = "GET",
             data: Optional[dict] = None) -> str:
    """Generic text fetcher with error handling."""
    cfg = cfg or HttpConfig()
    sess = session or make_session(cfg)

    if method.upper() == "POST":
        resp = sess.post(url, data=data, params=params,
                         timeout=cfg.timeout, headers=cfg.headers)
    else:
        resp = sess.get(url, params=params,
                        timeout=cfg.timeout, headers=cfg.headers)

    _check_response(resp)
    return resp.text
    
def post_json(url: str,
              json: dict,
              params: Optional[dict] = None,
              session: Optional[requests.Session] = None,
              cfg: Optional[HttpConfig] = None) -> dict:
    """Generic POST JSON helper (for RCSB search GraphQL)."""
    cfg = cfg or HttpConfig()
    sess = session or make_session(cfg)

    resp = sess.post(url, json=json, params=params,
                     timeout=cfg.timeout, headers=cfg.headers)

    _check_response(resp)
    try:
        return resp.json()
    except Exception as e:
        log.exception("Failed to parse JSON from %s", url)
        raise e
def get_bytes(url: str, session=None, cfg: "HttpConfig" = None) -> bytes:
    """Download binary data (e.g. PNG) with optional session and HttpConfig."""
    cfg = cfg or HttpConfig()
    session = session or make_session(cfg)
    r = session.get(url, timeout=cfg.timeout_seconds)
    r.raise_for_status()
    return r.content
