from dotenv import load_dotenv
load_dotenv()
import cloudflare
import logging
import time
import utils

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('buy.log'),
        logging.StreamHandler()
    ]
)

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
    print("🚀 Starting domain registration process...")
    domains_to_output = []
    try:
        with open('input/buy.txt') as f:
            domains = f.readlines()
        print(f"📋 Found {len(domains)} domains to process")

        for i, domain in enumerate(domains, 1):
            domain = domain.strip()
            print(f"\n[{i}/{len(domains)}] Processing domain: {domain}")
            try:
                result = buy_domain(domain)
                if result:
                    domains_to_output.append(result)
                    print(f"✅ Successfully processed {domain}")
                else:
                    print(f"❌ Failed to process {domain}")
            except Exception as e:
                print(f"💥 Error with {domain}: {e}")
                logging.error(f"Failed to register domain {domain}: {e}")
    except FileNotFoundError:
        print("❌ No input/buy.txt file found!")
        logging.error("No domains to register.")
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        logging.error("User interrupted the process.")

    print(f"\n📊 Creating CSV for {len(domains_to_output)} successful domains...")
    utils.create_domain_csv(domains_to_output)
    print("✨ Process complete!")

if __name__ == '__main__':
    cloudflare.assert_env_vars()
    utils.assert_env_vars()
    main()
    # fix_nameservers()
    # fix_redirects()
    # generate_all_inboxes()



        