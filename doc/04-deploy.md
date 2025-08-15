# 1. Connect to the server and initial setup (as root user)

```
ssh root@your_server_ip
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx git postgresql postgresql-contrib
```

# 2. Create a new user and configure permissions

```
adduser ali
CpG#A6&K[652
usermod -aG sudo ali
```

# 3. Switch to the new user (ali) and set up the project

```
su - ali
git clone -b main https://github.com/shahrokh-rhmani/sql-injection.git
cd sql-injection/

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# 4. Configure the .env file

```
mv env-example .env
```
```
cat .env
```
```
sed -i 's/DEBUG=True/DEBUG=False/' .env
sed -i "s/^ALLOWED_HOSTS=.*/ALLOWED_HOSTS=82.115.20.217/" .env
sed -i "s/^DB_NAME=.*/DB_NAME=shop_db/" .env
sed -i "s/^DB_USER=.*/DB_USER=shop_admin/" .env
```
```
NEW_PASSWORD="9~z+E39QoY&s4*&9"
sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=$(echo "$NEW_PASSWORD" | sed 's/[&]/\\&/g')|" .env
unset NEW_PASSWORD
```
```
sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())' | sed 's/[\/&]/\\&/g')/" .env
```
```
cat .env
```
```
history -c
```

# 5. PostgreSQL setup (as root user)

return to the root user
```
exit  
```
```
sudo -u postgres psql
```
```
CREATE DATABASE shop_db;
CREATE USER shop_admin WITH PASSWORD '9~z+E39QoY&s4*&9';
```
```
\q
```
```
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE shop_db TO shop_admin;"
sudo -u postgres psql -d shop_db -c "ALTER SCHEMA public OWNER TO shop_admin;"
```
```
sudo -u postgres psql -c "\l"
sudo -u postgres psql -c "\du"
```

# 6. Nginx configuration (as root user)

```
sudo nano /etc/nginx/sites-available/sql-injection
```
```
server {
    listen 80;
    server_name 82.115.20.217;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/sql-injection/static/;
        expires 30d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn/gunicorn.sock;
    }
}
```
```
sudo mkdir -p /var/www/sql-injection/static/
sudo chown -R ali:www-data /var/www/sql-injection/static/
sudo chmod -R 755 /var/www/sql-injection/static/
```
```
sudo ln -s /etc/nginx/sites-available/sql-injection /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```
```
sudo systemctl status nginx
```
```
sudo tail -n 50 /var/log/nginx/error.log
```

# 7. Gunicorn service setup (as root user)

```
sudo nano /etc/systemd/system/gunicorn.service
```
```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ali
Group=www-data
WorkingDirectory=/home/ali/sql-injection/src
ExecStart=/home/ali/sql-injection/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn/gunicorn.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```
```
sudo mkdir -p /run/gunicorn
sudo chown ali:www-data /run/gunicorn
sudo chmod 775 /run/gunicorn
```
```
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

# 8. Run migrations (as ali user)

```
su - ali
cd sql-injection/src/
source ../venv/bin/activate
python manage.py migrate
python manage.py collectstatic
```

