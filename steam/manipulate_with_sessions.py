import os
import json

import time
from playwright.sync_api import sync_playwright

# COOKIES_FILE = "steam_cookies.json"
STEAM_LOGIN_URL = "https://store.steampowered.com/login/"
STEAM_GUARD_URL = "https://store.steampowered.com/account/authorizeddevices"

abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
save_path = os.path.join(abs_path, 'steam', 'sessions')

def save_cookies(context, username):
    cookies = context.cookies()
    # Фильтруем куки только для store.steampowered.com
    filtered = [c for c in cookies if c.get("domain") == "store.steampowered.com"]

    sessionid = None
    steamLoginSecure = None

    for c in filtered:
        if c["name"] == "sessionid":
            sessionid = c["value"]
        elif c["name"] == "steamLoginSecure":
            steamLoginSecure = c["value"]

    if not sessionid or not steamLoginSecure:
        print("❌ Не найдены необходимые cookies для store.steampowered.com")
        return

    data = {
        username: {
            "sessionid": sessionid,
            "steamLoginSecure": steamLoginSecure
        }
    }

    with open(f"{save_path}/{username}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Куки сохранены в формате для пользователя {username}")

def load_cookies(context, username):
    path_to_account_cookies = f"{save_path}/{username}.json"
    if not os.path.exists(path_to_account_cookies):
        return False
    with open(path_to_account_cookies, "r", encoding="utf-8") as f:
        data = json.load(f)

    user_cookies = next(iter(data.values()))
    cookies_to_add = []

    # Формируем куки для Playwright
    for name, value in user_cookies.items():
        cookies_to_add.append({
            "name": name,
            "value": value,
            "domain": "store.steampowered.com",
            "path": "/",
            "httpOnly": False,
            "secure": True,
            "sameSite": "Lax"
        })

    context.add_cookies(cookies_to_add)
    print(f"🔑 Загружены куки пользователя: {list(data.keys())[0]}")
    return True

def login_automatically_and_save(username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(STEAM_LOGIN_URL)

        print("🔐 Ожидаем форму входа...")

        page.wait_for_selector('input[type="text"]')
        page.fill('input[type="text"]', username)

        page.wait_for_selector('input[type="password"]')
        page.fill('input[type="password"]', password)

        print("➡️ Нажимаем кнопку входа...")

        form = page.locator('form').filter(has=page.locator('input[type="password"]'))
        sign_in_button = form.locator('button[type="submit"]')
        sign_in_button.wait_for()
        sign_in_button.click()

        input("⏳ Если появляется капча — реши её и нажми Enter...")

        save_cookies(context)
        browser.close()

def close_all_sessions(username):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        if not load_cookies(context, username):
            print("❌ Нет сохранённой сессии. Сначала выполните вход.")
            return

        page = context.new_page()
        page.goto(STEAM_GUARD_URL)

        print("⏳ Переходим на страницу управления сессиями...")

        # Ждём кнопку из нужного блока и кликаем по ней
        page.wait_for_selector("button:has-text('Выйти из аккаунта везде')", timeout=10000)
        page.click("button:has-text('Выйти из аккаунта везде')")

        # Подтверждаем в модалке
        page.wait_for_selector("button:has-text('Продолжить')", timeout=5000)
        page.click("button:has-text('Продолжить')")

        print("✅ Все активные сессии завершены.")
        os.remove(f"{save_path}/{username}.json")
        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    print("1 — Автоматический вход и сохранение сессии")
    print("2 — Завершить все активные сеансы")

    choice = input("Выбери действие (1/2): ").strip()

    if choice == "1":
        login_automatically_and_save()
    elif choice == "2":
        close_all_sessions()
    else:
        print("❌ Неверный выбор.")



