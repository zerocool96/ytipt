import argparse
import asyncio
import json
import logging
from urllib.parse import urlparse, urljoin

from playwright.async_api import async_playwright

logging.basicConfig(
    format="%(levelname)s::%(asctime)s - %(message)s", level=logging.INFO
)
BASE_URL = "https://tamilultra.in"


async def scrape_tv_channels(page):
    # ... (unchanged)

    # Then, navigate to each channel's stream page and capture the M3U8 URLs
    for title, _, stream_page_url in channel_info_list:
        # ... (unchanged)

        # Query for player option elements and click to load M3U8 URL
        player_option_elements = await page.query_selector_all(
            "#playeroptionsul > li.dooplay_player_option"
        )
        for player_option_element in player_option_elements:
            # ... (unchanged)

            # Write M3U8 URL to a text file
            with open("m3u8_urls.txt", "a") as m3u8_file:
                m3u8_file.write(f"{title} - {index}: {m3u8_url}\n")

        logging.info("Scraped %s", title)

    return []


async def scrape_category(category_url, page):
    # ... (unchanged)


async def scrape_all_categories():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()

        # ... (unchanged)

        # Scrape channels from each category
        for category_url in category_urls:
            logging.info("Scraping %s", category_url)
            await scrape_category(category_url, page)

        await browser.close()
        logging.info("Done scraping TamilUltra. M3U8 URLs saved to m3u8_urls.txt")


def main(is_scraping: bool = True):
    if is_scraping:
        asyncio.run(scrape_all_categories())
        return

    logging.warning("Data posting to MediaFusion is disabled in this mode.")
    logging.info("M3U8 URLs can be found in m3u8_urls.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape TamilUltra Live TV")
    parser.add_argument(
        "--no-scrape",
        action="store_true",
        help="Don't scrape TamilUltra. Use this option to add the data to MediaFusion",
    )
    args = parser.parse_args()
    main(not args.no_scrape)
