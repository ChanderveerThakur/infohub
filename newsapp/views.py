import os
import requests
from django.shortcuts import render
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
# fallback placeholder image when API article has no image
PLACEHOLDER_IMAGE = "https://via.placeholder.com/800x450?text=No+Image"

def fetch_news_from_api(query, page_size=50):
    """
    Fetch articles from NewsAPI 'everything' endpoint.
    Returns the JSON list of articles (may be empty).
    """
    if not query:
        query = "technology"

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": page_size,  # max number of articles to retrieve at once (NewsAPI max ~100)
        "language": "en",
        # you can add 'sortBy': 'publishedAt' if you want newest first
        "apiKey": NEWS_API_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("articles", [])
    except Exception:
        # On failure, return empty list (the template shows friendly message)
        return []
    
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='login')
def home(request):
    return render(request, 'newsapp/home.html')


def news_home(request):
    """
    View that accepts:
      - ?query=search-term    (search text)
      - ?show=N               (how many articles to show; default 10)
    It fetches up to max_needed articles from the API and slices to 'show'.
    """
    # read GET params
    query = request.GET.get("query", "").strip()
    try:
        show = int(request.GET.get("show", 10))
    except (TypeError, ValueError):
        show = 10

    # ensure sensible bounds
    if show < 1:
        show = 10
    # NewsAPI allows up to 100 in one request; we cap at 100
    max_to_fetch = min(max(show, 10), 100)

    articles_raw = fetch_news_from_api(query or "technology", page_size=max_to_fetch)

    articles = []
    for a in articles_raw:
        title = a.get("title") or "No title"
        desc = a.get("description") or a.get("content") or "No description available."
        url = a.get("url") or "#"
        img = a.get("urlToImage") or a.get("image") or PLACEHOLDER_IMAGE

        # Normalize the dictionary keys expected by the template
        articles.append({
            "title": title,
            "description": desc,
            "url": url,
            "urlToImage": img,
        })

    # slice to requested count (show)
    visible_articles = articles[:show]

    context = {
        "articles": visible_articles,
        "query": query,
        "show": show,
        "total_available": len(articles),
    }
    return render(request, "news.html", context)
