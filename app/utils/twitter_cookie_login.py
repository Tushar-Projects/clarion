# twitter_cookie_login_human.py
import asyncio
import json
import math
import os
import random
import time
from typing import Tuple

from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

load_dotenv()

TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")

# Choose engine: "firefox" (recommended), "chromium", "webkit"
BROWSER_ENGINE = os.getenv("PLAYWRIGHT_ENGINE", "firefox")

# Where cookies will be stored
SESSION_FILE = "twitter_session.json"

# --- Human-ish helpers -------------------------------------------------------
def rand(min_v=0.2, max_v=1.2):
    return random.uniform(min_v, max_v)

async def human_delay(min_s=0.6, max_s=2.2):
    await asyncio.sleep(rand(min_s, max_s))

async def human_pause_long():
    await asyncio.sleep(rand(2.5, 5.5))

async def human_type(el, text: str, min_delay=0.12, max_delay=0.28):
    """
    Type text char-by-char with variable delays and occasional small backspace+pause
    to mimic human typing mistakes/corrections.
    """
    for ch in text:
        await el.type(ch, delay=int(random.uniform(min_delay, max_delay) * 1000))
        # micro pause occasionally for realism
        if random.random() < 0.06:
            await asyncio.sleep(random.uniform(0.05, 0.25))
    # occasional short thinking pause after typing
    if random.random() < 0.3:
        await asyncio.sleep(random.uniform(0.3, 0.9))

async def smooth_move_mouse(page: Page, start: Tuple[int, int], end: Tuple[int, int], steps=20):
    """
    Move the mouse in a smooth curve from start to end (a tiny bit slower).
    """
    sx, sy = start
    ex, ey = end
    for i in range(1, steps + 1):
        t = i / steps
        # ease-in-out cubic
        t_e = (3 - 2 * t) * (t ** 2)
        x = sx + (ex - sx) * t_e + random.uniform(-1, 1)
        y = sy + (ey - sy) * t_e + random.uniform(-1, 1)
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.006, 0.02))

def pick_random_viewport():
    # Choose a desktop-like viewport or a large laptop
    choices = [
        {"width": 1366, "height": 768},
        {"width": 1440, "height": 900},
        {"width": 1536, "height": 864},
        {"width": 1280, "height": 800}
    ]
    return random.choice(choices)

def random_user_agent():
    # A small pool of realistic desktop user agents (rotate)
    agents = [
        # Firefox desktop
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        # Chrome desktop
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Safari Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15"
    ]
    return random.choice(agents)

