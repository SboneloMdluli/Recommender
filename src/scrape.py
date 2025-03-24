import logging

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from src.config.app_settings import settings
from src.config.book_config import book_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def setup_driver() -> webdriver.Chrome:
    """Set up and configure the Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument(f"user-agent={settings.headers.user_agent}")
    return webdriver.Chrome(options=options)


def extract_element_text(element: WebElement | None, default: str = "Not found") -> str:
    """Extract text from element with fallback."""
    return element.text if element else default


def get_product_details(
        cell: WebElement,
        book_settings: dict,
) -> dict | None:
    """Extract product details from a cell."""
    details = {}

    try:
        title_element = cell.find_element(
            By.CLASS_NAME, book_settings.elements["title"],
        )
        details["title"] = extract_element_text(title_element, "No title found")

        author_element = cell.find_element(
            By.CLASS_NAME, book_settings.elements["author"],
        )
        details["author"] = extract_element_text(author_element, "No author found")

        price_element = cell.find_element(
            By.CLASS_NAME, book_settings.elements["current_price"],
        )
        details["current_price"] = extract_element_text(
            price_element, "No price found",
        )

        try:
            list_price_element = cell.find_element(
                By.CLASS_NAME, book_settings.elements["list_price"],
            )
            details["list_price"] = extract_element_text(
                list_price_element, "No list price",
            )
        except NoSuchElementException:
            details["list_price"] = "No list price"

        try:
            discount_element = cell.find_element(
                By.CLASS_NAME, book_settings.elements["discount"],
            )
            details["discount"] = extract_element_text(
                discount_element, "No discount",
            )
        except NoSuchElementException:
            details["discount"] = "No discount"

        # Get rating and review count
        try:
            rating_element = cell.find_element(
                By.CLASS_NAME, book_settings.elements["container"],
            )
            details["rating"] = rating_element.find_element(
                By.CLASS_NAME, book_settings.elements["score"],
            ).text
            details["review_count"] = rating_element.find_element(
                By.CLASS_NAME, book_settings.elements["review_count"],
            ).text
        except NoSuchElementException:
            details["rating"] = "No rating"
            details["review_count"] = "No reviews"

        # Get stock information
        try:
            details["stock_status"] = cell.find_element(
                By.CLASS_NAME, book_settings.elements["status_availability"],
            ).text
            stock_pills = cell.find_elements(
                By.CLASS_NAME, book_settings.elements["locations"],
            )
            details["stock_locations"] = [pill.text for pill in stock_pills]
        except NoSuchElementException:
            details["stock_status"] = "Stock status unknown"
            details["stock_locations"] = []

    except NoSuchElementException as e:
        logger.exception("Failed to extract product details", exc_info=e)
        return None

    return details


def get_books() -> None:
    """Scrape book information from Takealot."""
    driver = None
    try:
        driver = setup_driver()
        driver.get(book_settings.urls["books"])

        wait = WebDriverWait(driver, 180)
        cells = wait.until(
            ec.presence_of_all_elements_located(
                (By.CLASS_NAME, book_settings.elements["product_card"]),
            ),
        )

        logger.info("Found %d product cells", len(cells))

        for index, cell in enumerate(cells, 1):
            logger.info("Processing product %d", index)
            details = get_product_details(cell, book_settings)

            if details:
                logger.info("Product Details:")
                for key, value in details.items():
                    logger.info("%s: %s", key, value)
                logger.info("-" * 50)

    except TimeoutException:
        logger.exception("Timed out waiting for page to load")
    except WebDriverException as e:
        logger.exception("WebDriver error occurred", exc_info=e)
    finally:
        if driver:
            driver.quit()
