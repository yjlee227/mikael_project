
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium_stealth import stealth

# --- Setup Chrome Options ---
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
# The following arguments are recommended for stealth
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# --- Initialize WebDriver ---
# Selenium's built-in manager will attempt to download the correct chromedriver
driver = webdriver.Chrome(options=options)

# --- Apply Stealth ---
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

# --- Start Scraping ---
try:
    # Navigate to Klook
    url = "https://www.klook.com"
    print(f"Navigating to {url}...")
    driver.get(url)

    # Wait for the page to load for observation
    print("Waiting for 5 seconds to allow page to load...")
    time.sleep(5)

    print("Page loaded successfully.")
    print(f"Page Title: {driver.title}")

    # TODO: Add your specific scraping logic here.
    # For example: find elements, extract text, click buttons, etc.

finally:
    # --- Cleanup ---
    print("Closing the browser.")
    driver.quit()