# --- Main login flow --------------------------------------------------------
async def login_and_save_cookies():
    if not TWITTER_USERNAME or not TWITTER_PASSWORD:
        raise Exception("Set TWITTER_USERNAME and TWITTER_PASSWORD in your environment (or .env).")

    async with async_playwright() as p:
        print(f"🚀 Launching {BROWSER_ENGINE} (headful recommended)...")

        launch_opts = dict(headless=False, slow_mo=120)  # slow_mo helps; headful is less suspicious
        browser: Browser
        if BROWSER_ENGINE == "firefox":
            browser = await p.firefox.launch(**launch_opts)
        elif BROWSER_ENGINE == "webkit":
            browser = await p.webkit.launch(**launch_opts)
        else:
            browser = await p.chromium.launch(**launch_opts)

        viewport = pick_random_viewport()
        ua = random_user_agent()
        context: BrowserContext = await browser.new_context(
            user_agent=ua,
            viewport=viewport,
            locale="en-US",
            timezone_id="America/Los_Angeles",  # adjust if you want
            java_script_enabled=True,
        )

        # Extra headers to look more "real"
        await context.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1"
        })

        page: Page = await context.new_page()
        try:
            print("🌐 Navigating to https://x.com/i/flow/login ...")
            await page.goto("https://x.com/i/flow/login", timeout=180_000)
            await human_delay(2.4, 4.8)

            # attempt multiple selector options, waiting patiently
            selectors = [
                'input[name="text"]',                 # common
                'input[autocomplete="username"]',     # alternate
                'input[type="text"]',
            ]
            username_el = None
            for sel in selectors:
                try:
                    await page.wait_for_selector(sel, timeout=40_000)
                    username_el = await page.query_selector(sel)
                    if username_el:
                        break
                except Exception:
                    # missing selector — continue to next possibility
                    pass

            if not username_el:
                print("❌ Username input not found (timed out). Saving page dump for debugging.")
                await page.screenshot(path="login_username_missing.png", full_page=True)
                content = await page.content()
                open("login_page_dump.html", "w", encoding="utf-8").write(content)
                return

            # scroll + hover + move mouse + click + type
            box = await username_el.bounding_box()
            if box:
                # move mouse slowly to this field
                await smooth_move_mouse(page, (random.randint(100, 300), random.randint(100, 300)),
                                        (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2),
                                        steps=random.randint(18, 36))
                await page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            else:
                await username_el.click()

            await human_delay(0.8, 1.6)
            await human_type(username_el, TWITTER_USERNAME)

            # some flows have a "Next" button — try to detect it and click human-like
            try:
                next_btn_selectors = ['div[role="button"]:has-text("Next")', 'text="Next"', 'div:has-text("Next")']
                clicked_next = False
                for ns in next_btn_selectors:
                    try:
                        nb = await page.query_selector(ns)
                        if nb:
                            nb_box = await nb.bounding_box()
                            if nb_box:
                                await smooth_move_mouse(page, (box["x"], box["y"] + box["height"]), 
                                                        (nb_box["x"] + nb_box["width"]/2, nb_box["y"] + nb_box["height"]/2),
                                                        steps=random.randint(12, 24))
                                await nb.click()
                                clicked_next = True
                                break
                    except Exception:
                        continue
                if not clicked_next:
                    # Press Enter as fallback but wait shortly
                    await human_delay(0.6, 1.2)
                    await page.keyboard.press("Enter")
            except Exception:
                pass

            await human_delay(2.0, 4.0)

            # Wait for either password field, or an extra flow (e.g., "email instead")
            pwd_selectors = ['input[name="password"]', 'input[type="password"]']
            password_el = None
            for sel in pwd_selectors:
                try:
                    await page.wait_for_selector(sel, timeout=60_000)
                    password_el = await page.query_selector(sel)
                    if password_el:
                        break
                except Exception:
                    pass

            if not password_el:
                print("⚠️ Password input not detected. There might be an intermediate verification step. Dumping page.")
                await page.screenshot(path="password_missing.png", full_page=True)
                open("post_username_page.html", "w", encoding="utf-8").write(await page.content())
                return

            pwd_box = await password_el.bounding_box()
            if pwd_box:
                await smooth_move_mouse(page, (random.randint(200, 500), random.randint(200, 500)),
                                        (pwd_box["x"] + pwd_box["width"]/2, pwd_box["y"] + pwd_box["height"]/2),
                                        steps=random.randint(18, 36))
                await page.mouse.click(pwd_box["x"] + pwd_box["width"]/2, pwd_box["y"] + pwd_box["height"]/2)
            else:
                await password_el.click()

            await human_delay(0.8, 1.8)
            await human_type(password_el, TWITTER_PASSWORD)

            # Click login / submit
            # try to find buttons labelled Log in / Login / Continue
            login_btn = None
            for txt in ["Log in", "Log in", "Log in to Twitter", "Sign in", "Log in to X"]:
                candidate = await page.query_selector(f'div[role="button"]:has-text("{txt}")')
                if candidate:
                    login_btn = candidate
                    break
            if login_btn:
                lb_box = await login_btn.bounding_box()
                if lb_box:
                    await smooth_move_mouse(page, (pwd_box["x"], pwd_box["y"] + pwd_box["height"]),
                                            (lb_box["x"] + lb_box["width"]/2, lb_box["y"] + lb_box["height"]/2),
                                            steps=random.randint(12, 24))
                    await login_btn.click()
                else:
                    await login_btn.click()
            else:
                # fallback to Enter
                await human_delay(0.5, 1.2)
                await page.keyboard.press("Enter")

            # Wait some more for navigation; allow a longer timeout
            await human_delay(4.0, 7.0)
            try:
                await page.wait_for_load_state("networkidle", timeout=120_000)
            except Exception:
                # still proceed to check page contents
                pass

            # Detect common failure messages and handle
            page_content = (await page.content()).lower()
            if "could not log you in" in page_content or "try again later" in page_content or "attention required" in page_content:
                print("⚠️ Detected login failure page content. Saving screenshot and HTML dump.")
                await page.screenshot(path="login_failure.png", full_page=True)
                open("login_failure_dump.html", "w", encoding="utf-8").write(await page.content())
                return

            # Otherwise assume success if URL looks like home or profile
            current_url = page.url
            print("📍 Current URL:", current_url)
            if any(x in current_url for x in ["/home", "/i/", "/explore"]) or "login" not in current_url:
                # Success
                print("✅ Login appears successful — saving cookies...")
                cookies = await context.cookies()
                with open(SESSION_FILE, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, indent=2)
                print(f"💾 Cookies saved to {SESSION_FILE}")
            else:
                print("⚠️ Login ambiguous. Saving debug snapshot.")
                await page.screenshot(path="login_ambiguous.png", full_page=True)
                open("login_ambiguous.html", "w", encoding="utf-8").write(await page.content())

        except Exception as ex:
            print("❌ Unexpected error during login flow:", ex)
            await page.screenshot(path="login_unexpected_error.png", full_page=True)
            open("login_exception.html", "w", encoding="utf-8").write(await page.content())
        finally:
            await context.close()
            await browser.close()

# Launch
if __name__ == "__main__":
    asyncio.run(login_and_save_cookies())
