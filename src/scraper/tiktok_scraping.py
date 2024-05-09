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
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
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
    browser = webdriver.Chrome(options=create_browser_options())
    browser.get(url)
    return browser


def get_html_soup(browser):
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    browser.quit()
    return soup


def scroll_down(browser):
    scroll_pause_time = 30
    screen_height = browser.execute_script("return window.screen.height;")
    i = 1
    while True:
        browser.execute_script(
            "window.scrollTo(0, {screen_height}*{i});".format(
                screen_height=screen_height, i=i
            )
        )
        i += 1
        time.sleep(scroll_pause_time)
        scroll_height = browser.execute_script("return document.body.scrollHeight;")
        if (screen_height) * i > scroll_height:
            break


def get_videos_section_html(soup):
    videos_section_divs = soup.find(
        "div", {"class": "css-1qb12g8-DivThreeColumnContainer eegew6e2"}
    )
    return videos_section_divs


def extract_videos_links(videos_section_divs):
    videos_links = []
    if videos_section_divs:
        videos_divs = videos_section_divs.find_all(
            "div", {"class": "css-x6y88p-DivItemContainerV2 e19c29qe8"}
        )
        for video_div in videos_divs:
            video_link = video_div.find(
                "a", href=lambda href: href and "tiktok.com" in href
            )["href"]
            videos_links.append(video_link)
    return videos_links


def calcuate_downloaded_videos():
    total_videos = len(os.listdir(DOWNLOADED_VIDS_DIR))
    return total_videos


def wait_for_download(num_vids_before):
    """Wait for download tiktok completely"""
    while True:
        time.sleep(1)  # Check every second
        current_vids = calcuate_downloaded_videos()
        print("current_vids: ", current_vids)
        files = [f.endswith(".mp4") for f in os.listdir(DOWNLOADED_VIDS_DIR)]
        if current_vids > num_vids_before and all(files):
            print(f"Video downloaded successfully! Total videos: {current_vids}")
            break


def download_video(url):
    num_vids_before = calcuate_downloaded_videos()
    adblock_path = "src/scraper/adblocker.crx"

    options = Options()
    options.add_extension(adblock_path)

    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )
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
    """Adding Random delay to mimic the human behaviour"""
    # Random float between 5 and 10 seconds
    delay = random.uniform(5, 10)
    time.sleep(delay)
    print("Resuming operation.")


def scrape_tiktok_video_links(url):
    driver = open_url(url)

    # Wait 30 seconds to solve CAPTCHA manually
    time.sleep(30)

    scroll_down(driver)

    # Get HTML soup after scrolling
    html_soup = get_html_soup(driver)

    # Continue with scraping
    videos_section_divs = get_videos_section_html(html_soup)
    videos_links = extract_videos_links(videos_section_divs)

    return videos_links


def download_videos(videos_links):
    for video_num, video_link in enumerate(videos_links):
        """TODO: REMOVE THIS LINE AFTER TESTING"""
        if video_num > 10:
            break
        print(video_link)
        download_video(video_link)
        random_delay()


def download_tiktok_videos(url):
    videos_links = scrape_tiktok_video_links(url)
    for video_link in videos_links:
        print(f"Downloading video from {video_link}")
        download_video(video_link)
        random_delay()
