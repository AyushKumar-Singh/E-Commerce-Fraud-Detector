#!/bin/bash
# DuckDNS Dynamic DNS Update Script
# E-Commerce Fraud Detector
#
# This script updates your DuckDNS subdomain with your current public IP.
# Run via cron every 5 minutes for automatic updates.
#
# SETUP:
# 1. Go to https://www.duckdns.org and login with GitHub/Google
# 2. Create a subdomain (e.g., "fraud-detector")
# 3. Copy your token from the DuckDNS dashboard
# 4. Update SUBDOMAIN and TOKEN below
# 5. Make executable: chmod 700 duck.sh
# 6. Test: ./duck.sh
# 7. Add to cron: crontab -e
#    */5 * * * * /path/to/duck.sh >/dev/null 2>&1

# ============================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================
SUBDOMAIN="YOUR_SUBDOMAIN"  # e.g., "fraud-detector" (without .duckdns.org)
TOKEN="YOUR_DUCKDNS_TOKEN"  # Your token from duckdns.org dashboard
# ============================================

# Log file
LOGFILE="${HOME}/duckdns/duck.log"
mkdir -p "$(dirname "$LOGFILE")"

# Timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Update DuckDNS
RESPONSE=$(curl -s "https://www.duckdns.org/update?domains=${SUBDOMAIN}&token=${TOKEN}&ip=")

# Log result
if [ "$RESPONSE" = "OK" ]; then
    echo "${TIMESTAMP} - SUCCESS: IP updated for ${SUBDOMAIN}.duckdns.org" >> "$LOGFILE"
else
    echo "${TIMESTAMP} - FAILED: Response was '${RESPONSE}'" >> "$LOGFILE"
fi

# Keep log file manageable (last 100 lines)
if [ -f "$LOGFILE" ]; then
    tail -100 "$LOGFILE" > "${LOGFILE}.tmp" && mv "${LOGFILE}.tmp" "$LOGFILE"
fi
