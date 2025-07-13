import streamlit as st
import feedparser
from data_provider import DataProvider

try:
    from newsapi.newsapi_client import NewsApiClient
except ImportError:
    NewsApiClient = None

class NewsProvider(DataProvider):
    def __init__(self, api_key=None):
        self.api_key = api_key
        if NewsApiClient is None:
            st.warning("NewsAPI client is not available. News features will be limited.")

    def get_data(self, **kwargs):
        # This method is not used directly, but required by the abstract class
        pass

    def get_news_from_newsapi(self, query, language='en', page_size=10):
        if not self.api_key or NewsApiClient is None:
            st.warning("NewsAPI key is not set or client is not available.")
            return []
        try:
            newsapi = NewsApiClient(api_key=self.api_key)
            news = newsapi.get_everything(q=query,
                                         language=language,
                                         sort_by='relevancy',
                                         page_size=page_size)
            articles = []
            for article in news['articles']:
                articles.append({
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'source': article['source']['name'],
                    'published_at': article['published_at'],
                    'content': article['content']
                })
            return articles
        except Exception as e:
            st.error(f"Error fetching news from NewsAPI: {str(e)}")
            return []

    def get_news_from_yahoo(self, ticker):
        try:
            news_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
            feed = feedparser.parse(news_url)
            articles = []
            for entry in feed.entries[:10]:
                articles.append({
                    'title': entry.title,
                    'description': entry.summary if 'summary' in entry else '',
                    'url': entry.link,
                    'source': 'Yahoo Finance',
                    'published_at': entry.published if 'published' in entry else '',
                    'content': entry.summary if 'summary' in entry else ''
                })
            return articles
        except Exception as e:
            st.error(f"Error fetching news from Yahoo Finance: {str(e)}")
            return []