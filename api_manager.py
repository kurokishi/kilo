import streamlit as st

class APIKeyManager:
    def get_fmp_api_key(self):
        return st.session_state.get('fmp_api_key')

    def set_fmp_api_key(self, api_key):
        st.session_state.fmp_api_key = api_key

    def get_news_api_key(self):
        return st.session_state.get('news_api_key')

    def set_news_api_key(self, api_key):
        st.session_state.news_api_key = api_key
