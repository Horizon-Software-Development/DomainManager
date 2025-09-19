from dotenv import load_dotenv
load_dotenv()
import cloudflare
import utils
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup.log'),
        logging.StreamHandler()
    ]
)

def setup_existing_domains():
    print("🚀 Setting up existing domains...")

    # Read domains from file
    with open('input/buy.txt') as f:
        domains = [line.strip() for line in f.readlines()]

    print(f"📋 Found {len(domains)} domains to setup")

    for i, domain in enumerate(domains, 1):
        print(f"\n[{i}/{len(domains)}] Processing domain: {domain}")

        try:
            # Step 3: Add to Cloudflare
            print(f"🌐 Adding {domain} to Cloudflare...")
            zone_id, nameservers = cloudflare.add_domain_to_cloudflare(domain)
            print(f"✅ Added to Cloudflare. Zone ID: {zone_id}")

            # Step 4: Create redirect rule
            print(f"🔀 Creating redirect rule for {domain}...")
            cloudflare.create_cloudflare_redirect(zone_id, pattern=f'*{domain}*')
            print(f"✅ Redirect rule created")

            # Optional: Update nameservers at Namecheap
            print(f"🔧 Updating nameservers at Namecheap...")
            utils.NAMECHEAP.set_nameservers(domain, nameservers)
            print(f"✅ Nameservers updated")

        except Exception as e:
            print(f"❌ Error with {domain}: {e}")
            logging.error(f"Failed to setup domain {domain}: {e}")

    print("✨ Setup complete!")

if __name__ == '__main__':
    cloudflare.assert_env_vars()
    utils.assert_env_vars()
    setup_existing_domains()