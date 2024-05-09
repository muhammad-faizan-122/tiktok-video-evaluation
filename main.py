from src.scraper.tiktok_scraping import download_tiktok_videos
from src.video_quality_eval import assess_videos_quality
from constants.scraper.constants import TIKTOK_URL


if __name__ == "__main__":
    download_tiktok_videos(TIKTOK_URL)
    assess_videos_quality()
