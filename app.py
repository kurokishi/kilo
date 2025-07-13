import streamlit as st
from ui import UIHelper
from api_manager import APIKeyManager
from yfinance_provider import YFinanceProvider
from fmp_provider import FMPProvider
from portfolio import Portfolio
from stock_analyzer import StockAnalyzer
from sentiment_analyzer import SentimentAnalyzer
from news_provider import NewsProvider
from risk_profiler import RiskProfiler

class App:
    def __init__(self):
        self.ui = UIHelper()
        self.api_manager = APIKeyManager()
        self.yfinance_provider = YFinanceProvider()
        self.risk_profiler = RiskProfiler()

    def run(self):
        st.set_page_config(
            page_title="Stock Analysis Toolkit Pro+",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="auto"
        )
        self.ui.setup_pwa()
        self.ui.inject_responsive_css()
        
        selected_menu, uploaded_file = self.ui.display_sidebar(self.api_manager)
        
        fmp_api_key = self.api_manager.get_fmp_api_key()
        news_api_key = self.api_manager.get_news_api_key()

        fmp_provider = FMPProvider(fmp_api_key)
        news_provider = NewsProvider(news_api_key)
        
        portfolio = Portfolio(self.yfinance_provider, fmp_provider)
        stock_analyzer = StockAnalyzer(self.yfinance_provider, fmp_provider)
        sentiment_analyzer = SentimentAnalyzer(news_provider)

        if uploaded_file:
            portfolio.load_from_file(uploaded_file)

        st.title("Stock Analysis Toolkit Pro+")

        if selected_menu == "Dashboard Portfolio" or selected_menu == "Analisis DCA":
            if not portfolio.df.empty:
                portfolio.get_dca_analysis()
            else:
                st.info("Silakan upload file portfolio untuk melihat dashboard")
        
        elif selected_menu == "Prediksi Harga Saham":
            if not portfolio.df.empty:
                selected_ticker = st.selectbox("Pilih Saham", portfolio.df['Ticker'].tolist())
                stock_analyzer.get_prediction(selected_ticker)
            else:
                st.warning("Silakan upload file portfolio terlebih dahulu")

        elif selected_menu == "Valuasi Saham":
            if not portfolio.df.empty and fmp_api_key:
                selected_ticker = st.selectbox("Pilih Saham", portfolio.df['Ticker'].tolist())
                clean_ticker = selected_ticker.replace('.JK', '')
                stock_analyzer.get_valuation(clean_ticker)
            elif not fmp_api_key:
                st.warning("Silakan masukkan API Key FMP di sidebar")
            else:
                st.warning("Silakan upload file portfolio terlebih dahulu")
        
        elif selected_menu == "Market News & Sentiment":
            sentiment_analyzer.display_news_feed()

        elif selected_menu == "Tracking Modal":
            portfolio.capital_tracking()

        elif selected_menu == "Rekomendasi Pembelian":
            if not portfolio.df.empty and fmp_api_key:
                portfolio.update_realtime_data()
                stock_analyzer.investment_simulation(portfolio.df)
            elif not fmp_api_key:
                st.warning("Silakan masukkan API Key FMP di sidebar")
            else:
                st.warning("Silakan upload file portfolio terlebih dahulu")

        elif selected_menu == "Smart Assistant & Rekomendasi AI":
            st.header("🤖 Smart Assistant & Rekomendasi AI")
            
            tab1, tab2, tab3 = st.tabs([
                "Saham Undervalued",
                "Rekomendasi Diversifikasi",
                "Skor Risiko Portofolio"
            ])
            
            with tab1:
                stock_analyzer.get_undervalued_recommendations()

            with tab2:
                st.subheader("Rekomendasi Diversifikasi Portofolio")
                st.info("Dapatkan rekomendasi alokasi portofolio berdasarkan profil risiko Anda:")
                
                risk_profile = self.risk_profiler.get_user_profile()
                
                if risk_profile and not portfolio.df.empty:
                    portfolio.update_realtime_data()
                    self.risk_profiler.get_diversification_recommendation(portfolio.df, risk_profile)
            
            with tab3:
                st.subheader("Analisis Risiko Portofolio")
                st.info("Skor risiko portofolio Anda berdasarkan karakteristik saham:")
                
                if not portfolio.df.empty and fmp_api_key:
                    portfolio.update_realtime_data()
                    self.risk_profiler.calculate_portfolio_risk_score(portfolio.df, fmp_provider)

        elif selected_menu == "Komparasi Saham":
            if fmp_api_key:
                stock_analyzer.stock_comparison(portfolio.df)
            else:
                st.warning("Silakan masukkan API Key FMP di sidebar")


if __name__ == "__main__":
    app = App()
    app.run()
