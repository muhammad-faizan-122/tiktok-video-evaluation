from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
import random


def create_browser_options():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )
    return options


def open_url(url):
    browser = webdriver.Chrome(options=create_browser_options())
    browser.get(url)
    return browser


def get_html_soup(browser):
    WebDriverWait(browser, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    html_content = browser.page_source
    return BeautifulSoup(html_content, "html.parser")


def scroll_down_and_extract_links(browser, max_links=100):
    """
    Continuously scrolls down the page and extracts links until the specified number of links is reached.

    Args:
        browser (webdriver): The browser instance to operate on.
        max_links (int): Maximum number of unique links to collect before stopping.

    Returns:
        list: A list of collected video links, up to the max_links specified.
    """
    links_collected = []
    last_height = browser.execute_script("return document.body.scrollHeight")

    while len(links_collected) < max_links:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Allow time for the page to load and new content to appear

        # Extract and collect links
        soup = BeautifulSoup(browser.page_source, "html.parser")
        current_links = [
            a["href"]
            for a in soup.find_all("a", href=True)
            if "tiktok.com" in a["href"]
        ]
        new_links = set(current_links) - set(links_collected)
        links_collected.extend(new_links)

        # Check if enough links have been collected
        if len(links_collected) >= max_links:
            break

        # Check if the end of the page has been reached
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Wait longer before trying to scroll again to give more time for new content to load
            time.sleep(10)
        last_height = new_height

    return list(links_collected)[:max_links]


def extract_videos_links(soup):
    videos_section = soup.find(
        "div", class_="css-1qb12g8-DivThreeColumnContainer eegew6e2"
    )
    return (
        [
            a["href"]
            for a in videos_section.find_all("a", href=True)
            if "tiktok.com" in a["href"]
        ]
        if videos_section
        else []
    )


def download_tiktok_videos(url):
    driver = open_url(url)
    time.sleep(30)  # Time for manual CAPTCHA solving
    video_links = scroll_down_and_extract_links(driver)
    driver.quit()  # Close the browser after links are collected
    print(f"Collected {len(video_links)} video links.")
    # Additional logic to download videos can be added here
