

# Selectors I found
## Elements holding the key data
<li> Title → inside
<div class="category-description"><h2><a href="...">TITLE TEXT</a></h2></div>
So the selector is div.category-description h2 a.

Image → inside


<div class="category-image"><figure><img ...></figure></div>
Selector: div.category-image img.
Note: the real image URL is in data-src (lazy‑loaded), while src may be a placeholder.

Category → not printed per card. It’s implied by the section you’re scraping (/entertainment). So you can safely hardcode "मनोरञ्जन" for all records or use it globally for the page.

<li>Author → inside
<div class="author-name"><p><a href="...">AUTHOR NAME</a></p></div>
Selector: div.author-name a.
Some cards genuinely lack this block, so you must handle None.

Unusual loading behavior
Lazy images: Many <img> tags use data-src for the real image and only load a placeholder in src. Always check data-src first, then fall back to src.

Missing authors: Not every article card has an author-name block. Your scraper should return "author": None when it’s absent.

Category field: The category isn’t repeated inside each card; it’s implied by the page section. That’s why hardcoding "मनोरञ्जन" is correct.


# What I asked the AI
<ol> 
<li> 
do we need to maintain hierachy?
import json
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

BASE_URL = "https://ekantipur.com"
ENTERTAINMENT_URL = f"{BASE_URL}/entertainment"
SELECTORS = {
    # container for one article card in the entertainment feed
    "article_card": "div.category", 
    # inside a card
    "title": "h2 a",                
    "image": "img",                
    "author": "span.author",        
}
</li>

2.
how could i extract url?
<div class="category-image"><a href="https://ekantipur.com/entertainment/2026/08/03/ariana-grande-announces-retirement-from-public-life-50-39.html"><figure><img class="loaded" alt="Ariana Grande announces withdrawal from public life" src="https://assets-cdn-api.ekantipur.com/thumb.php?src=https://assets-cdn.ekantipur.com/uploads/source/news/kantipur/2026/third-party/ariana-grande-arrives-at-the-62nd-annual-grammy-awards-at-news-photo-0382026060515-1000x0.jpg&amp;w=701&amp;h=0"></figure></a></div>


3.
i can't get those 5 records 
<div class="category"><div class="category-inner-wrapper"><div class="category-description"><h2><a href="https://ekantipur.com/entertainment/2026/07/30/oscar-winner-gerard-leto-accused-of-sexual-misconduct-by-four-women-02-49.html">ओस्कार विजेता जेराड लेटोविरुद्ध चार महिलाद्वारा यौन दुर्व्यवहारको आरोप</a></h2><div class="author-name"><p><a href="https://ekantipur.com/author/author-14301">कान्तिपुर संवाददाता</a></p> </div><p>...</p><div class="time-wrapper"><span>5 MINS READ</span></div></div><div class="category-image">...</div></div></div>

</ol>
# One thing it got wrong
Gemini originally suggested using the selector

{"article_card": "div.category-main-wrapper"}
for the entertainment feed.

### How I noticed
When I ran the scraper, page.query_selector_all("div.category-main-wrapper") only returned one element instead of multiple article cards. That was the red flag — I expected at least 5+ articles but only got one record in my JSON output. Inspecting the page with DevTools showed that the repeating unit for each article is actually ("div.category"), not div.category-main-wrapper.

### What I changed
I updated the selector to: {"article_card": "div.category"}
After this change, query_selector_all returned the full list of article cards, and slicing [:5] correctly gave me the top 5 records. I also adjusted the child selectors accordingly (div.category-description h2 a for the title, div.category-image img for the image, and div.author-name a for the author).

