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
    # Scrape channel metadata
    channel_elements = await page.query_selector_all("article.item.movies")

    # Then, navigate to each channel's stream page and capture the M3U8 URLs
    for channel_element in channel_elements:
        title_element = await channel_element.query_selector("h3 > a")
        title = (
            (await title_element.text_content())
            .replace("\u2013", "-")
            .split("-")[0]
            .strip()
            .title()
            if title_element
            else "No Title"
        )

        # Navigate to the stream page
        stream_page_link_element = await channel_element.query_selector(".poster > a")
        stream_page_url = (
            await stream_page_link_element.get_attribute("href")
            if stream_page_link_element
            else "No Stream Page URL"
        )
        await page.goto(stream_page_url)

        m3u8_url_data = []

        # Query for player option elements and click to load M3U8 URL
        player_option_elements = await page.query_selector_all(
            "#playeroptionsul > li.dooplay_player_option"
        )
        for index, player_option_element in enumerate(player_option_elements, 1):
            # Click the player option element
            await player_option_element.click()
            # Wait for the iframe to load and get its 'src' attribute
            iframe_element = await page.wait_for_selector("iframe.metaframe.rptss")
            iframe_src = await iframe_element.get_attribute("src")
            m3u8_url_part = iframe_src.replace("/player.php?", "")
            # Check if iframe_src is a valid URL
            parsed_src = urlparse(m3u8_url_part)
            behavior_hints = {}
            if parsed_src.scheme and parsed_src.netloc:
                # If it's a valid URL, use it directly
                m3u8_url = m3u8_url_part
                if "jio.tamilultra.in" in m3u8_url:
                    behavior_hints = {
                        "notWebReady": True,
                        "proxyHeaders": {
                            "request": {
                                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                                "Referer": BASE_URL + "/",
                            }
                        },
                    }
            else:
                # Otherwise, join with the BASE_URL
                m3u8_url = urljoin(BASE_URL, m3u8_url_part)
                behavior_hints = {
                    "is_redirect": True,
                    "proxyHeaders": {
                        "request": {
                            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                            "Referer": urljoin(BASE_URL, iframe_src),
                        }
                    },
                }
            m3u8_url_data.append((m3u8_url, behavior_hints))

        # Save M3U8 URLs to a text file
        with open("m3u8_urls.txt", "a") as m3u8_file:
            for m3u8_url, behavior_hints in m3u8_url_data:
                m3u8_file.write(f"{title} - {index}: {m3u8_url}\n")

        logging.info("Scraped %s", title)

    return []


async def scrape_category(category_url, page):
    # Navigate to the category page
    await page.goto(category_url)

    # Scrape channels from the current page
    channels_data = await scrape_tv_channels(page)

    # Try to find a pagination control and collect all page URLs
    pagination_links = await page.query_selector_all("div.pagination a.inactive")
    page_urls = [category_url]  # Include the first page
    for link in pagination_links:
        page_url = await link.get_attribute("href")
        if page_url:
            page_urls.append(page_url)

    logging.info("found %d pages", len(page_urls))

    # Iterate over each page URL and scrape channels
    for page_url in page_urls:
        if page_url != category_url:  # We already scraped the first page
            await page.goto(page_url)
            # Scrape channels from this page
            channels_data.extend(await scrape_tv_channels(page))

    return channels_data


async def scrape_all_categories():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()

        # Extract category URLs
        await page.goto(BASE_URL)
        category_elements = await page.query_selector_all(".main-header a")
        category_urls = [
            urljoin(BASE_URL, await element.get_attribute("href"))
            for element in category_elements
        ]

        # Scrape channels from each category
        all_channels_data = []
        for category_url in category_urls:
            logging.info("Scraping %s", category_url)
            all_channels_data.extend(await scrape_category(category_url, page))

        await browser.close()

        # remove duplicates
        unique_channels = {channel["title"]: channel for channel in all_channels_data}
        unique_channels_data = list(unique_channels.values())

        logging.info("found %d channels", len(unique_channels_data))

        # Uncomment the following lines if you want to save the channel data to a JSON file
        # with open("tamilultra.json", "w") as file:
        #     json.dump({"channels": unique_channels_data}, file, indent=4)

        logging.info("Done scraping TamilUltra. M3U8 URLs saved to m3u8_urls.txt")


def main(is_scraping: bool = True):
    if is_scraping:
        asyncio.run(scrape_all_categories())
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape TU Live TV")
    parser.add_argument(
        "--no-scrape",
        action="store_true",
        help="Don't scrape Tu",
    )
    args = parser.parse_args()
    main(not args.no_scrape)
