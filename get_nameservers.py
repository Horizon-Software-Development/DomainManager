from dotenv import load_dotenv
load_dotenv()
import cloudflare
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nameservers.log'),
        logging.StreamHandler()
    ]
)

def get_cloudflare_nameservers():
    print("🚀 Getting Cloudflare nameservers for your domains...")

    # Read domains from file
    with open('input/buy.txt') as f:
        domains = [line.strip() for line in f.readlines()]

    print(f"📋 Found {len(domains)} domains")
    print("\n" + "="*60)
    print("STEP 1: Add these domains to Cloudflare and get nameservers")
    print("="*60)

    nameserver_info = []

    for i, domain in enumerate(domains, 1):
        print(f"\n[{i}/{len(domains)}] Processing domain: {domain}")

        try:
            # Add domain to Cloudflare to get nameservers
            print(f"🌐 Adding {domain} to Cloudflare...")
            zone_id, nameservers = cloudflare.add_domain_to_cloudflare(domain)

            nameserver_info.append({
                'domain': domain,
                'zone_id': zone_id,
                'nameservers': nameservers
            })

            print(f"✅ Added! Zone ID: {zone_id}")
            print(f"📡 Nameservers: {', '.join(nameservers)}")

        except Exception as e:
            print(f"❌ Error with {domain}: {e}")
            logging.error(f"Failed to get nameservers for {domain}: {e}")

    print("\n" + "="*60)
    print("STEP 2: Update nameservers at Namecheap")
    print("="*60)

    for info in nameserver_info:
        print(f"\nDomain: {info['domain']}")
        print(f"Nameserver 1: {info['nameservers'][0]}")
        print(f"Nameserver 2: {info['nameservers'][1]}")
        print("-" * 40)

    print(f"\n📝 Instructions:")
    print(f"1. Go to Namecheap dashboard")
    print(f"2. For each domain above, change nameservers to the Cloudflare ones")
    print(f"3. Wait 24 hours for DNS propagation")
    print(f"4. Then run: python setup_redirects.py")

    # Save info for later use
    import json
    with open('nameserver_info.json', 'w') as f:
        json.dump(nameserver_info, f, indent=2)

    print(f"\n💾 Nameserver info saved to: nameserver_info.json")

if __name__ == '__main__':
    cloudflare.assert_env_vars()
    get_cloudflare_nameservers()