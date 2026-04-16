from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

URL = "https://benesovsky.denik.cz/volny-cas/kam-na-nejlepsi-tocene-cepovane-pivo-na-benesovsku-hlasujte-v-ankete-20260413.html"
TARGET = "CRAFT BEER PUB - U Škvorů, Čerčany"

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

driver.get(URL)
time.sleep(5)

answers = driver.find_elements(By.CLASS_NAME, "survey__answer")

clicked = False

for ans in answers:
    try:
        text = ans.text.strip()

        if TARGET in text:
            # kliknutí na odpověď
            ans.click()
            clicked = True
            print(f"Clicked: {text}")
            break
    except:
        pass

if not clicked:
    print("Target not found!")

# kliknutí na submit button
try:
    submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit.click()
    print("Vote submitted!")
except:
    print("Submit button not found!")

time.sleep(3)

# === výsledky ===
answers = driver.find_elements(By.CLASS_NAME, "survey__answer")

results = []

for ans in answers:
    try:
        text = ans.find_element(By.CLASS_NAME, "survey__progress-text").text
        percent_style = ans.find_element(By.CLASS_NAME, "survey__progress").get_attribute("style")
        percent = percent_style.split(":")[1].replace("%;", "").strip()

        results.append((text, float(percent)))
    except:
        pass

results.sort(key=lambda x: x[1], reverse=True)

print("=== CURRENT RESULTS ===")
for i, (name, pct) in enumerate(results, 1):
    print(f"{i}. {name} - {pct}%")

driver.quit()
