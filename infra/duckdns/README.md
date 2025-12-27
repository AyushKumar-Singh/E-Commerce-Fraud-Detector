# DuckDNS Setup Guide

DuckDNS provides free dynamic DNS subdomains. Perfect for home servers or development environments without a static IP.

## Quick Setup

### 1. Create Account & Subdomain
1. Go to [duckdns.org](https://www.duckdns.org)
2. Sign in with GitHub, Google, Reddit, or Twitter
3. Create a subdomain (e.g., `fraud-detector`)
4. Note your **token** from the dashboard

### 2. Configure Update Script
```bash
# Edit the script
nano duck.sh

# Update these values:
SUBDOMAIN="your-subdomain"  # e.g., "fraud-detector"
TOKEN="your-duckdns-token"  # From dashboard

# Make executable
chmod 700 duck.sh

# Test it
./duck.sh
cat ~/duckdns/duck.log
```

### 3. Setup Automatic Updates (Cron)
```bash
# Open crontab editor
crontab -e

# Add this line (updates every 5 minutes)
*/5 * * * * /home/YOUR_USER/E-Commerce_Fraud_Detector/infra/duckdns/duck.sh >/dev/null 2>&1
```

### 4. Verify
```bash
# Check if IP is updated
ping fraud-detector.duckdns.org

# Check logs
cat ~/duckdns/duck.log
```

## Your Domain

After setup, your application will be accessible at:
```
http://fraud-detector.duckdns.org
```

Use this domain with Let's Encrypt to get free SSL:
```bash
sudo certbot --nginx -d fraud-detector.duckdns.org
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `KO` response | Check token and subdomain spelling |
| No updates | Verify cron is running: `crontab -l` |
| IP not changing | Check public IP: `curl ifconfig.me` |
