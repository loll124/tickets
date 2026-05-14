import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests

URL = "https://www.tazkarti.com/#/matches"
CHECK_INTERVAL = 30
NTFY_TOPIC = "NagatyMatch"

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = "/usr/bin/chromium"
    driver = webdriver.Chrome(
        service=Service("/usr/bin/chromedriver"),
        options=options
    )
    return driver

def check_for_tickets(driver):
    driver.get(URL)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "item-cate"))
        )
    except:
        print("Page timed out, retrying next round...")
        return False

    # keep clicking view more until it's gone or disabled
    while True:
        try:
            view_more = driver.find_element(By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'view more') and not(@disabled)]")
            driver.execute_script("arguments[0].click();", view_more)  # JS click bypasses interception
            time.sleep(3)
        except:
            break  # no more enabled view more button

    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    has_zamalek = "zamalek sc" in body_text
    has_date = "wed 20 may 2026" in body_text
    print(f"Zamalek: {has_zamalek} | Date: {has_date}")
    return has_zamalek and has_date

def notify():
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data="Zamalek tickets are live! Go buy now!",
        headers={
            "Title": "yalla ya bagaaaaty!",
            "Priority": "urgent",
            "Tags": "rotating_light"
        }
    )

# --- MAIN LOOP ---
driver = get_driver()
print(f"Watching for Zamalek tickets every {CHECK_INTERVAL}s...")

try:
    while True:
        if check_for_tickets(driver):
            notify()
            print("Zamalek tickets found! Notification sent!")
        else:
            print(f"No Zamalek tickets yet... checking again in {CHECK_INTERVAL}s")
        time.sleep(CHECK_INTERVAL)
finally:
    try:
        driver.quit()
    except:
        pass