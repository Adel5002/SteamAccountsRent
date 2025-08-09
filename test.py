import requests

# Замените эти значения на данные от вашего прокси
proxy_host = "150.241.251.77"  # IP
proxy_port = "50100"           # порт
proxy_user = "aromat2911"      # если требуется
proxy_pass = "dnfiXUVccs"      # если требуется

# Если прокси с авторизацией:
proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
print(proxy_url)

# Если прокси без авторизации:
# proxy_url = f"http://{proxy_host}:{proxy_port}"

proxies = {
    "http": proxy_url,
    "https": proxy_url
}

session = requests.Session()
session.proxies.update(proxies)

# Пример запроса через прокси
try:
    response = session.get("https://httpbin.org/ip", timeout=10)
    print("Ваш IP через прокси:", response.json())
except requests.exceptions.RequestException as e:
    print("Ошибка при использовании прокси:", e)
