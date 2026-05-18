from playwright.sync_api import sync_playwright
import json


BASE_URL = "https://ekantipur.com"
ENTERTAINMENT_URL = "https://ekantipur.com/entertainment"


def get_text(element):
    """
    Safely extract text from element.
    """

    try:
        if element:
            text = element.text_content()

            if text:
                return text.strip()

    except Exception:
        pass

    return None


def get_attr(element, attribute):
    """
    Safely extract attribute value.
    """

    try:
        if element:
            value = element.get_attribute(attribute)

            if value:
                return value.strip()

    except Exception:
        pass

    return None


def close_popup(page):
    """
    Close popup advertisements if present.
    """

    try:
        page.keyboard.press("Escape")

        page.wait_for_timeout(1000)

    except Exception:
        pass


def extract_entertainment_news(page):
    """
    Extract top 5 entertainment news articles.
    """

    print("Opening entertainment page...")

    page.goto(ENTERTAINMENT_URL)

    page.wait_for_load_state("networkidle")

    page.wait_for_timeout(3000)

    close_popup(page)

    news_items = []

    # Get article cards
    articles = page.locator("article")

    count = articles.count()

    print(f"Found {count} article elements")

    extracted = 0

    for i in range(count):

        if extracted >= 5:
            break

        try:
            article = articles.nth(i)

            title = get_text(
                article.locator("h2").first
            )

            image_url = get_attr(
                article.locator("img").first,
                "src"
            )

            category = "मनोरञ्जन"

            author = get_text(
                article.locator(".author").first
            )

            # Skip empty cards
            if not title:
                continue

            news_data = {
                "title": title,
                "image_url": image_url,
                "category": category,
                "author": author
            }

            news_items.append(news_data)

            extracted += 1

            print(f"Extracted article {extracted}")

        except Exception as e:
            print(f"Error: {e}")

    return news_items


def extract_cartoon(page):
    """
    Extract cartoon of the day.
    """

    print("Opening homepage for cartoon section...")

    page.goto(BASE_URL)

    page.wait_for_load_state("networkidle")

    page.wait_for_timeout(3000)

    close_popup(page)

    cartoon_data = {
        "title": None,
        "image_url": None,
        "author": None
    }

    sections = page.locator("section")

    section_count = sections.count()

    for i in range(section_count):

        try:
            section = sections.nth(i)

            text = section.text_content()

            if text and "व्यंग्यचित्र" in text:

                cartoon_data["title"] = get_text(
                    section.locator("h2").first
                )

                cartoon_data["image_url"] = get_attr(
                    section.locator("img").first,
                    "src"
                )

                cartoon_data["author"] = get_text(
                    section.locator(".author").first
                )

                print("Cartoon section extracted")

                break

        except Exception:
            pass

    return cartoon_data


def save_output(data):
    """
    Save data to output.json
    """

    with open(
        "output.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("output.json saved successfully")


def main():

    final_data = {
        "entertainment_news": [],
        "cartoon_of_the_day": {}
    }

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        # Entertainment news
        final_data["entertainment_news"] = (
            extract_entertainment_news(page)
        )

        # Cartoon section
        final_data["cartoon_of_the_day"] = (
            extract_cartoon(page)
        )

        # Save JSON
        save_output(final_data)

        browser.close()

        print("Scraping completed successfully")


if __name__ == "__main__":
    main()