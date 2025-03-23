import hydra
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.schemas.scraper_schema import WebScraper

#

@hydra.main(version_base=None, config_path="../conf", config_name="scrapping")
def get_books(cfg: WebScraper) -> None:
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    # Add user agent from config
    options.add_argument(f"user-agent={cfg.settings.headers['User-Agent']}")
    # Create a new driver instance with options
    driver = webdriver.Chrome(options=options)
    try:
        # Open books
        driver.get(cfg.settings.urls["books"])

        # Wait for the page to load and for elements to be present
        wait = WebDriverWait(driver, 180)

        # Find all product cards
        cells = wait.until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "product-card")
            )
        )

        print(f"Found {len(cells)} product cells")

        # Process each cell
        for index, cell in enumerate(cells, 1):
            print(f"\n{'=' * 50}")
            print(f"Product {index}:")
            print(f"{'=' * 50}")

            try:
                # Get product title
                title_element = cell.find_element(
                    By.CLASS_NAME, "product-card-module_product-title_16xh8"
                )
                title = (
                    title_element.text if title_element else "No title found"
                )

                # Get author name
                author_element = cell.find_element(By.CLASS_NAME, "authors")
                author = (
                    author_element.text
                    if author_element
                    else "No author found"
                )

                # Get current price
                price_element = cell.find_element(
                    By.CLASS_NAME,
                    "accessible-text-module_accessible-text_11WAe",
                )
                current_price = (
                    price_element.text if price_element else "No price found"
                )

                # Get list price (if available)
                try:
                    list_price_element = cell.find_element(
                        By.CLASS_NAME,
                        "product-card-price-module_list-price_om_3Y",
                    )
                    list_price = (
                        list_price_element.text
                        if list_price_element
                        else "No list price"
                    )
                except:
                    list_price = "No list price"

                # Get discount percentage (if available)
                try:
                    discount_element = cell.find_element(
                        By.CLASS_NAME, "badge.saving"
                    )
                    discount = (
                        discount_element.text
                        if discount_element
                        else "No discount"
                    )
                except:
                    discount = "No discount"

                # Get rating and review count
                try:
                    rating_element = cell.find_element(
                        By.CLASS_NAME, "rating-module_rating_1rLjy"
                    )
                    rating = rating_element.find_element(
                        By.CLASS_NAME, "score"
                    ).text
                    review_count = rating_element.find_element(
                        By.CLASS_NAME, "rating-module_review-count_3g6zO"
                    ).text
                except:
                    rating = "No rating"
                    review_count = "No reviews"

                # Get stock status
                try:
                    stock_status = cell.find_element(
                        By.CLASS_NAME, "stock-availability-status"
                    ).text

                    # Get stock locations
                    stock_pills = cell.find_elements(
                        By.CLASS_NAME, "stock-pill-text"
                    )
                    stock_locations = [pill.text for pill in stock_pills]
                except:
                    stock_status = "Stock status unknown"
                    stock_locations = []

                print(f"Title: {title}")
                print(f"Author: {author}")
                print(f"Current Price: {current_price}")
                print(f"List Price: {list_price}")
                print(f"Discount: {discount}")
                print(f"Rating: {rating}")
                print(f"Reviews: {review_count}")
                print(f"Stock Status: {stock_status}")
                print(f"Available at: {', '.join(stock_locations)}")

            except Exception as e:
                print(f"Error extracting data: {str(e)}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        # Close the browser
        driver.quit()
