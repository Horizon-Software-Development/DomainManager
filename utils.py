from functools import cache
import requests
from requests.exceptions import RequestException, Timeout
from namecheapapi import DomainAPI
import os
from faker import Faker

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

def create_domain_csv(domains: list[dict[str, str | list]]) -> None:
    gen = Faker()
    with open('output/inboxer.csv', 'w') as f:
        f.write('Domain,Nameserver-1,Nameserver-2,Password,Redirect,Email-1,Email-2,Email-3,Name-1,Name-2,Name-3\n')
        for domain in domains:
            name_1 = gen.name()
            name_2 = gen.name()
            name_3 = gen.name()
            email_1 = name_1.replace(' ', '').lower() + '@' + domain['name']
            email_2 = name_2.replace(' ', '').lower() + '@' + domain['name']
            email_3 = name_2.replace(' ', '').lower() + '@' + domain['name']
            f.write(f"{domain['name']},{domain['nameservers'][0]},{domain['nameservers'][1]},{gen.password()},{os.getenv('CLOUDFLARE_REDIRECT_URL')},{email_1},{email_2},{email_3},{name_1},{name_2},{name_3}\n")
