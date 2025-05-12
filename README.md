# Advanced Discord Webhook Logger 🌐🔍
### WARNING THIS CODE IS ONLY FOR EDUCATION PURPOSE ONLY

A powerful IP/device tracking tool that logs detailed visitor information to your Discord webhook, including geolocation, device fingerprints, and VPN detection.

![Demo Screenshot](https://files.catbox.moe/p1vfwp.png)

## Features ✨

- 📌 IP address tracking with geolocation (country, city, ZIP)
- 🖥️ Detailed device/browser fingerprinting
- 🔍 VPN/Proxy/Tor detection
- 📱 Mobile device identification
- 🌐 Network information (ISP, ASN)
- 🔗 Automatic lookup links
- 💾 Session tracking
- 🛡️ Basic anti-detection measures

## Requirements 📋

- Python 3.8+
- pip package manager

## Installation ⚙️

### For Linux:
**bash**
# Clone the repository
```git clone https://github.com/yourusername/webhook-logger.git
cd webhook-logger```

# Install dependencies
```pip3 install -r requirements.txt```

# Edit configuration
```nano config.py  # Add your Discord webhook URL```


## Termux (Android) Installation & Usage 📱

### Full Setup Guide:

**bash**
# 1. Update packages and install requirements
```pkg update -y && pkg upgrade -y```
 ```pkg install python git -y````

# 2. Clone the repository
```git clone https://github.com/yourusername/webhook-logger.git```
```cd webhook-logger```

# 3. Install Python dependencies
```pip install -r requirements.txt```

# 4. Configure your webhook
nano config.py
# Replace "YOUR_DISCORD_WEBHOOK_URL" with your actual webhook URL
# Save with Ctrl+O, Enter, then Ctrl+X

USAGE 🚀
```python3 tool.py```
