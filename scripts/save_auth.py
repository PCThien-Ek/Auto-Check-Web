# scripts/save_auth.py
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, expect
from dotenv import load_dotenv
import os, json, time, re

load_dotenv(override=True)
BASE = os.getenv("BASE_URL", "https://store.ratemate.top").rstrip("/")
PATH = os.getenv("LOGIN_PATH", "/en/login")
STATE = os.getenv("AUTH_STATE", "auth_state.json")

with sync_playwright() as p:
    b = p.chromium.launch(headless=False, slow_mo=120)
    ctx = b.new_context()
    page = ctx.new_page()
    page.goto(urljoin(BASE + "/", PATH.lstrip("/")), wait_until="domcontentloaded")

    print("\n==> ĐĂNG NHẬP TAY tới khi modal đóng hẳn (không còn ô Email/Password).")
    input("==> Xong thì nhấn Enter để lưu phiên...")

    # Kiểm tra đã rời trang login/modal
    login_ui_still_visible = False
    try:
        email = page.get_by_placeholder("Email")
        pwd   = page.get_by_placeholder("Password")
        login_ui_still_visible = (email.is_visible() or pwd.is_visible())
    except Exception:
        pass

    # Heuristic: URL không còn /login và không còn input password
    if re.search(r"/login(\b|/|\?|#)", page.url, re.I) or login_ui_still_visible:
        print(f"[WARN] Có vẻ vẫn ở màn hình login. URL hiện tại: {page.url}")

    # Lưu state
    ctx.storage_state(path=STATE)

    # In nhanh số cookie và các key localStorage để bạn tự kiểm
    data = json.load(open(STATE, "r", encoding="utf-8"))
    cookies = data.get("cookies", [])
    origins = data.get("origins", [])
    ls_keys = []
    for o in origins:
        for item in o.get("localStorage", []):
            ls_keys.append(item["name"])
    print(f"[INFO] cookies: {len(cookies)} | localStorage keys: {ls_keys}")
    print(f"Đã lưu phiên vào: {STATE}")
    b.close()
