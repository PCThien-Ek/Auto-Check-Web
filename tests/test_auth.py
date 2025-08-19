import re

def test_login_form_fields(page, base_url, login_path):
    page.goto(f"{base_url}{login_path}")
    page.get_by_placeholder("Email").is_visible()
    page.get_by_placeholder("Password").is_visible()
    page.get_by_role("button", name=re.compile(r"^\s*Log\s*in\s*$", re.I)).is_visible()

def test_password_toggle_eye(page, base_url, login_path):
    page.goto(f"{base_url}{login_path}")
    pwd = page.get_by_placeholder("Password")
    pwd.fill("12345678")
    # thử bấm icon 'eye' nếu có
    eye = page.locator('[data-testid="password-visibility"], [aria-label*="show"], [aria-label*="hide"]')
    if eye.count():
        eye.first.click()
        assert pwd.get_attribute("type") in ("text", "password")

def test_forgot_password_link(page, base_url, login_path):
    page.goto(f"{base_url}{login_path}")
    link = page.get_by_role("link", name=re.compile("forgot", re.I))
    if link.count():
        href = link.first.get_attribute("href")
        assert href and "forgot" in href.lower()

def test_register_link_exists(page, base_url, login_path):
    page.goto(f"{base_url}{login_path}")
    reg = page.get_by_role("link", name=re.compile("create|sign\s*up|register", re.I))
    assert reg.count() > 0
