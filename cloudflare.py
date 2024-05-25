from requests.exceptions import RequestException, Timeout
from typing import Tuple, List, NoReturn
from functools import cache
import requests
import os


CLOUDFLARE_API_KEY=os.getenv('CLOUDFLARE_API_KEY')
CLOUDFLARE_EMAIL=os.getenv('CLOUDFLARE_EMAIL')
CLOUDFLARE_API_URL=os.getenv('CLOUDFLARE_API_URL')
CLOUDFLARE_REDIRECT_URL=os.getenv('CLOUDFLARE_REDIRECT_URL')
CLOUDFLARE_HEADERS={
    "X-Auth-Email": CLOUDFLARE_EMAIL,
    "X-Auth-Key": CLOUDFLARE_API_KEY,
    "Content-Type": "application/json"
}

def assert_env_vars() ->  bool:
    if not all([
        CLOUDFLARE_API_KEY,
        CLOUDFLARE_EMAIL,
        CLOUDFLARE_API_URL,
        CLOUDFLARE_REDIRECT_URL
    ]):
        raise RuntimeError("Missing Cloudflare environment variables.")

def _send_cloudflare_request(
        endpoint: str, method='get', headers : dict = None, 
        data : dict = None, retries: int = 0, **kwargs
    ) -> requests.Response | NoReturn:
    url = f"{CLOUDFLARE_API_URL}/{endpoint}"
    try:
        if not data:
            data = {}
        if not headers:
            headers = CLOUDFLARE_HEADERS or {}
        response = getattr(requests, method)(url, headers=headers, json=data, **kwargs)
        print(response.json())
        response.raise_for_status()
        return response
    except Timeout:
        if retries < 3:
            return _send_cloudflare_request(endpoint, method, headers, data, retries + 1, **kwargs)
        raise RuntimeError(f"Cloudflare API request for {endpoint} timed out.")
    except RequestException as e:
        raise RuntimeError(f"Cloudflare API request for {endpoint} failed: {e}")

@cache
def get_cloudflare_account_id() -> str:
    response = _send_cloudflare_request('accounts', headers=CLOUDFLARE_HEADERS, timeout=3600)
    return response.json()['result'][0]['id']

def add_domain_to_cloudflare(domain: str, retries : int = 3) -> Tuple[str, List[str]]:
    cloudflare_account_id: str = get_cloudflare_account_id()
    data = {"name": domain, "account": {"id": cloudflare_account_id}, "jump_start": True}
    response = _send_cloudflare_request('zones', method='post', headers=CLOUDFLARE_HEADERS, data=data)
    result = response.json()["result"]
    zone_id = result["id"]
    nameservers = result["name_servers"]
    return zone_id, nameservers

def get_all_domains() -> List[str]:
    response = _send_cloudflare_request('zones', headers=CLOUDFLARE_HEADERS)
    return [{
        'name': zone['name'],
        'id': zone['id'],
        'nameservers': zone['name_servers']
        } for zone in response.json()['result']]

def create_cloudflare_redirect(zone_id: str, pattern: str = '*') -> bool:
    data = {
        "targets": [{"target": "url", "constraint": {"operator": "matches", "value": pattern}}],
        "actions": [{"id": "forwarding_url", "value": {"url": CLOUDFLARE_REDIRECT_URL, "status_code": 301}}],
        "priority": 1,
        "status": "active"
    }
    response = _send_cloudflare_request(f'zones/{zone_id}/pagerules', method='post', headers=CLOUDFLARE_HEADERS, data=data)
    return response.status_code == 200