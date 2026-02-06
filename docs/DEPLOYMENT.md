# Deployment Guide

This guide covers deploying the NAIA Airport Management System to a production environment.

## Table of Contents

1. [Server Requirements](#server-requirements)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Server Setup](#server-setup)
4. [Application Deployment](#application-deployment)
5. [Database Configuration](#database-configuration)
6. [Web Server Configuration](#web-server-configuration)
7. [SSL/TLS Setup](#ssltls-setup)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Backup Strategy](#backup-strategy)
10. [Troubleshooting](#troubleshooting)

---

## Server Requirements

### Minimum Hardware
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 20 GB SSD
- **Bandwidth**: 100 Mbps

### Recommended Hardware
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **Bandwidth**: 1 Gbps

### Software Requirements
- Ubuntu 22.04 LTS (or similar Linux distribution)
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Nginx 1.24+
- Supervisor (for process management)
- Let's Encrypt (for SSL certificates)

---

## Pre-Deployment Checklist

Before deploying, ensure:

- [ ] All tests pass locally
- [ ] DEBUG is set to False
- [ ] Secret key is generated and secure
- [ ] Database credentials are configured
- [ ] Email settings are configured
- [ ] Paystack API keys are set (production keys)
- [ ] Static files are collected
- [ ] Media storage is configured
- [ ] Logging is configured
- [ ] Error reporting is set up

---

## Server Setup

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Dependencies

```bash
# Python and build tools
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib libpq-dev

# Redis
sudo apt install -y redis-server

# Nginx
sudo apt install -y nginx

# Supervisor
sudo apt install -y supervisor

# Git
sudo apt install -y git

# Other utilities
sudo apt install -y curl wget vim htop
```

### 3. Create Application User

```bash
sudo useradd -m -s /bin/bash naia
sudo passwd naia
sudo usermod -aG sudo naia
```

---

## Application Deployment

### 1. Clone Repository

```bash
sudo -u naia -i
cd /home/naia
git clone https://github.com/yourusername/airport-management.git app
cd app
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env
```

Edit `.env` with production settings:

```env
# Core Settings
SECRET_KEY=your-very-long-random-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=naia_production
DB_USER=naia_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Paystack (Production Keys)
PAYSTACK_SECRET_KEY=sk_live_xxxxx
PAYSTACK_PUBLIC_KEY=pk_live_xxxxx

# Email
EMAIL_HOST=smtp.yourmailprovider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=email_password
DEFAULT_FROM_EMAIL=NAIA <noreply@yourdomain.com>

# Security
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. Run Migrations

```bash
python manage.py migrate --settings=airport_system.settings.production
```

### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput --settings=airport_system.settings.production
```

### 6. Create Superuser

```bash
python manage.py createsuperuser --settings=airport_system.settings.production
```

---

## Database Configuration

### 1. Create PostgreSQL Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE naia_production;
CREATE USER naia_user WITH PASSWORD 'secure_password_here';
ALTER ROLE naia_user SET client_encoding TO 'utf8';
ALTER ROLE naia_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE naia_user SET timezone TO 'Africa/Lagos';
GRANT ALL PRIVILEGES ON DATABASE naia_production TO naia_user;
\q
```

### 2. Configure Redis

Edit `/etc/redis/redis.conf`:

```conf
# Bind to localhost only
bind 127.0.0.1

# Set max memory
maxmemory 256mb
maxmemory-policy allkeys-lru

# Enable AOF persistence
appendonly yes
```

Restart Redis:

```bash
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

---

## Web Server Configuration

### 1. Gunicorn Configuration

Create `/home/naia/app/gunicorn.conf.py`:

```python
# Gunicorn configuration file
import multiprocessing

# Bind address
bind = "127.0.0.1:8000"

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
threads = 2

# Timeout
timeout = 60
keepalive = 5

# Logging
accesslog = "/home/naia/logs/gunicorn-access.log"
errorlog = "/home/naia/logs/gunicorn-error.log"
loglevel = "info"

# Process naming
proc_name = "naia_gunicorn"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

### 2. Supervisor Configuration

Create `/etc/supervisor/conf.d/naia.conf`:

```ini
[program:naia_web]
command=/home/naia/app/venv/bin/gunicorn airport_system.wsgi:application -c /home/naia/app/gunicorn.conf.py
directory=/home/naia/app
user=naia
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/naia/logs/supervisor-web.log
environment=DJANGO_SETTINGS_MODULE="airport_system.settings.production"

[program:naia_celery]
command=/home/naia/app/venv/bin/celery -A airport_system worker --loglevel=info
directory=/home/naia/app
user=naia
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/naia/logs/supervisor-celery.log
environment=DJANGO_SETTINGS_MODULE="airport_system.settings.production"

[program:naia_celerybeat]
command=/home/naia/app/venv/bin/celery -A airport_system beat --loglevel=info
directory=/home/naia/app
user=naia
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/naia/logs/supervisor-celerybeat.log
environment=DJANGO_SETTINGS_MODULE="airport_system.settings.production"
```

Create logs directory and start Supervisor:

```bash
sudo mkdir -p /home/naia/logs
sudo chown naia:naia /home/naia/logs
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### 3. Nginx Configuration

Create `/etc/nginx/sites-available/naia`:

```nginx
upstream naia_app {
    server 127.0.0.1:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/naia-access.log;
    error_log /var/log/nginx/naia-error.log;

    # Max upload size
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /home/naia/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/naia/app/media/;
        expires 7d;
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://naia_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health/ {
        proxy_pass http://naia_app;
        access_log off;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/naia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## SSL/TLS Setup

### Using Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Auto-Renewal

```bash
sudo certbot renew --dry-run
```

Add to crontab:

```bash
sudo crontab -e
# Add this line:
0 0 1 * * /usr/bin/certbot renew --quiet
```

---

## Monitoring and Logging

### Application Logs

- Gunicorn access: `/home/naia/logs/gunicorn-access.log`
- Gunicorn error: `/home/naia/logs/gunicorn-error.log`
- Django logs: `/home/naia/app/logs/`
- Celery: `/home/naia/logs/supervisor-celery.log`

### System Monitoring

Install monitoring tools:

```bash
# Install htop for system monitoring
sudo apt install htop

# Install netdata for web-based monitoring (optional)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

### Log Rotation

Create `/etc/logrotate.d/naia`:

```
/home/naia/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 naia naia
    sharedscripts
    postrotate
        supervisorctl restart naia_web
    endscript
}
```

---

## Backup Strategy

### Database Backups

Create backup script `/home/naia/scripts/backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/naia/backups/db"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="naia_db_backup_${DATE}.sql.gz"

mkdir -p $BACKUP_DIR
pg_dump naia_production | gzip > "${BACKUP_DIR}/${FILENAME}"

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

Add to crontab:

```bash
0 2 * * * /home/naia/scripts/backup_db.sh
```

### Media Files Backup

Create `/home/naia/scripts/backup_media.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/naia/backups/media"
DATE=$(date +%Y%m%d)
FILENAME="naia_media_backup_${DATE}.tar.gz"

mkdir -p $BACKUP_DIR
tar -czf "${BACKUP_DIR}/${FILENAME}" /home/naia/app/media/

# Keep only last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

---

## Troubleshooting

### Common Issues

**1. 502 Bad Gateway**
- Check if Gunicorn is running: `sudo supervisorctl status`
- Check Gunicorn logs: `tail -f /home/naia/logs/gunicorn-error.log`

**2. Static files not loading**
- Run `collectstatic` again
- Check Nginx configuration
- Check file permissions: `ls -la /home/naia/app/staticfiles/`

**3. Database connection errors**
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check credentials in `.env`
- Test connection: `psql -h localhost -U naia_user -d naia_production`

**4. Celery tasks not running**
- Check Celery worker: `sudo supervisorctl status naia_celery`
- Check Redis: `redis-cli ping`
- Check logs: `tail -f /home/naia/logs/supervisor-celery.log`

### Useful Commands

```bash
# Restart all services
sudo supervisorctl restart all
sudo systemctl reload nginx

# Check service status
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server

# View logs
tail -f /home/naia/logs/gunicorn-error.log
tail -f /var/log/nginx/naia-error.log
journalctl -u nginx -f

# Django management
cd /home/naia/app
source venv/bin/activate
python manage.py shell --settings=airport_system.settings.production
python manage.py dbshell --settings=airport_system.settings.production
```

---

## Security Recommendations

1. **Firewall**: Configure UFW to allow only necessary ports
   ```bash
   sudo ufw allow OpenSSH
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   ```

2. **Fail2ban**: Install and configure for SSH and Nginx protection
   ```bash
   sudo apt install fail2ban
   ```

3. **Regular Updates**: Keep system packages updated
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **SSH Hardening**: Disable password authentication, use SSH keys

5. **Database Security**: Ensure PostgreSQL only accepts local connections

---

**Last Updated**: 2024
