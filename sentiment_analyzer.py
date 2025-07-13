import streamlit as st
import numpy as np
from textblob import TextBlob

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    SentimentIntensityAnalyzer = None

class SentimentAnalyzer:
    def __init__(self, news_provider):
        self.news_provider = news_provider
        if SentimentIntensityAnalyzer is None:
            st.warning("vaderSentiment module not found. Sentiment analysis will be limited.")
            self.analyzer = None
        else:
            self.analyzer = SentimentIntensityAnalyzer()

    def analyze_text(self, text):
        try:
            vader_scores = {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 0}
            if self.analyzer:
                vader_scores = self.analyzer.polarity_scores(text)
            
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            sentiment = {
                'vader_compound': vader_scores['compound'],
                'vader_positive': vader_scores['pos'],
                'vader_negative': vader_scores['neg'],
                'vader_neutral': vader_scores['neu'],
                'textblob_polarity': polarity,
                'textblob_subjectivity': subjectivity,
                'combined_score': (vader_scores['compound'] + polarity) / 2
            }
            return sentiment
        except:
            return {
                'vader_compound': 0, 'vader_positive': 0, 'vader_negative': 0, 'vader_neutral': 0,
                'textblob_polarity': 0, 'textblob_subjectivity': 0, 'combined_score': 0
            }

    def display_news_feed(self):
        st.subheader("📰 Market News & Sentiment Analysis")
        
        news_source = st.selectbox("Sumber Berita", ["Yahoo Finance", "NewsAPI"])
        
        analysis_level = st.radio("Tingkat Analisis", ["Market", "Sektor", "Saham Tertentu"], horizontal=True)
        
        articles = []
        
        if analysis_level == "Market":
            query = "stocks OR market OR economy"
            if news_source == "NewsAPI":
                articles = self.news_provider.get_news_from_newsapi(query)
            else:
                articles = self.news_provider.get_news_from_yahoo('^GSPC')
        
        elif analysis_level == "Saham Tertentu":
            ticker = st.text_input("Masukkan Kode Saham (contoh: AAPL)", "AAPL")
            if news_source == "NewsAPI":
                articles = self.news_provider.get_news_from_newsapi(ticker)
            else:
                articles = self.news_provider.get_news_from_yahoo(ticker)

        if articles:
            st.subheader(f"Berita Terbaru ({len(articles)} ditemukan)")
            
            sentiment_scores = []
            for article in articles:
                text = f"{article['title']}. {article['description']}"
                sentiment = self.analyze_text(text)
                article['sentiment'] = sentiment
                sentiment_scores.append(sentiment['combined_score'])
            
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
            
            st.metric("Rata-rata Sentimen Pasar", f"{avg_sentiment:.2f}", 
                     "Positif" if avg_sentiment > 0.1 else "Negatif" if avg_sentiment < -0.1 else "Netral",
                     delta_color="off")

            for article in articles:
                sentiment = article['sentiment']
                sentiment_score = sentiment['combined_score']
                
                border_color = "green" if sentiment_score > 0.2 else "red" if sentiment_score < -0.2 else "gray"
                
                with st.container():
                    st.markdown(f"""
                    <div style="border-left: 5px solid {border_color}; padding: 10px; margin-bottom: 10px; background-color: #f8f9fa; border-radius: 5px;">
                        <h4><a href="{article['url']}" target="_blank">{article['title']}</a></h4>
                        <p>{article['description']}</p>
                        <div style="font-size: 0.8em; color: #666;">
                            <b>Sumber:</b> {article['source']} | 
                            <b>Tanggal:</b> {article['published_at'][:10] if article['published_at'] else 'N/A'} | 
                            <b>Sentimen:</b> {sentiment_score:.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Tidak ada berita yang ditemukan.")