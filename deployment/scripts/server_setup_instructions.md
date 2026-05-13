# Production deployment instructions for server admin

Place the release tarball `alumniconnect-prod.tar.gz` in `/tmp` on the server, then run:

```bash
sudo mkdir -p /var/www/alumniconnect
sudo tar -xzf /tmp/alumniconnect-prod.tar.gz -C /var/www/alumniconnect
sudo chown -R www-data:www-data /var/www/alumniconnect
```

Create a Python virtualenv and install requirements:

```bash
cd /var/www/alumniconnect/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Create the `.env.production` file at `/var/www/alumniconnect/.env.production` with values (example from `.env.production.example`). Ensure `SECRET_KEY` is >=32 chars and `PUBLIC_BASE_URL` is `https://csf.ru.ac.bd/iceaa`.

Create MySQL user and database (replace values):

```sql
CREATE DATABASE alumniconnect CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ac_user'@'localhost' IDENTIFIED BY 'REPLACE_WITH_PASSWORD';
GRANT ALL PRIVILEGES ON alumniconnect.* TO 'ac_user'@'localhost';
FLUSH PRIVILEGES;
```

Import schema if needed:

```bash
mysql -u ac_user -p alumniconnect < /var/www/alumniconnect/backend/schema.sql
```

Create systemd unit file and enable service (the repo provides a unit at `deployment/systemd/alumniconnect.service`).

Install and configure Nginx, copy `deployment/nginx/alumniconnect_iceaa.conf` to `/etc/nginx/sites-available/alumniconnect` and symlink to `sites-enabled`. Then test config and reload:

```bash
sudo ln -s /etc/nginx/sites-available/alumniconnect /etc/nginx/sites-enabled/alumniconnect
sudo nginx -t
sudo systemctl reload nginx
```

Obtain TLS certs with certbot (Nginx plugin recommended):

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d csf.ru.ac.bd
```

Verify the app at `https://csf.ru.ac.bd/iceaa/api/health`.
