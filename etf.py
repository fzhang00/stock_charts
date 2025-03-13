import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

url = "https://etf.com/etfanalytics/etf-fund-flows-tool-result?tickers=xly%2C&startDate=2023-01-01&endDate=2024-05-09&frequency=WEEKLY"

# Set up Selenium webdriver
driver = webdriver.Chrome()
driver.get(url)

# Wait for 1 second for the webpage to load
time.sleep(1)

# Find element by XPath
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//table[@id='fund-flow-result-output-table']/thead/tr/th/span"))
)

# Do something with the element
print(element.text)

# Close the webdriver
driver.quit()
