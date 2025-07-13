import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import random
from sentiment_analyzer import SentimentAnalyzer
from news_provider import NewsProvider

class StockAnalyzer:
    def __init__(self, yfinance_provider, fmp_provider):
        self.yfinance_provider = yfinance_provider
        self.fmp_provider = fmp_provider

    def get_prediction(self, ticker):
        try:
            st.subheader(f"📈 Prediksi Harga Saham: {ticker}")
            
            hist = self.yfinance_provider.get_stock_history(ticker)
            if hist is None:
                return
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name='Harga Historis'
            ))
            
            hist['MA20'] = hist['Close'].rolling(window=20).mean()
            hist['MA50'] = hist['Close'].rolling(window=50).mean()
            
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['MA20'],
                line=dict(color='orange', width=1.5),
                name='MA 20 Hari'
            ))
            
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['MA50'],
                line=dict(color='blue', width=1.5),
                name='MA 50 Hari'
            ))
            
            fig.update_layout(
                title=f'Perjalanan Harga {ticker}',
                yaxis_title='Harga (Rp)',
                xaxis_rangeslider_visible=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            last_price = hist['Close'].iloc[-1]
            ma20 = hist['MA20'].iloc[-1]
            ma50 = hist['MA50'].iloc[-1]
            
            if ma20 > ma50 and last_price > ma20:
                trend = "Naik"
                prediction = last_price * 1.05
            elif ma20 < ma50 and last_price < ma20:
                trend = "Turun"
                prediction = last_price * 0.95
            else:
                trend = "Netral"
                prediction = last_price * 1.01
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Harga Terakhir", f"Rp {last_price:,.0f}")
            col2.metric("Prediksi 1 Bulan", f"Rp {prediction:,.0f}", 
                       f"{(prediction/last_price-1)*100:+.2f}%")
            col3.metric("Trend", trend)
            
            rsi = self._calculate_rsi(hist['Close'])
            macd, signal = self._calculate_macd(hist['Close'])
            
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=hist.index, y=rsi, name='RSI', line=dict(color='purple')))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.update_layout(title='Relative Strength Index (RSI)', yaxis_title='RSI')
            st.plotly_chart(fig_rsi, use_container_width=True)
            
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=hist.index, y=macd, name='MACD', line=dict(color='blue')))
            fig_macd.add_trace(go.Scatter(x=hist.index, y=signal, name='Signal', line=dict(color='orange')))
            fig_macd.update_layout(title='Moving Average Convergence Divergence (MACD)', yaxis_title='Value')
            st.plotly_chart(fig_macd, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error in prediction: {str(e)}")

    def _calculate_rsi(self, prices, window=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        
        avg_gain = gain.rolling(window=window).mean().replace(0, 1e-10)
        avg_loss = loss.rolling(window=window).mean().replace(0, 1e-10)
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, prices, slow=26, fast=12, signal=9):
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        return macd, macd_signal

    def get_valuation(self, ticker):
        try:
            st.subheader(f"💰 Valuasi Saham: {ticker}")
            
            fmp_data = self.fmp_provider.get_fmp_data(ticker)
            if not fmp_data:
                st.warning("Tidak dapat melanjutkan valuasi tanpa data FMP")
                return
            
            profile = fmp_data['profile']
            ratios = fmp_data['ratios']
            cashflow = fmp_data['cashflow']
            quote = fmp_data['quote']
            growth = fmp_data['growth']
            
            col1, col2, col3 = st.columns(3)
            current_price = quote.get('price', 0)
            change_percent = quote.get('changesPercentage', 0)
            
            col1.metric("Harga Saat Ini", f"Rp {current_price:,.0f}", 
                       f"{change_percent:+.2f}%")
            
            per = ratios.get('priceEarningsRatio', 0)
            industry_per = profile.get('peRatio', per * 1.1)
            col2.metric("PER (Price/Earnings)", f"{per:.2f}", 
                       f"Industri: {industry_per:.2f}", delta_color="off")
            
            pbv = ratios.get('priceToBookRatio', 0)
            industry_pbv = pbv * 1.15
            col3.metric("PBV (Price/Book)", f"{pbv:.2f}", 
                       f"Industri: {industry_pbv:.2f}", delta_color="off")
            
        except Exception as e:
            st.error(f"Error in valuation: {str(e)}")

    def investment_simulation(self, portfolio_df):
        st.subheader("💰 Rekomendasi Pembelian Saham Berbasis Valuasi")
        
        investment_amount = st.number_input(
            "Modal Investasi (Rp)",
            min_value=100000,
            step=100000,
            value=500000,
            format="%d"
        )
        
        valuation_scores = []
        for ticker in portfolio_df['Ticker']:
            clean_ticker = ticker.replace('.JK', '')
            score = self.calculate_valuation_score(clean_ticker)
            valuation_scores.append(score)
        
        portfolio_df['Valuation Score'] = valuation_scores
        
        portfolio_df = portfolio_df.sort_values(by='Valuation Score', ascending=False)
        
        total_score = portfolio_df['Valuation Score'].sum()
        if total_score > 0:
            portfolio_df['Allocation Weight'] = portfolio_df['Valuation Score'] / total_score
        else:
            portfolio_df['Allocation Weight'] = 1 / len(portfolio_df)
        
        portfolio_df['Allocation Amount'] = portfolio_df['Allocation Weight'] * investment_amount
        portfolio_df['Additional Shares'] = (portfolio_df['Allocation Amount'] / portfolio_df['Current Price']).astype(int)
        portfolio_df['Additional Investment'] = portfolio_df['Additional Shares'] * portfolio_df['Current Price']
        
        actual_investment = portfolio_df['Additional Investment'].sum()
        
        remaining_capital = investment_amount - actual_investment
        
        if remaining_capital > 0:
            for idx, row in portfolio_df.iterrows():
                if remaining_capital <= 0:
                    break
                current_price = row['Current Price']
                if current_price <= remaining_capital:
                    additional_shares = remaining_capital // current_price
                    if additional_shares > 0:
                        portfolio_df.at[idx, 'Additional Shares'] += additional_shares
                        additional_investment = additional_shares * current_price
                        portfolio_df.at[idx, 'Additional Investment'] += additional_investment
                        remaining_capital -= additional_investment
        
        portfolio_df['New Shares'] = portfolio_df['Lot Balance'] + portfolio_df['Additional Shares']
        portfolio_df['New Value'] = portfolio_df['New Shares'] * portfolio_df['Current Price']
        
        total_new_investment = portfolio_df['Additional Investment'].sum()
        total_new_value = portfolio_df['New Value'].sum()
        total_portfolio_value = portfolio_df['Current Value'].sum()
        
        st.write(f"### Rekomendasi Pembelian untuk Modal Rp {investment_amount:,.0f}")
        
        col1, col2 = st.columns(2)
        col1.metric("Total Investasi Tambahan", f"Rp {total_new_investment:,.0f}")
        col2.metric("Total Nilai Portfolio Baru", f"Rp {total_new_value:,.0f}",
                    f"{((total_new_value - total_portfolio_value)/total_portfolio_value*100):+.2f}%")
        
        buy_recommendations = portfolio_df[portfolio_df['Additional Shares'] > 0].copy()
        buy_recommendations = buy_recommendations.sort_values(by='Additional Investment', ascending=False)
        
        if not buy_recommendations.empty:
            buy_recommendations['Ranking'] = range(1, len(buy_recommendations) + 1)
            
            rec_df = buy_recommendations[['Ranking', 'Ticker', 'Valuation Score', 'Current Price', 'Additional Shares', 'Additional Investment']]
            
            rec_df = rec_df.rename(columns={
                'Valuation Score': 'Skor Valuasi',
                'Current Price': 'Harga Saat Ini',
                'Additional Shares': 'Jumlah Pembelian',
                'Additional Investment': 'Total Pembelian'
            })
            
            rec_display = rec_df.style.format({
                'Harga Saat Ini': 'Rp {:,.0f}',
                'Total Pembelian': 'Rp {:,.0f}'
            }).background_gradient(subset=['Skor Valuasi'], cmap='YlGn')
            
            st.dataframe(rec_display, use_container_width=True)
            
            fig = px.pie(buy_recommendations, names='Ticker', values='Additional Investment',
                         title='Distribusi Pembelian Berdasarkan Valuasi')
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=buy_recommendations['Ticker'],
                y=buy_recommendations['Valuation Score'],
                text=buy_recommendations['Valuation Score'],
                textposition='auto',
                marker_color='skyblue'
            ))
            fig_bar.update_layout(
                title='Skor Valuasi Saham',
                yaxis_title='Skor',
                xaxis_title='Saham'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("Tidak ada rekomendasi pembelian saham dengan modal yang tersedia")
        
        return portfolio_df

    def calculate_valuation_score(self, ticker):
        try:
            fmp_data = self.fmp_provider.get_fmp_data(ticker)
            if not fmp_data:
                return 0
            
            ratios = fmp_data['ratios']
            
            per = ratios.get('priceEarningsRatio', 0)
            pbv = ratios.get('priceToBookRatio', 0)
            roe = ratios.get('returnOnEquity', 0) * 100
            npm = ratios.get('netProfitMargin', 0) * 100
            dividend_yield = ratios.get('dividendYield', 0) * 100
            
            score = 0
            
            if per > 0 and per < 15: score += 3
            elif per < 20: score += 2
            elif per < 25: score += 1
                
            if pbv > 0 and pbv < 1: score += 3
            elif pbv < 1.5: score += 2
            elif pbv < 2: score += 1
                
            if roe > 20: score += 3
            elif roe > 15: score += 2
            elif roe > 10: score += 1
                
            if npm > 20: score += 3
            elif npm > 15: score += 2
            elif npm > 10: score += 1
                
            if dividend_yield > 5: score += 3
            elif dividend_yield > 3: score += 2
            elif dividend_yield > 1: score += 1
                
            return score
        
        except Exception as e:
            st.error(f"Error calculating valuation score: {str(e)}")
            return 0

    def get_undervalued_recommendations(self):
        st.subheader("🔍 Saham Undervalued Minggu Ini")
        
        if not self.fmp_provider.api_key:
            st.warning("Silakan masukkan API Key FMP di sidebar untuk mengakses fitur ini")
            return []
        
        try:
            indonesian_stocks_url = f"https://financialmodelingprep.com/api/v3/stock-screener?exchange=IDX&apikey={self.fmp_provider.api_key}"
            response = requests.get(indonesian_stocks_url)
            stocks_data = response.json()
            
            if not stocks_data:
                st.warning("Tidak dapat menemukan data saham Indonesia")
                return []
            
            filtered_stocks = [
                stock for stock in stocks_data
                if stock.get('marketCap', 0) > 1000000000000
            ]
            
            selected_stocks = random.sample(filtered_stocks, min(20, len(filtered_stocks)))
            
            undervalued_stocks = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, stock in enumerate(selected_stocks):
                ticker = stock['symbol']
                status_text.text(f"Menganalisis {ticker} ({i+1}/{len(selected_stocks)})...")
                
                score = self.calculate_valuation_score(ticker)
                
                if score >= 8:
                    fmp_data = self.fmp_provider.get_fmp_data(ticker)
                    if not fmp_data:
                        continue
                    
                    ratios = fmp_data.get('ratios', {})
                    quote = fmp_data.get('quote', {})
                    
                    undervalued_stocks.append({
                        'Ticker': ticker,
                        'Nama': stock.get('companyName', ticker),
                        'PER': ratios.get('priceEarningsRatio', 0),
                        'PBV': ratios.get('priceToBookRatio', 0),
                        'Dividend Yield': ratios.get('dividendYield', 0) * 100,
                        'ROE': ratios.get('returnOnEquity', 0) * 100,
                        'Skor': score,
                        'Harga': quote.get('price', 0)
                    })
                
                progress_bar.progress((i+1)/len(selected_stocks))
            
            status_text.text("Analisis selesai!")
            
            if undervalued_stocks:
                undervalued_stocks.sort(key=lambda x: x['Skor'], reverse=True)
                
                st.success(f"Ditemukan {len(undervalued_stocks)} saham undervalued!")
                
                df = pd.DataFrame(undervalued_stocks)
                st.dataframe(df.style.format({
                    'PER': '{:.2f}',
                    'PBV': '{:.2f}',
                    'Dividend Yield': '{:.2f}%',
                    'ROE': '{:.2f}%',
                    'Harga': 'Rp {:,.0f}'
                }).background_gradient(subset=['Skor'], cmap='YlGn'), use_container_width=True)
                
                fig = px.bar(df, x='Nama', y='Skor', color='Skor',
                             title='Skor Undervalued Saham',
                             labels={'Nama': 'Saham', 'Skor': 'Skor Undervalued'})
                st.plotly_chart(fig, use_container_width=True)
                
                return undervalued_stocks
            else:
                st.warning("Tidak ditemukan saham yang memenuhi kriteria undervalued minggu ini")
                return []
                
        except Exception as e:
            st.error(f"Error dalam mendapatkan rekomendasi saham undervalued: {str(e)}")
            return []

    def stock_comparison(self, portfolio_df=pd.DataFrame()):
        st.subheader("📊 Komparasi Saham")
        st.info("Bandingkan saham dari portofolio Anda dengan saham lainnya di pasar Indonesia")
       
        tickers_input = st.text_input(
            "Masukkan kode saham (pisahkan dengan koma, contoh: BBCA,BBRI,TLKM):",
            "BBCA.JK,BBRI.JK"
        )
        
        input_tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        
        portfolio_tickers = []
        if not portfolio_df.empty:
            portfolio_tickers = portfolio_df['Ticker'].tolist()
        
        all_tickers = list(set(input_tickers + portfolio_tickers))
        
        if len(all_tickers) < 2:
            st.warning("Masukkan minimal 2 saham untuk dibandingkan")
            return
        if len(all_tickers) > 5:
            st.warning("Maksimal 5 saham yang dapat dibandingkan")
            all_tickers = all_tickers[:5]
        
        if not self.fmp_provider.api_key:
            st.warning("Silakan masukkan API Key FMP di sidebar untuk fitur ini")
            return

        selected_portfolio = portfolio_tickers

        comparison_data = []
        
        with st.spinner("Mengumpulkan data saham..."):
            for ticker in all_tickers:
                clean_ticker = ticker.replace('.JK', '')
                
                fmp_data = self.fmp_provider.get_fmp_data(clean_ticker)
                
                sentiment_score = self.get_stock_sentiment(ticker)
                
                last_price, _, _, _ = self.yfinance_provider.get_realtime_data(ticker)
                
                if fmp_data and 'profile' in fmp_data:
                    profile = fmp_data.get('profile', {})
                    ratios = fmp_data.get('ratios', {})
                    growth = fmp_data.get('growth', {})
                    quote = fmp_data.get('quote', {})
                else:
                    profile, ratios, growth, quote = {}, {}, {}, {}
                
                comparison_data.append({
                    "Ticker": ticker,
                    "Nama": profile.get('companyName', ticker),
                    "Harga": quote.get('price', last_price) if last_price else 0,
                    "PER": ratios.get('priceEarningsRatio', 0),
                    "PBV": ratios.get('priceToBookRatio', 0),
                    "ROE": ratios.get('returnOnEquity', 0) * 100 if ratios.get('returnOnEquity') else 0,
                    "Pertumbuhan Pendapatan": growth.get('growthRevenue', 0) * 100 if growth.get('growthRevenue') else 0,
                    "Sentimen": sentiment_score,
                    "Dividen Yield": ratios.get('dividendYield', 0) * 100 if ratios.get('dividendYield') else 0,
                    "Sumber": "Portofolio Anda" if ticker in selected_portfolio else "Pasar Indonesia"
                })

        if not comparison_data:
            st.error("Tidak ada data yang berhasil dikumpulkan")
            return
        
        st.subheader("Perbandingan Metrik Fundamental")
        df = pd.DataFrame(comparison_data)
        
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Grafik Perbandingan")
        
        metrics = st.multiselect(
            "Pilih metrik untuk ditampilkan:",
            options=["PER", "PBV", "ROE", "Pertumbuhan Pendapatan", "Sentimen", "Dividen Yield"],
            default=["PER", "PBV", "ROE"]
        )
        
        if metrics:
            for metric in metrics:
                fig = px.bar(
                    df, x="Ticker", y=metric, color="Sumber", title=f"Perbandingan {metric}",
                    text=df[metric].apply(lambda x: f"{x:.2f}{'%' if metric != 'Sentimen' else ''}"),
                    labels={"value": metric},
                    color_discrete_map={"Portofolio Anda": "green", "Pasar Indonesia": "blue"}
                )
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{metric}")

    def get_stock_sentiment(self, ticker):
        news_provider = NewsProvider()
        sentiment_analyzer = SentimentAnalyzer(news_provider)
        articles = news_provider.get_news_from_yahoo(ticker)
        sentiment_scores = []
        
        for article in articles[:5]:
            text = f"{article['title']}. {article['description']}"
            sentiment = sentiment_analyzer.analyze_text(text)
            sentiment_scores.append(sentiment['combined_score'])
        
        return np.mean(sentiment_scores) if sentiment_scores else 0