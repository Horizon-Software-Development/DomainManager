from dotenv import load_dotenv
load_dotenv()
import cloudflare
import logging
import time
import utils

logging.basicConfig(filename='buy.log', level=logging.INFO)

def buy_domain(domain: str) -> None:
    try:
        zone_id, _ = cloudflare.add_domain_to_cloudflare(domain)
        logging.info(f"Successfully added domain {domain} to Cloudflare")
    except Exception as e:
        logging.error(f"Failed to add domain {domain} to Cloudflare: {e}")
        return
    checker = utils.NAMECHEAP.check(domain)
    if not checker.get(domain, False): 
        logging.error(f"Domain {domain} is not available.")
        return
    try:
        utils.NAMECHEAP.register(domain, address=utils.get_address()['Registrant'], 
            nameservers=_)
        logging.info(f"Successfully registered domain {domain}")
    except Exception as e:
        logging.error(f"Failed to register domain {domain}: {e}")
    
    time.sleep(10)
    try:
        cloudflare.create_cloudflare_redirect(zone_id, pattern=f'*{domain}*')
        logging.info(f"Successfully created redirect for domain {domain}")
    except Exception as e:
        logging.error(f"Failed to create redirect for domain {domain}: {e}")
        return
    return {
        'name': domain,
        'nameservers': _,
        'id': zone_id
    }
    
def fix_nameservers() -> None:
    domains = cloudflare.get_all_domains()
    for domain in domains:
        try:
            utils.NAMECHEAP.set_nameservers(domain['name'], domain['nameservers'])
            logging.info(f"Successfully set nameservers for domain {domain['name']}")
        except Exception as e:
            logging.error(f"Failed to set nameservers for domain {domain['name']}: {e}")
            continue
        time.sleep(2)

def fix_redirects() -> None:
    domains = cloudflare.get_all_domains()
    for domain in domains:
        try:
            cloudflare.create_cloudflare_redirect(domain['id'], pattern=f'*{domain["name"]}*')
            logging.info(f"Successfully created redirect for domain {domain['name']}")
        except Exception as e:
            logging.error(f"Failed to create redirect for domain {domain['name']}: {e}")
            continue
        time.sleep(2)

def generate_all_inboxes() -> None:
    domains = cloudflare.get_all_domains()
    utils.create_domain_csv(domains)
    
def main() -> None:
    domains_to_output = []
    try:
        with open('input/buy.txt') as f:
            domains = f.readlines()
        for domain in domains:
            try:
                _ = buy_domain(domain.strip())
                if _:
                    domains_to_output.append(_)
            except Exception as e:
                logging.error(f"Failed to register domain {domain.strip()}: {e}")
    except FileNotFoundError:
        logging.error("No domains to register.")
    except KeyboardInterrupt:
        logging.error("User interrupted the process.")
    utils.create_domain_csv(domains_to_output)

if __name__ == '__main__':
    cloudflare.assert_env_vars()
    utils.assert_env_vars()
    # main()
    # fix_nameservers()
    # fix_redirects()
    generate_all_inboxes()



        