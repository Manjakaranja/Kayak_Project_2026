import logging
from pathlib import Path

import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess


BASE_DIR = Path(__file__).resolve().parents[2]

# TOP 5 destinations generated previously
TOP_DESTINATIONS_PATH = (
    BASE_DIR
    / "data"
    / "outputs"
    / "top_5_destinations.csv"
)

# Booking raw output
OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "booking"
    / "booking_data.csv"
)


# Load ONLY top 5 cities


def load_top_destinations(path: Path) -> list[str]:

    df = pd.read_csv(path)

    cities = (
        df["city"]
        .dropna()
        .unique()
        .tolist()
    )

    print(f"Top destinations loaded: {cities}")

    return cities


class BookingSpider(scrapy.Spider):

    name = "booking"

    def __init__(
        self,
        cities: list[str],
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.cities = cities

    async def start(self):

        for city in self.cities:

            url = (
                "https://www.booking.com/"
                f"searchresults.html?ss={city}"
            )

            yield scrapy.Request(
                url=url,

                callback=self.parse,

                errback=self.handle_error,

                meta={
                    "city": city,

                    "playwright": True,

                    "playwright_include_page": True,

                    "playwright_page_goto_kwargs": {
                        "wait_until": "domcontentloaded",
                        "timeout": 20000,
                    },

                    "playwright_context_kwargs": {
                        "extra_http_headers": {
                            "Accept-Language":
                            "fr-FR,fr;q=0.9",
                        }
                    },
                },

                dont_filter=True,
            )

    async def parse(self, response):

        page = response.meta.get(
            "playwright_page"
        )

        city = response.meta.get("city")

        try:

            await page.wait_for_selector(
                "a[data-testid='title-link']",
                timeout=15000,
            )

            content = await page.content()

            response = response.replace(
                body=content
            )

            hotel_links = response.css(
                "a[data-testid='title-link']::attr(href)"
            ).getall()

            # keep only first 25
            hotel_links = hotel_links[:25]

            print(
                f"-> {len(hotel_links)} "
                f"hôtels trouvés pour {city}"
            )

            for link in hotel_links:

                yield scrapy.Request(
                    url=link,

                    callback=self.parse_hotel_details,

                    errback=self.handle_error,

                    meta={
                        "city": city,

                        "playwright": True,

                        "playwright_include_page": True,

                        "playwright_page_goto_kwargs": {
                            "wait_until":
                            "domcontentloaded",

                            "timeout": 20000,
                        },
                    },

                    dont_filter=True,
                )

        except Exception as e:

            self.logger.warning(
                f"Aucun hôtel exploitable "
                f"pour {city} : {e}"
            )

        finally:

            if page:
                await page.close()

    async def parse_hotel_details(
        self,
        response
    ):

        page = response.meta.get(
            "playwright_page"
        )

        city = response.meta.get("city")

        try:

            content = await page.content()

            response = response.replace(
                body=content
            )

            # Hotel name
            name = response.css(
                "h2[class='ddb12f4f86 pp-header__title']::text"
            ).get()

            if not name:

                name = response.css(
                    "h2.pp-header__title::text"
                ).get()

            # Rating
            rating = response.css(
                "div[class='f63b14ab7a dff2e52086']::text"
            ).get()

            if not rating:

                rating = response.css(
                    "div[data-testid='review-score-right-component']::text"
                ).get()

            # Description
            description = response.css(
                "p[data-testid='property-description']::text"
            ).get()

            # Address
            address = response.css(
                "div[class='b99b6ef58f cb4b7a25d9 b06461926f']::text"
            ).get()

            if not address:

                address = response.css(
                    "span[data-node_tt_id='location_score_tooltip']::text"
                ).get()

            # Coordinates
            coords = response.css(
                'div[data-testid="map-entry-point-desktop-wrapper"]::attr(data-atlas-latlng)'
            ).get()

            if not coords:

                coords = response.css(
                    '[data-atlas-latlng]::attr(data-atlas-latlng)'
                ).get()

            hotel_data = {

                "hotel_name":
                name.strip() if name else None,

                "rating":
                rating.strip() if rating else None,

                "description":
                description.strip()
                if description else None,

                "address":
                address.strip()
                if address else None,

                "url":
                response.url,

                "city":
                city,

                "latitude":
                None,

                "longitude":
                None,
            }

            if coords and "," in coords:

                lat, lng = coords.split(
                    ",",
                    1
                )

                hotel_data["latitude"] = (
                    lat.strip()
                )

                hotel_data["longitude"] = (
                    lng.strip()
                )

            yield hotel_data

        except Exception as e:

            self.logger.warning(
                f"Erreur parsing hôtel "
                f"{response.url} "
                f"({city}) : {e}"
            )

        finally:

            if page:
                await page.close()

    async def handle_error(self, failure):

        request = failure.request

        page = request.meta.get(
            "playwright_page"
        )

        city = request.meta.get("city")

        self.logger.warning(
            f"Erreur téléchargement "
            f"pour {city} - "
            f"{request.url}: {failure.value}"
        )

        if page:
            await page.close()


def main():

    cities = load_top_destinations(
        TOP_DESTINATIONS_PATH
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.unlink(
        missing_ok=True
    )

    process = CrawlerProcess(
        settings={

            "USER_AGENT":
            (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0.0.0 "
                "Safari/537.36"
            ),

            "LOG_LEVEL":
            logging.INFO,

            "DOWNLOAD_HANDLERS": {
                "http":
                (
                    "scrapy_playwright.handler."
                    "ScrapyPlaywrightDownloadHandler"
                ),

                "https":
                (
                    "scrapy_playwright.handler."
                    "ScrapyPlaywrightDownloadHandler"
                ),
            },

            "PLAYWRIGHT_BROWSER_TYPE":
            "chromium",

            "PLAYWRIGHT_LAUNCH_OPTIONS": {
                "headless": True,
            },

            "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT":
            2,

            "CONCURRENT_REQUESTS":
            1,

            "DOWNLOAD_DELAY":
            4,

            "RANDOMIZE_DOWNLOAD_DELAY":
            True,

            "DOWNLOAD_TIMEOUT":
            20,

            "RETRY_TIMES":
            1,

            "CLOSESPIDER_TIMEOUT":
            1800,

            "TWISTED_REACTOR":
            (
                "twisted.internet."
                "asyncioreactor."
                "AsyncioSelectorReactor"
            ),

            "FEEDS": {
                str(OUTPUT_PATH): {

                    "format": "csv",

                    "encoding": "utf-8",

                    "overwrite": True,
                },
            },
        }
    )

    print(
        f"Booking output file: "
        f"{OUTPUT_PATH}"
    )

    process.crawl(
        BookingSpider,
        cities=cities,
    )

    process.start()


if __name__ == "__main__":
    main()