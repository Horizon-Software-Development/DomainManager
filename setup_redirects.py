from dotenv import load_dotenv
load_dotenv()
import cloudflare
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('redirects.log'),
        logging.StreamHandler()
    ]
)

def setup_redirects():
    print("🚀 Setting up redirect rules...")

    # Load nameserver info from previous step
    try:
        with open('nameserver_info.json', 'r') as f:
            nameserver_info = json.load(f)
    except FileNotFoundError:
        print("❌ nameserver_info.json not found! Run get_nameservers.py first")
        return

    print(f"📋 Found {len(nameserver_info)} domains with nameserver info")

    for i, info in enumerate(nameserver_info, 1):
        domain = info['domain']
        zone_id = info['zone_id']

        print(f"\n[{i}/{len(nameserver_info)}] Setting up redirects for: {domain}")

        try:
            # Create redirect rule
            print(f"🔀 Creating redirect rule for {domain}...")
            success = cloudflare.create_cloudflare_redirect(zone_id, pattern=f'*{domain}*')

            if success:
                print(f"✅ Redirect rule created for {domain}")
            else:
                print(f"⚠️ Redirect rule may have failed for {domain}")

        except Exception as e:
            print(f"❌ Error creating redirect for {domain}: {e}")
            logging.error(f"Failed to create redirect for {domain}: {e}")

    print("\n✨ Redirect setup complete!")
    print(f"🌐 All domains should now redirect to: {cloudflare.CLOUDFLARE_REDIRECT_URL}")

if __name__ == '__main__':
    cloudflare.assert_env_vars()
    setup_redirects()