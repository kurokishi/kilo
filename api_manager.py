import streamlit as st

class APIKeyManager:
   def get_fmp_api_key(self):
       key_suffix = st.session_state.get("current_menu", "default")
       input_key = f"fmp_api_key_input_{key_suffix}"
       button_key = f"save_fmp_api_key_{key_suffix}"

       if 'fmp_api_key' not in st.session_state:
           with st.sidebar:
                st.subheader("FinancialModelingPrep API")
                api_key = st.text_input("Masukkan API Key FMP", type="password", key=input_key)
                if st.button("Simpan API Key", key=button_key):
                    st.session_state.fmp_api_key = api_key
                    st.success("API Key disimpan!")
                    st.rerun()
          return None
       return st.session_state.fmp_api_key
