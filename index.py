import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = "https://benesovsky.denik.cz/volny-cas/kam-na-nejlepsi-tocene-cepovane-pivo-na-benesovsku-hlasujte-v-ankete-20260413.html"
TARGET = "CRAFT BEER PUB - U Škvorů, Čerčany"

# 🔥 CI proxy fix
os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

options = Options()

# 🧠 stealth / CI stabilita
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# 🧨 anti-proxy issues
options.add_argument("--no-proxy-server")
options.add_argument("--proxy-bypass-list=*")

# 🧠 důležité: snížení "automation fingerprint"
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 25)

try:
    driver.get(URL)

    # ⏳ počkej na body stránky (ne JS delay)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    time.sleep(3)

    driver.save_screenshot("step1_loaded.png")

    # 🍪 cookie (pokud existuje)
    try:
        cookie = driver.find_element(By.XPATH, "//button[contains(., 'Souhlas')]")
        driver.execute_script("arguments[0].click();", cookie)
    except:
        pass

    # ⏳ ANKETA
    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "survey__answer")))
    except:
        print("❌ survey__answer NOT FOUND → likely blocked or different HTML")

        print(driver.page_source[:2000])
        driver.save_screenshot("blocked_or_empty.png")

        driver.quit()
        exit(1)

    answers = driver.find_elements(By.CLASS_NAME, "survey__answer")

    print(f"Found answers: {len(answers)}")

    clicked = False

    for a in answers:
        text = a.text.strip()

        if TARGET in text:
            driver.execute_script("arguments[0].scrollIntoView(true);", a)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", a)

            print("✅ CLICKED:", text)
            clicked = True
            break

    if not clicked:
        print("❌ TARGET NOT FOUND")

    # 🟢 submit
    try:
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        driver.execute_script("arguments[0].click();", submit)
        print("✅ SUBMITTED")
    except:
        print("❌ SUBMIT NOT FOUND")

    time.sleep(5)

    # 📊 results debug
    try:
        results = driver.find_elements(By.CLASS_NAME, "survey__answer")

        print("=== RESULTS ===")
        for r in results:
            print(r.text)

    except:
        print("❌ RESULTS FAIL")
        driver.save_screenshot("results_fail.png")

finally:
    driver.save_screenshot("final.png")
    driver.quit()
