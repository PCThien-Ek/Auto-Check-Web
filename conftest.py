# conftest.py
import os, re, time
from urllib.parse import urljoin
from dotenv import load_dotenv
import pytest

load_dotenv(override=True)

AUTH_STATE_PATH = os.getenv("AUTH_STATE", "auth_state.json")

def _modal_visible(page) -> bool:
    try:
        modal = page.locator('[role="dialog"][aria-modal="true"] .ant-modal-content').first
        return modal.is_visible()
    except Exception:
        return False

@pytest.fixture(scope="session")
def base_url():
    return os.getenv("BASE_URL", "https://store.ratemate.top").rstrip("/")

@pytest.fixture(scope="session")
def login_path():
    return os.getenv("LOGIN_PATH", "/en/login")

@pytest.fixture(scope="session")
def creds():
    email = os.getenv("LOGIN_EMAIL") or (os.getenv("USERNAME") if "@" in (os.getenv("USERNAME") or "") else None)
    pwd   = os.getenv("LOGIN_PASSWORD") or os.getenv("PASSWORD")
    return {"user": email, "pwd": pwd}

@pytest.fixture
def logged_page(browser, base_url, login_path, creds):
    # --- Nhánh 1: có state sẵn -> dùng luôn
    if os.path.exists(AUTH_STATE_PATH):
        ctx = browser.new_context(storage_state=AUTH_STATE_PATH, base_url=base_url)
        page = ctx.new_page()
        page.goto(urljoin(base_url + "/", "en/store"), wait_until="domcontentloaded")
        if not _modal_visible(page):   # modal không hiện -> coi như đã login
            try:
                yield page
            finally:
                ctx.close()
            return
        ctx.close()  # state hết hạn -> rơi xuống nhánh 2

    # --- Nhánh 2: login qua modal/form
    ctx = browser.new_context(base_url=base_url)
    page = ctx.new_page()
    page.goto(urljoin(base_url + "/", login_path.lstrip("/")), wait_until="domcontentloaded")

    scope = page.locator('[role="dialog"][aria-modal="true"] .ant-modal-content').first
    if scope.count() == 0:
        scope = page  # fallback nếu form không nằm trong modal

    # Email
    email = scope.get_by_placeholder("Email")
    if email.count() == 0:
        email = scope.locator("#email")
    email.first.wait_for(state="visible", timeout=8000)
    assert creds["user"] and "@" in creds["user"], "Thiếu LOGIN_EMAIL hợp lệ trong .env"
    email.first.fill(creds["user"])

    # Password
    pwd = scope.get_by_placeholder("Password")
    if pwd.count() == 0:
        pwd = scope.locator('input[type="password"], #password')
    pwd.first.wait_for(state="visible", timeout=8000)
    assert creds["pwd"], "Thiếu LOGIN_PASSWORD/PASSWORD trong .env"
    pwd.first.fill(creds["pwd"])

    # Submit
    submit = scope.get_by_role("button", name=re.compile(r"^\s*Log\s*in\s*$", re.I))
    if submit.count() == 0:
        submit = scope.locator('button[type="submit"]')
    submit.first.wait_for(state="attached", timeout=5000)
    submit.first.click()

    # Thành công khi: modal **biến mất** hoặc rời /login (chờ tối đa 15s)
    deadline = time.time() + 15
    while time.time() < deadline:
        left_login_url = re.search(r"/login(\b|/|\?|#)", page.url, re.I) is None
        if left_login_url or not _modal_visible(page):
            break
        time.sleep(0.4)
    else:
        os.makedirs("report", exist_ok=True)
        page.screenshot(path="report/login_failure.png", full_page=True)
        raise AssertionError(f"Login có vẻ chưa thành công. URL: {page.url} (xem report/login_failure.png)")

    # Lưu state cho lần sau/CI
    page.context.storage_state(path=AUTH_STATE_PATH)

    try:
        yield page
    finally:
        ctx.close()
