"""
Ekantipur scraper — Task 1 (entertainment news) + Task 2 (cartoon of the day)


Workflow this script assumes (matches the four-step loop in the guide):
  1. Inspect  -> you fill in SELECTORS below from real DevTools
  2. Instruct -> hand the real HTML snippet + these notes to your agent,
                 one function at a time, and paste its output in place of
                 the stub functions
  3. Review   -> read the diff against the checklist in the Appendix (§04)
  4. Verify   -> run it, open output.json next to the live page, eyeball it
"""


import json
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright



# Base url 
BASE_URL = "https://ekantipur.com"


# locating and retrieving the url for entertainment section and cartoon sections.

ENTERTAINMENT_URL = f"{BASE_URL}/entertainment"
CARTOON_URL = f"{BASE_URL}/cartoon"




# ---------------------------------------------------------------------------
# (DEVTOOLS): replace every value here with what you actually find.
# Open ekantipur.com/entertainment, Ctrl+Shift+C, click an article card.
# ---------------------------------------------------------------------------
SELECTORS = {
    # container for one article card in the entertainment feed
    "article_card": "div.category",  # confirm real class name
    # inside a card
    "title": "div.category-description h2 a",               
    "image": "div.category-image a figure img", # couldn't get the image link whithout using hierarchy 
    "category"  :"div.category-name p a" ,            
    "author": "div.author-name p a",        # — confirm this exists; some cards
      # — confirm this exists; some cards
                                     # have none, per the appendix notes
    # cartoon of the day section (homepage or /cartoon — confirm which page
    # actually has "today's" cartoon vs. an archive list)
    "cartoon_section": "div.col-lg-4",      
    "cartoon_image": "div.cartoon-image figure a img",        
    "cartoon_title": "div.cartoon-description p",        
    "cartoon_author": "div.cartoon-description p",      
}


def extract_entertainment_articles(page, limit: int = 5) -> list[dict]:
    """
    Extract the top `limit` article cards from the entertainment section.

    Returns a list of dicts: {title, image_url, category, author}.
    author is None (not omitted) when the card has no author element —
    per the appendix, some cards genuinely lack one.
    """
    try: 
        page.wait_for_selector(SELECTORS["article_card"])
        cards = page.query_selector_all(SELECTORS["article_card"])[:limit]

        results = []
        # Category Extraction globally for the page rather then the card  because each card is within entertainment section.
        category_el = page.query_selector(SELECTORS["category"])
        category = category_el.text_content().strip() if category_el else None
    
        for card in cards:
            title_el = card.query_selector(SELECTORS["title"])
            title = title_el.text_content().strip() if title_el else None

            img_el = card.query_selector(SELECTORS["image"])
            image_url = None
            if img_el:
            # Prefer data-src: lazy-loaded images keep a placeholder in src.
                raw_src = img_el.get_attribute("data-src") or img_el.get_attribute("src")
                if raw_src:
                    image_url = urljoin(page.url, raw_src)

        
        #    Author extraction
            author_el = card.query_selector(SELECTORS["author"])
            author = author_el.text_content().strip() if author_el else None
       
            print(f"title: {title}\nimage_url: {image_url}\ncategory: {category}\nauthor: {author}")
            results.append({
                "title": title,
                "image_url": image_url,
                "category": category,  
                "author": author,
            })

        return results
    except Exception as e:
        print(f"Error extracting entertainment articles: {e}")
        return []


def extract_cartoon_of_the_day(page) -> dict:
        """
        Extract the Cartoon of the Day (ग्व्यँय त्र) section.
        Returns {title, image_url, author}.
        """
        # (DEVTOOLS): confirm this section lives on the homepage vs a
        # dedicated /cartoon page, and which entry actually represents "today's"
        # cartoon vs. an archive grid (homepage showed what looked like a
        # scrolling list of past cartoons, e.g. "गजब छ बा" repeated — the FIRST
        # one is presumably "today's" but verify against the live page).
    
        section = page.query_selector(SELECTORS["cartoon_section"])
        if section is None:
            raise RuntimeError(
                "Cartoon section selector did not match anything — "
                "re-check SELECTORS['cartoon_section'] in DevTools."
            )

        img_el = section.query_selector(SELECTORS["cartoon_image"])
        image_url = None
        if img_el:
            # checking lazy loading using 'data-src'
            raw_src = img_el.get_attribute("data-src") or img_el.get_attribute("src")  
            if raw_src:
                image_url = urljoin(page.url, raw_src)

        title_el = section.query_selector(SELECTORS["cartoon_title"])
        title = title_el.text_content().strip().split('-')[0].strip() if title_el else None

        author_el = section.query_selector(SELECTORS["cartoon_author"])
        author = author_el.text_content().strip().split('-')[1].strip() if author_el else None

        #Testing cartoon extraction 
        print(f"\ntitle: {title}\nimage_url: {image_url}\nauthor: {author}")

        return {"title": title, "image_url": image_url, "author": author}


def main():
    with sync_playwright() as p:
        # headless=False while developing so you can watch it work;
        # switch to True for your final submission run.
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(ENTERTAINMENT_URL)
        page.wait_for_load_state("networkidle")
        entertainment_news = extract_entertainment_articles(page, limit=5)
        browser.close()

        # Opening browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # navigate to wherever the cartoon actually lives once you've
        # confirmed it in DevTools — may or may not be the same page.
        page.goto(CARTOON_URL)
        page.wait_for_load_state("networkidle")
        
        cartoon_of_the_day = extract_cartoon_of_the_day(page) #calling the funtion for extraction

        browser.close() # closed the browser

    output = {
        "entertainment_news": entertainment_news,
        "cartoon_of_the_day": cartoon_of_the_day
    }

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nWrote output.json with {len(entertainment_news)} articles + 1 cartoon.")


if __name__ == "__main__":
    main()
