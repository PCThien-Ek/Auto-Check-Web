# tests/test_login.py
import re

def test_login_succeeds(logged_page):
    assert not re.search(r"/login(\b|/|\?|#)", logged_page.url, re.I), f"Still on login: {logged_page.url}"

def test_no_login_modal_after_login(logged_page):
    modal = logged_page.locator('[role="dialog"][aria-modal="true"] .ant-modal-content').first
    assert modal.count() == 0 or not modal.is_visible(), "Modal login vẫn còn hiển thị."
