"""
utils/scraper.py
────────────────
Fetch chat messages from KidsChat.net and return them as
`Username: Message` lines.  Works for both guest and account login.

Dependencies
------------
selenium-4.x, webdriver-manager, beautifulsoup4, requests
"""

from __future__ import annotations
import time, re, requests
from typing import Optional, List
from bs4 import BeautifulSoup

PAUSE = 0.6  # slow things down so you can see each step


# ───────────────────────── helpers ──────────────────────────
def _sleep(t: float = PAUSE) -> None:
    time.sleep(t)


def _scroll_and_click(drv, xpath: str, timeout: int = 15):
    """Scroll until *xpath* is clickable or raise."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    step = drv.execute_script("return window.innerHeight") or 800
    end  = time.time() + timeout
    while time.time() < end:
        try:
            elem = WebDriverWait(drv, 1).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            elem.click()
            return
        except Exception:
            drv.execute_script("window.scrollBy(0, arguments[0]);", step)
    raise TimeoutError(f"Could not click {xpath!r} within {timeout}s")


def _maybe_switch_to_iframe(drv) -> None:
    """If a chat iframe exists, switch into it; otherwise stay put."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    try:
        WebDriverWait(drv, 3).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[src*='kidschat']")
            )
        )
        _sleep()
    except Exception:
        # no iframe on this code path – that’s fine
        pass


# ───────────────────────── core ─────────────────────────────
def scrape_chat_logs(
    url: str,
    *,
    use_selenium: bool,
    guest_login: bool,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> str:
    """
    Parameters
    ----------
    url          : KidsChat landing page (e.g. https://kidschat.net/)
    use_selenium : must be True for any login flow
    guest_login  : True ➜ click “Guest login”, False ➜ use username/password
    username/password : account creds (ignored when guest_login=True)
    """
    if not use_selenium:
        raise ValueError("KidsChat is JS-heavy – `use_selenium` must be True.")

    # ── Selenium setup ────────────────────────────────────────────
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from webdriver_manager.chrome import ChromeDriverManager

    opts = Options()
    # opts.add_argument("--headless=new")  # turn on once everything is stable
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    drv = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=opts
    )

    try:
        drv.get(url)
        _sleep()

        # 1️⃣ Accept the terms page
        _scroll_and_click(
            drv,
            "//*[self::a or self::button]"
            "[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),'i accept')]",
            timeout=20,
        )
        _sleep()

        # 2️⃣ Wait for redirect to /kidschat/
        WebDriverWait(drv, 20).until(EC.url_contains("/kidschat"))
        _sleep()

        # 3️⃣ Choose login method
        if guest_login:
            _scroll_and_click(drv, "//*[contains(@onclick,'getGuestLogin')]")
            _sleep(1.0)
        else:
            _scroll_and_click(drv, "//*[contains(@onclick,'getLogin')]")
            _sleep()

            # fill in creds
            user_in = drv.find_element(By.CSS_SELECTOR, "input[type='text']")
            pwd_in  = drv.find_element(By.CSS_SELECTOR, "input[type='password']")
            user_in.send_keys(username); _sleep()
            pwd_in.send_keys(password);  _sleep()
            pwd_in.send_keys(Keys.RETURN); _sleep(1.0)

        # 4️⃣ If the chat sits inside an iframe, switch to it
        _maybe_switch_to_iframe(drv)

        # 5️⃣ Wait for at least one chat message <li class="chat_log …">
        CHAT_ITEMS = "ul#chat_logs_container li.chat_log"
        WebDriverWait(drv, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, CHAT_ITEMS))
        )
        _sleep()

        html = drv.page_source

    finally:
        drv.quit()

    # ── Parse HTML with BeautifulSoup ────────────────────────────
    soup = BeautifulSoup(html, "html.parser")
    items: List[str] = []
    for li in soup.select("ul#chat_logs_container li.chat_log"):
        user = li.find("span", class_="chat_nickname")
        msg  = li.find("div",  class_="my_text")  # user messages
        if not user or not msg:
            # system messages or kicks/bans
            text = li.get_text(" ", strip=True)
            if text:
                items.append(text)
            continue
        items.append(f"{user.get_text(strip=True)}: {msg.get_text(strip=True)}")

    return "\n".join(items) or "No chat messages captured."
