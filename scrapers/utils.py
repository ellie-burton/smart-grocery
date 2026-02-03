# scrapers/utils.py
import re
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def _get_chrome_version():
    """Detect installed Chrome major version so we request a matching ChromeDriver."""
    try:
        if sys.platform == "win32":
            # Windows: registry
            result = subprocess.run(
                [
                    "reg",
                    "query",
                    r"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon",
                    "/v",
                    "version",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout:
                # Output e.g. "    version    REG_SZ    144.0.7559.110"
                for part in result.stdout.split():
                    if re.match(r"^\d+\.\d+\.\d+", part):
                        return part
        elif sys.platform == "darwin":
            # macOS
            result = subprocess.run(
                [
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "--version",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout:
                # e.g. "Google Chrome 144.0.7559.110"
                return result.stdout.strip().split()[-1]
        else:
            result = subprocess.run(
                ["google-chrome", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip().split()[-1]
    except Exception:
        pass
    return None


def get_chrome_major_version():
    """Return installed Chrome major version (e.g. 144) or None. Use for uc.Chrome(version_main=...)."""
    v = _get_chrome_version()
    if not v:
        return None
    try:
        return int(v.split(".")[0])
    except (ValueError, AttributeError):
        return None


def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Keep commented for debugging
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    chrome_version = _get_chrome_version()
    if chrome_version:
        driver_path = ChromeDriverManager(driver_version=chrome_version).install()
    else:
        driver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    driver.maximize_window()
    return driver