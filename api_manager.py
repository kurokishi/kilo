import streamlit as st

class APIKeyManager:
    def get_fmp_api_key(self):
        if 'fmp_api_key' not in st.session_state:
            with st.sidebar:
                st.subheader("FinancialModelingPrep API")
                api_key = st.text_input("Masukkan API Key FMP", type="password", key="fmp_api_key_input")
                if st.button("Simpan API Key", key="save_fmp_api_key"):
                    st.session_state.fmp_api_key = api_key
                    st.success("API Key disimpan!")
                    st.rerun()
            return None
        return st.session_state.fmp_api_key

    def get_news_api_key(self):
        if 'news_api_key' not in st.session_state:
            with st.sidebar:
                st.subheader("NewsAPI Configuration")
                api_key = st.text_input("Masukkan NewsAPI Key", type="password", key="news_api_key_input")
                if st.button("Simpan NewsAPI Key", key="save_news_api_key"):
                    st.session_state.news_api_key = api_key
                    st.success("NewsAPI Key disimpan!")
                    st.rerun()
            return None
        return st.session_state.news_api_key