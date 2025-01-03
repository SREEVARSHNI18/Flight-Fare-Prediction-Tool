import os
import time
import pandas as pd
import numpy as np
import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from airportsdata import load


class AirportNotFoundError(Exception):
    """Custom exception"""

    pass


def setup_webdriver():
    # Set Chrome WebDriver options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
    chrome_options.add_argument("--window-size=1920,1080")

    # Initialize Chrome WebDriver
    return webdriver.Chrome(options=chrome_options)


def get_airport_code(city_name):
    print(city_name)
    airports = load("IATA")
    for code, details in airports.items():
        if details["city"].lower() == city_name.lower():
            print(f"Airport code for {city_name} is {code}")
            return code
    raise AirportNotFoundError(f"Airport code for the {city_name} couldnot be found")


def get_airlines(soup):
    """Extracts airline names from the BeautifulSoup object."""
    airlines = []
    airlines_tags = soup.find_all("span", class_="codeshares-airline-names", text=True)
    for tag in airlines_tags:
        airlines.append(tag.text)
    return airlines


def get_total_stops(soup):
    """Extracts total stops from the BeautifulSoup object."""
    stops_list = []
    stops = soup.find_all("div", class_="section stops")
    for stop in stops:
        for stop_text in stop.find_all("span", class_="stops-text"):
            stops_list.append(stop_text.text)
    return stops_list


def get_price(soup):
    """Extracts prices from the BeautifulSoup object."""
    prices = []
    price_tags = soup.find_all(
        "div", class_="Flights-Results-FlightPriceSection right-alignment sleek"
    )
    for tag in price_tags:
        for price_text in tag.find_all("span", class_="price-text"):
            prices.append(price_text.text)
    return prices


def get_duration(soup):
    """Extracts flight durations from the BeautifulSoup object."""
    duration_list = []
    durations = soup.find_all("div", class_="section duration allow-multi-modal-icons")
    for duration in durations:
        for duration_text in duration.find_all("div", class_="top"):
            duration_list.append(duration_text.text)
    return duration_list


def main():
    driver = setup_webdriver()
    sources = []
    destinations = []

    print("Please enter '-1' when done.")
    print("-" * 10)

    while True:
        source = input("From which city?\n")
        if source == "-1":
            break
        destination = input("Where to?\n")
        if destination == "-1":
            break
        sources.append(source)
        destinations.append(destination)
        print("-" * 10)

    print("\nRoutes:")
    for i in range(len(sources)):
        print(f"{sources[i]} => {destinations[i]}")

    start_date = np.datetime64(input("Start Date (YYYY-MM-DD): "))
    end_date = np.datetime64(input("End Date (YYYY-MM-DD): "))
    num_days = (end_date - start_date).item().days

    for i in range(len(sources)):
        column_names = [
            "Airline",
            "Source",
            "Destination",
            "Duration",
            "Total stops",
            "Price",
            "Date",
        ]

        data = []  # Initialize data list for each source and destination pair

        for j in tqdm.tqdm(range(num_days + 1)):
            if j % 10 == 0 and j != 0:
                driver.quit()
                driver = webdriver.Chrome(options=chrome_options)
            try:
                url = f"https://www.en.kayak.sa/flights/{get_airport_code(sources[i])}-{get_airport_code(destinations[i])}/{start_date + j}"
                print(url)
                driver.get(url)

                # Click the 'Show More' button to get all flights
                show_more_button = driver.find_element(
                    By.XPATH, '//a[@class = "moreButton"]'
                )
                if show_more_button:
                    show_more_button.click()
                    time.sleep(5)
                else:
                    print(f"Could not find 'Show More' button on {url}")
            except NoSuchElementException:
                print(f"Could not find 'Show More' button on {url}")
                continue

            soup = BeautifulSoup(driver.page_source, "html.parser")

            try:
                airlines = get_airlines(soup)
            except Exception as e:
                print(f"Error parsing data for {url}: {e}")
                continue

            if not airlines:
                print(f"No flights found for {url}")
                continue

            total_stops = get_total_stops(soup)
            prices = get_price(soup)
            duration = get_duration(soup)
            if (
                len(airlines) != len(prices)
                or len(airlines) != len(duration)
                or len(airlines) != len(total_stops)
            ):
                print(f"Error: Mismatched lengths on {url}")
                continue

            # Convert numpy.datetime64 object to Python datetime object
            current_date = (start_date + j).astype(datetime).strftime("%Y-%m-%d")

            # Append data to the list
            for k in range(len(airlines)):
                data.append(
                    {
                        "Airline": airlines[k],
                        "Source": sources[i],
                        "Destination": destinations[i],
                        "Duration": duration[k],
                        "Total stops": total_stops[k],
                        "Price": prices[k],
                        "Date": current_date,
                    }
                )

        df = pd.DataFrame(
            data, columns=column_names
        )  # Convert list of dictionaries to dataframe
        df = df.replace("\n", "", regex=True)
        df = df.reset_index(drop=True)

        file_name = f"{sources[i]}_{destinations[i]}.csv"
        if not os.path.exists(file_name) or not os.path.isfile(file_name):
            try:
                df.to_csv(file_name, index=False)
                print(
                    f"Data for {sources[i]} => {destinations[i]} saved as {file_name}"
                )
            except PermissionError:
                print(f"Permission denied: {file_name}")
        else:
            print(f"File already exists: {file_name}")

    driver.quit()


if __name__ == "__main__":
    main()
