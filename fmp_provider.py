import requests
import streamlit as st
from data_provider import DataProvider

class FMPProvider(DataProvider):
    def __init__(self, api_key):
        self.api_key = api_key

    def get_data(self, **kwargs):
        # This method is not used directly, but required by the abstract class
        pass

    def get_fmp_data(self, ticker):
        if not self.api_key:
            st.warning("FMP API Key is not set.")
            return None
        try:
            profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={self.api_key}"
            profile_response = requests.get(profile_url)
            
            if profile_response.status_code != 200:
                error_msg = f"Error {profile_response.status_code}: {profile_response.text}"
                st.error(f"Error fetching FMP profile data: {error_msg}")
                return None
                
            profile_data = profile_response.json()
            
            if not profile_data:
                st.warning(f"Data perusahaan tidak ditemukan untuk {ticker}")
                return None
            
            ratios_url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?period=annual&apikey={self.api_key}"
            ratios_response = requests.get(ratios_url)
            ratios_data = ratios_response.json()
            
            cashflow_url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?period=annual&apikey={self.api_key}"
            cashflow_response = requests.get(cashflow_url)
            cashflow_data = cashflow_response.json()
            
            quote_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={self.api_key}"
            quote_response = requests.get(quote_url)
            quote_data = quote_response.json()
            
            growth_url = f"https://financialmodelingprep.com/api/v3/income-statement-growth/{ticker}?period=annual&apikey={self.api_key}"
            growth_response = requests.get(growth_url)
            growth_data = growth_response.json()
            
            fmp_data = {
                'profile': profile_data[0] if profile_data else {},
                'ratios': ratios_data[0] if ratios_data else {},
                'cashflow': cashflow_data[0] if cashflow_data else {},
                'quote': quote_data[0] if quote_data else {},
                'growth': growth_data[0] if growth_data else {}
            }
            return fmp_data
            
        except Exception as e:
            if "0" in str(e):
                st.error("Koneksi ke API FMP gagal. Silakan cek koneksi internet Anda.")
            else:
                st.error(f"Error fetching FMP data: {str(e)}")
            return None