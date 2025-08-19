# scripts/save_auth.py
import os
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv(override=True)
BASE = os.getenv("BASE_URL", "https://store.ratemate.top").rstrip("/")
PATH = os.getenv("LOGIN_PATH", "/en/login")
STATE = os.getenv("AUTH_STATE", "auth_state.json")

with sync_playwright() as p:
    b = p.chromium.launch(headless=False, slow_mo=150)
    ctx = b.new_context()
    page = ctx.new_page()
    page.goto(urljoin(BASE + "/", PATH.lstrip("/")), wait_until="domcontentloaded")
    print("\n==> Hãy đăng nhập tay trong cửa sổ (nếu có CAPTCHA/2FA).")
    input("==> Xong nhấn Enter ở terminal để lưu phiên...")
    ctx.storage_state(path=STATE)
    print(f"Đã lưu state vào {STATE}")
    b.close()
