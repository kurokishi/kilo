import yfinance as yf
import streamlit as st
import time
from data_provider import DataProvider

class YFinanceProvider(DataProvider):
    def get_data(self, **kwargs):
        # This method is not used directly, but required by the abstract class
        pass

    def get_realtime_data(self, ticker):
        try:
            time.sleep(0.5)  # Delay 500ms between requests
            
            stock = yf.Ticker(ticker)
            
            try:
                hist = stock.history(period="1d", interval="5m")
            except Exception as e:
                hist = stock.history(period="1d", interval="1d")
            
            if hist.empty:
                hist = stock.history(period="1d")
                if hist.empty:
                    return None, None, None, None
            
            last_price = hist['Close'].iloc[-1]
            
            try:
                prev_close = stock.info.get('previousClose', last_price)
            except:
                prev_close = hist['Open'].iloc[0] if not hist.empty else last_price
            
            change = last_price - prev_close
            change_percent = (change / prev_close) * 100
            
            return last_price, change, change_percent, hist
            
        except Exception as e:
            if "Too Many Requests" in str(e) or "429" in str(e):
                st.warning("Yahoo Finance rate limit terlampaui. Data mungkin tidak real-time.")
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="1d")
                    if not hist.empty:
                        last_price = hist['Close'].iloc[-1]
                        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else hist['Open'].iloc[0]
                        change = last_price - prev_close
                        change_percent = (change / prev_close) * 100
                        return last_price, change, change_percent, hist
                except:
                    pass
            
            st.error(f"Error fetching data: {str(e)}")
            return None, None, None, None

    def get_stock_history(self, ticker, period="1y"):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty:
                st.warning(f"Data tidak ditemukan untuk {ticker}")
                return None
            return hist
        except Exception as e:
            st.error(f"Error fetching history for {ticker}: {str(e)}")
            return None