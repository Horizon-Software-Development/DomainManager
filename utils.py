from functools import cache
import requests
from requests.exceptions import RequestException, Timeout
from namecheapapi import DomainAPI
import os


@cache
def get_my_ip(retries: int = 0) -> str:
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        response.raise_for_status()
        return response.json()['ip']
    except Timeout:
        if retries < 3:
            return get_my_ip(retries + 1)
        raise RuntimeError("Failed to retrieve IP. Ipify API request timed out.")
    except RequestException as e:
        raise RuntimeError(f"Failed to retrieve IP: {e}")
    
def assert_env_vars() -> bool:
    if not all([
        os.getenv('NAMECHEAP_USER'),
        os.getenv('NAMECHEAP_KEY'),
        os.getenv('NAMECHEAP_EXAMPLE_DOMAIN')
    ]):
        raise RuntimeError("Missing Namecheap environment variables.")

NAMECHEAP = DomainAPI(
    api_user=os.getenv('NAMECHEAP_USER'),
    api_key=os.getenv('NAMECHEAP_KEY'),
    username=os.getenv('NAMECHEAP_USER'),
    client_ip=get_my_ip(),
    sandbox=False
)


@cache
def get_address() -> dict:
    return NAMECHEAP.get_contacts(os.getenv('NAMECHEAP_EXAMPLE_DOMAIN'))