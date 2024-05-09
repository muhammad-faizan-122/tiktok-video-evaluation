from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from constants.scraper.constants import DOWNLOADED_VIDS_DIR
import time
import os
import random


def create_browser_options():
    """
    Creates and returns browser options for Chrome, pre-configured with various settings to optimize web scraping.
    """

    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )
    return options


def open_url(url):
    """
    Opens the specified URL in a Chrome browser.

    Args:
    url (str): The URL to open.

    Returns:
    webdriver.Chrome: The Chrome browser instance.
    """
    browser = webdriver.Chrome(options=create_browser_options())
    browser.get(url)
    return browser


def get_html_soup(browser):
    """
    Extracts HTML content from the browser page and returns a BeautifulSoup object.

    Args:
    browser (webdriver.Chrome): The Chrome browser instance.

    Returns:
    bs4.BeautifulSoup: The BeautifulSoup object representing the HTML content.
    """
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    browser.quit()
    return soup


def scroll_down(browser):
    """
    Scrolls down the webpage to load additional content dynamically.

    Args:
    browser (webdriver.Chrome): The Chrome browser instance.
    """
    scroll_pause_time = 2
    last_height = browser.execute_script("return document.body.scrollHeight")
    retries = 5  # Number of retries if no new content is loaded

    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)  # Allow time for the page to load
        new_height = browser.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            if retries > 0:
                retries -= 1
                time.sleep(scroll_pause_time)
                # Try scrolling again
                continue
            else:
                # Break the loop if retries are exhausted and no new content is loaded
                break
        else:
            retries = 3  # Reset retries if new content has been loaded
            last_height = new_height


def extract_video_links(videos_section_divs):
    """
    Extracts video links from the given section of HTML content.

    Args:
    videos_section_divs (bs4.element.Tag): The BeautifulSoup Tag representing the section containing video links.

    Returns:
    list: A list of video links.
    """
    if not videos_section_divs:
        return []
    video_links = []
    for video_div in videos_section_divs.find_all(
        "div", class_="css-x6y88p-DivItemContainerV2 e19c29qe8"
    ):
        a_tag = video_div.find("a", href=True)
        if a_tag and "tiktok.com" in a_tag["href"]:
            video_links.append(a_tag["href"])
    return video_links


def calculate_downloaded_videos():
    """
    Calculates the number of videos already downloaded.

    Returns:
    int: The number of downloaded videos.
    """
    try:
        return len([f for f in os.listdir(DOWNLOADED_VIDS_DIR) if f.endswith(".mp4")])
    except Exception as e:
        print(f"Error accessing directory: {e}")
        return 0


def wait_for_download(num_vids_before, max_retries=10):
    """
    Waits for new videos to be downloaded, retrying a specified number of times.

    Args:
    num_vids_before (int): Number of videos before starting the download.
    max_retries (int): Maximum number of retries to wait for the download to complete. Default is 10.
    """
    retries = 0
    while retries < max_retries:
        time.sleep(1)  # Wait for 1 second before checking again
        current_vids = calculate_downloaded_videos()
        print("current_vids: ", current_vids)
        if current_vids > num_vids_before:
            print(f"Video downloaded successfully! Total videos: {current_vids}")
            return
        retries += 1
    print("Reached maximum retries without downloading all videos.")


def download_video(url):
    """
    Downloads a video from the specified URL.

    Args:
    url (str): The URL of the video to download.
    """
    num_vids_before = calculate_downloaded_videos()

    options = create_browser_options()
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": DOWNLOADED_VIDS_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )

    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://ssstik.io/en")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "main_page_text"))
        ).send_keys(url)
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        ).click()
        no_watermark_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "a.pure-button.pure-button-primary.is-center.u-bl.dl-button.download_link.without_watermark.vignette_active.notranslate",
                )
            )
        )
        no_watermark_button.click()
        wait_for_download(num_vids_before)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()


def random_delay():
    """
    Adds a random delay to mimic human behavior.
    """
    # Random float between 5 and 10 seconds
    delay = random.uniform(5, 10)
    time.sleep(delay)
    print("Resuming operation.")
    # Random float between 5 and 10 seconds
    delay = random.uniform(5, 10)
    time.sleep(delay)
    print("Resuming operation.")


def scrape_tiktok_video_links(url):
    """
    Scrapes TikTok video links from the specified URL.

    Args:
    url (str): The URL of the TikTok page.

    Returns:
    list: A list of TikTok video links.
    """
    driver = open_url(url)
    # Wait 30 seconds to solve CAPTCHA manually
    time.sleep(30)
    scroll_down(driver)
    # Get HTML soup after scrolling
    html_soup = get_html_soup(driver)

    # Continue with scraping
    videos_section_divs = html_soup.find(
        "div", {"class": "css-1qb12g8-DivThreeColumnContainer eegew6e2"}
    )
    videos_links = extract_video_links(videos_section_divs)

    return videos_links


def download_tiktok_videos(url):
    """
    Downloads TikTok videos from the specified URL.

    Args:
    url (str): The URL of the TikTok page containing videos to download.
    """
    videos_links = scrape_tiktok_video_links(url)
    for video_link in videos_links:
        print(f"Downloading video from {video_link}")
        download_video(video_link)
        random_delay()
