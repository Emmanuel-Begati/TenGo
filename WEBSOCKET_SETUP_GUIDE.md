# TenGo WebSocket & Redis Setup Guide

## 🎯 Overview

This guide will help you set up and run your TenGo Django application with WebSocket support (Django Channels) and Redis for optimal performance.

## 🛠️ Prerequisites

1. **Redis Server** (for WebSocket channel layer)
2. **Nginx** (for reverse proxy)
3. **Python Virtual Environment**
4. **SSL Certificate** (for production HTTPS)

## 📋 Step-by-Step Setup

### 1. Install Redis (if not already installed)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# Start and enable Redis
sudo systemctl start redis
sudo systemctl enable redis

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### 2. Install Python Dependencies

```bash
cd /home/thisisemmanuel-tengo/htdocs/tengo.thisisemmanuel.pro

# Activate virtual environment
source venv/bin/activate

# Install/update requirements
pip install -r requirements.txt
```

### 3. Environment Configuration

Ensure your `.env` file has the correct Redis configuration:

```bash
# Check current .env
cat .env

# Make sure these are set:
USE_REDIS=True
REDIS_URL=redis://localhost:6379/0
```

### 4. Django Setup

```bash
# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Test Django configuration
python manage.py check
```

### 5. Start Services

#### Option A: Use the automated script (Recommended)

```bash
# Make sure the script is executable
chmod +x start_services.sh

# Start all services
./start_services.sh
```

#### Option B: Manual startup

```bash
# 1. Start Redis (if not running)
sudo systemctl start redis

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start Django ASGI server
daphne -b 0.0.0.0 -p 8060 TenGo.asgi:application

# Or run in background:
nohup daphne -b 0.0.0.0 -p 8060 TenGo.asgi:application > django.log 2>&1 &
```

### 6. Configure Nginx

```bash
# Copy the nginx configuration
sudo cp nginx_config.conf /etc/nginx/sites-available/tengo

# Enable the site
sudo ln -sf /etc/nginx/sites-available/tengo /etc/nginx/sites-enabled/tengo

# Remove default site if needed
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 7. SSL Certificate Setup (Production)

```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d tengo.thisisemmanuel.pro

# Certbot will automatically update your nginx configuration
```

## 🧪 Testing the Setup

### Test WebSocket Connections

```bash
# Install websockets for testing
source venv/bin/activate
pip install websockets

# Run WebSocket test
python test_websockets.py
```

### Test with Browser Console

Open your browser's developer console and test:

```javascript
// Test delivery WebSocket
const deliveryWs = new WebSocket('wss://tengo.thisisemmanuel.pro/ws/delivery/');
deliveryWs.onopen = () => console.log('Delivery WebSocket connected');
deliveryWs.onmessage = (event) => console.log('Delivery message:', event.data);

// Test restaurant WebSocket (replace 1 with actual restaurant ID)
const restaurantWs = new WebSocket('wss://tengo.thisisemmanuel.pro/ws/restaurant/1/');
restaurantWs.onopen = () => console.log('Restaurant WebSocket connected');
restaurantWs.onmessage = (event) => console.log('Restaurant message:', event.data);
```

## 🔧 Service Management

### Start Services

```bash
# Start all services
./start_services.sh
```

### Stop Services

```bash
# Stop all services
./stop_services.sh
```

### Check Service Status

```bash
# Check Django server
lsof -i :8060

# Check Redis
sudo systemctl status redis

# Check Nginx
sudo systemctl status nginx

# View Django logs
tail -f django.log
```

## 🐛 Troubleshooting

### Common Issues

1. **Port 8060 already in use**
   ```bash
   sudo lsof -ti:8060
   sudo kill -9 $(lsof -ti:8060)
   ```

2. **Redis connection failed**
   ```bash
   sudo systemctl restart redis
   redis-cli ping
   ```

3. **WebSocket connection refused**
   - Check if Django server is running on port 8060
   - Verify nginx configuration
   - Check Django logs for errors

4. **Static files not loading**
   ```bash
   python manage.py collectstatic --noinput
   sudo systemctl reload nginx
   ```

### Log Files

- **Django logs**: `django.log` in project directory
- **Nginx access logs**: `/var/log/nginx/tengo_access.log`
- **Nginx error logs**: `/var/log/nginx/tengo_error.log`
- **Redis logs**: `sudo journalctl -u redis`

## 🚀 Production Deployment

### Key Points for Production

1. **Security**:
   - Set `DEBUG = False` in settings
   - Use strong `SECRET_KEY`
   - Configure proper `ALLOWED_HOSTS`
   - Enable SSL/TLS

2. **Performance**:
   - Use Redis for caching and channels
   - Configure proper Nginx caching
   - Use a process manager like systemd or supervisor

3. **Monitoring**:
   - Set up log rotation
   - Monitor Redis memory usage
   - Monitor WebSocket connections

### Systemd Service (Optional)

Create `/etc/systemd/system/tengo.service`:

```ini
[Unit]
Description=TenGo Django Application
After=network.target redis.service
Requires=redis.service

[Service]
Type=simple
User=thisisemmanuel-tengo
WorkingDirectory=/home/thisisemmanuel-tengo/htdocs/tengo.thisisemmanuel.pro
Environment=PATH=/home/thisisemmanuel-tengo/htdocs/tengo.thisisemmanuel.pro/venv/bin
ExecStart=/home/thisisemmanuel-tengo/htdocs/tengo.thisisemmanuel.pro/venv/bin/daphne -b 0.0.0.0 -p 8060 TenGo.asgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tengo
sudo systemctl start tengo
```

## 📊 Expected Results

After successful setup:

1. ✅ Django application running on port 8060
2. ✅ Redis running on port 6379
3. ✅ Nginx proxying HTTPS to Django
4. ✅ WebSocket connections working via `/ws/` endpoints
5. ✅ Static files served efficiently by Nginx
6. ✅ Real-time notifications for delivery and restaurant dashboards

Your TenGo application should now be fully functional with WebSocket support! 🎉
