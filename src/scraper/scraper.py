from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import pandas as pd

def scrape_flight_data(source, dest, date):
    opt = webdriver.ChromeOptions()
    opt.add_argument("--headless")
    opt.add_argument("--disable-gpu")
    opt.add_argument("--disable-dev-shm-usage")
    opt.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options = opt)

    try:
        url = f"https://www.kayak.co.in/flights/{source}-{dest}/{date}?sort=bestflight_a"
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'listWrapper')]"))
        )
        time.sleep(5)

        flights = driver.find_elements(By.XPATH, "//div[contains(@id, 'listWrapper')]")
        flight_data = []

        for flight in flights:
            try:
                airline = flight.find_element(By.XPATH, ".//div[contains(@class, 'J0g6-operator-text')]").text
                departure = flight.find_element(By.XPATH, ".//div[contains(@class, 'vmXl')]/span[1]").text
                arrival = flight.find_element(By.XPATH, ".//div[contains(@class, 'vmXl')]/span[3]").text
                duration = flight.find_element(By.XPATH, ".//div[contains(@class, 'vmXl vmXl-mod-variant-default')]").text
                stops = flight.find_element(By.XPATH, ".//div[contains(@class, 'JWEO-stops-text')]").text
                price = flight.find_element(By.XPATH, ".//div[contains(@class, 'f8F1-price-text')]").text

                try:
                    seat_type = flight.find_element(By.XPATH, ".//div[contains(@class, 'DOum-name')]").text
                except:
                    seat_type = "NaN"

                flight_data.append({
                    "airline": airline,
                    "departure_time": departure,
                    "arrival_time": arrival,
                    "duration": duration,
                    "seat_type": seat_type,
                    "stops": stops,
                    "price": price
                })
            except Exception as e:
                print(f"Error: {e}")

            df = pd.DataFrame(flight_data)
            
            f_name = f"{source}_{dest}_{date}_flights.csv"
            df.to_csv(f_name, index = False)

    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        driver.quit()

scrape_flight_data("BOM", "MAA", "2024-12-15")