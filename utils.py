from functools import cache
import requests
from requests.exceptions import RequestException, Timeout
from namecheap import Namecheap
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
        os.getenv('NAMECHEAP_USERNAME'),
        os.getenv('NAMECHEAP_API_KEY'),
        os.getenv('NAMECHEAP_EXAMPLE_DOMAIN')
    ]):
        raise RuntimeError("Missing Namecheap environment variables.")

class NamecheapWrapper:
    def __init__(self, nc):
        self.nc = nc

    def check(self, domain: str) -> dict:
        result = self.nc.domains.check(domain)
        return {domain: result[0].available if result else False}

    def register(self, domain: str, address: dict, nameservers: list):
        registrant = address
        return self.nc.domains.create(
            domain=domain,
            registrant_first_name=registrant['FirstName'],
            registrant_last_name=registrant['LastName'],
            registrant_address1=registrant['Address1'],
            registrant_city=registrant['City'],
            registrant_state_province=registrant['StateProvince'],
            registrant_postal_code=registrant['PostalCode'],
            registrant_country=registrant['Country'],
            registrant_phone=registrant['Phone'],
            registrant_email_address=registrant['EmailAddress'],
            nameservers=nameservers
        )

    def set_nameservers(self, domain: str, nameservers: list):
        return self.nc.domains.set_nameservers(domain, nameservers)

NAMECHEAP = NamecheapWrapper(Namecheap(
    api_key=os.getenv('NAMECHEAP_API_KEY'),
    username=os.getenv('NAMECHEAP_USERNAME'),
    api_user=os.getenv('NAMECHEAP_API_USER', os.getenv('NAMECHEAP_USERNAME')),
    client_ip=get_my_ip(),
    sandbox=False
))

@cache
def get_address() -> dict:
    domain_info = NAMECHEAP.nc.domains.info(os.getenv('NAMECHEAP_EXAMPLE_DOMAIN'))
    return {
        'Registrant': {
            'FirstName': domain_info.registrant.first_name,
            'LastName': domain_info.registrant.last_name,
            'Address1': domain_info.registrant.address1,
            'City': domain_info.registrant.city,
            'StateProvince': domain_info.registrant.state_province,
            'PostalCode': domain_info.registrant.postal_code,
            'Country': domain_info.registrant.country,
            'Phone': domain_info.registrant.phone,
            'EmailAddress': domain_info.registrant.email_address
        }
    }

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
            email_3 = name_3.replace(' ', '').lower() + '@' + domain['name']
            f.write(f"{domain['name']},{domain['nameservers'][0]},{domain['nameservers'][1]},{gen.password()},{os.getenv('CLOUDFLARE_REDIRECT_URL')},{email_1},{email_2},{email_3},{name_1},{name_2},{name_3}\n")
