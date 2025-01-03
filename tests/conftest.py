import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from collections import Counter
import langdetect
import time
import os
import requests
from googletrans import Translator

IMAGE_DIR = "downloaded_images"

@pytest.fixture(params=["chrome", "firefox", "edge"])
def browser(request):
    # Initializing drivers for cross browser testing(Browser names are passed as params)
    browser_name = request.param
    if browser_name.lower() == "chrome":
        service = ChromeService("../drivers/chromedriver.exe")
        browser = webdriver.Chrome(service=service)
    elif browser_name.lower() == "firefox":
        service = FirefoxService("../drivers/geckodriver.exe")
        browser = webdriver.Firefox(service=service)
    elif browser_name.lower() == "edge":
        service = EdgeService("../drivers/msedgedriver.exe")
        browser = webdriver.Edge(service=service)
    else:
        print(f"Unsupported browser: {browser_name}")
        exit
    browser.maximize_window()
    # Visit the website El País, a Spanish news outlet
    browser.get("https://elpais.com/")
    time.sleep(5)
    accept_button = browser.find_element(By.ID, "didomi-notice-agree-button")
    accept_button.click()
    # Validating Website title ti be El País
    assert browser.title == "EL PAÍS: el periódico global"
    yield browser
    browser.quit()

@pytest.fixture
def setup_directory():
    # Setting up the directory for downloading cover images
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
    yield IMAGE_DIR