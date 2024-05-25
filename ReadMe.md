# Cloudflare Redirect Setup

This project helps you buy domains using Namecheap, set up a Cloudflare redirect using Python. It includes functions to check availlability of a domain using Namecheap add a domain to Cloudflare and create a page rule for URL redirection.

## Prerequisites

- Python 3.7+
- Cloudflare account
- Namecheap account

## Setup

### 1. Clone the Repository

sh git clone https://github.com/your-repo/cloudflare-redirect.git cd cloudflare-redirect

### 2. Create a Virtual Environment

sh python -m venv venv source venv/bin/activate # On Windows use venv\Scripts\activate

### 3. Install Requirements

sh pip install -r requirements.txt

### 4. Create and Configure `.env` File

Create a `.env` file in the root directory of the project and add your Cloudflare and Namecheap credentials. You can use the `.env.example` file as a reference.

sh cp .env.example .env

Edit the `.env` file and add your credentials:


CLOUDFLARE_API_KEY=your_cloudflare_api_key CLOUDFLARE_EMAIL=your_cloudflare_email CLOUDFLARE_API_URL=https://api.cloudflare.com/client/v4 CLOUDFLARE_REDIRECT_URL=https://your_redirect_url

NAMECHEAP_API_USER=your_namecheap_api_user NAMECHEAP_API_KEY=your_namecheap_api_key NAMECHEAP_USERNAME=your_namecheap_username NAMECHEAP_CLIENT_IP=your_local_ip_address

### 5. Add Your Local IP Address to Namecheap

Login to your Namecheap account and navigate to the API Access page. Add your local IP address to the list of allowed IPs.
Your Ip address: https://whatismyipaddress.com/

## Usage

create a .txt file listing all the domains you would like to buy at input/buy.py

sh (venv) python main.py 

