import pandas as pd
import streamlit as st
import time
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

class Portfolio:
    def __init__(self, yfinance_provider, fmp_provider):
        self.df = pd.DataFrame()
        self.yfinance_provider = yfinance_provider
        self.fmp_provider = fmp_provider

    def load_from_file(self, uploaded_file):
        try:
            if uploaded_file.name.endswith('.csv'):
                self.df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                self.df = pd.read_excel(uploaded_file)
            else:
                st.error("Format file tidak didukung. Harap upload file CSV atau Excel.")
                self.df = pd.DataFrame()
            
            if 'Avg Price' in self.df.columns:
                self.df['Avg Price'] = self.df['Avg Price'].replace('[Rp, ]', '', regex=True).astype(float)
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            self.df = pd.DataFrame()

    def update_realtime_data(self):
        if self.df.empty:
            return
        
        df_copy = self.df.copy()
        lot_balance_col = 'Lot Balance'
        
        current_prices = []
        for idx, row in df_copy.iterrows():
            ticker = row['Ticker']
            
            cache_key = f"price_{ticker}"
            if cache_key in st.session_state and (time.time() - st.session_state.get(f"{cache_key}_time", 0)) < 60:
                last_price = st.session_state[cache_key]
            else:
                last_price, _, _, _ = self.yfinance_provider.get_realtime_data(ticker)
                if last_price is not None:
                    st.session_state[cache_key] = last_price
                    st.session_state[f"{cache_key}_time"] = time.time()
            
            if last_price is None:
                last_price = row['Avg Price']
            
            current_prices.append(last_price)
        
        df_copy['Current Price'] = current_prices
        df_copy['Current Value'] = df_copy[lot_balance_col] * df_copy['Current Price']
        df_copy['Profit/Loss'] = df_copy['Current Value'] - (df_copy[lot_balance_col] * df_copy['Avg Price'])
        df_copy['Profit/Loss %'] = (df_copy['Current Value'] / (df_copy[lot_balance_col] * df_copy['Avg Price']) - 1) * 100
        
        self.df = df_copy

    def get_dca_analysis(self):
        if self.df.empty:
            return
        
        self.update_realtime_data()
        
        st.subheader("📊 Analisis Dollar Cost Averaging (DCA)")
        
        lot_balance_col = 'Lot Balance'
        
        self.df['Total Investment'] = self.df[lot_balance_col] * self.df['Avg Price']
        total_investment = self.df['Total Investment'].sum()
        total_current_value = self.df['Current Value'].sum()
        total_profit = total_current_value - total_investment
        total_profit_percent = (total_current_value / total_investment - 1) * 100 if total_investment else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Investasi", f"Rp {total_investment:,.0f}", "Nilai Awal")
        col2.metric("Nilai Saat Ini", f"Rp {total_current_value:,.0f}", 
                    f"{total_profit_percent:+.2f}%")
        col3.metric("Profit/Loss", f"Rp {total_profit:,.0f}", 
                    f"{total_profit_percent:+.2f}%")
        
        st.subheader("Alokasi Portfolio")
        fig = px.pie(self.df, names='Ticker', values='Current Value',
                     hover_data=['Profit/Loss %'],
                     title='Komposisi Portfolio Berdasarkan Nilai Saat Ini')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Profit/Loss per Saham")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=self.df['Ticker'],
            y=self.df['Profit/Loss'],
            text=self.df['Profit/Loss'].apply(lambda x: f"Rp {x:,.0f}"),
            textposition='auto',
            marker_color=np.where(self.df['Profit/Loss'] >= 0, 'green', 'red')
        ))
        
        fig_bar.update_layout(
            title='Profit/Loss per Saham',
            yaxis_title='Jumlah (Rp)',
            xaxis_title='Saham'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.subheader("Detail Portfolio")
        df_display = self.df[['Ticker', lot_balance_col, 'Avg Price', 'Current Price', 
                        'Total Investment', 'Current Value', 'Profit/Loss', 'Profit/Loss %']]
        
        df_display = df_display.rename(columns={
            lot_balance_col: 'Jumlah Lembar',
            'Avg Price': 'Harga Rata-rata',
            'Current Price': 'Harga Saat Ini',
            'Total Investment': 'Total Investasi',
            'Current Value': 'Nilai Saat Ini',
            'Profit/Loss': 'Keuntungan/Kerugian',
            'Profit/Loss %': 'Keuntungan/Kerugian %'
        })
        
        st.dataframe(df_display.style.format({
            'Harga Rata-rata': 'Rp {:,.0f}',
            'Harga Saat Ini': 'Rp {:,.0f}',
            'Total Investasi': 'Rp {:,.0f}',
            'Nilai Saat Ini': 'Rp {:,.0f}',
            'Keuntungan/Kerugian': 'Rp {:,.0f}',
            'Keuntungan/Kerugian %': '{:+.2f}%'
        }), use_container_width=True)

    def capital_tracking(self):
        if 'transactions' not in st.session_state:
            st.session_state.transactions = []
            
        st.subheader("💵 Tracking Modal")
        
        with st.expander("Tambah Transaksi Baru"):
            with st.form("transaction_form"):
                date = st.date_input("Tanggal Transaksi", pd.to_datetime("today"))
                ticker = st.text_input("Kode Saham", "BBCA.JK")
                action = st.selectbox("Aksi", ["Beli", "Jual"])
                shares = st.number_input("Jumlah Lembar", min_value=1, value=100)
                price = st.number_input("Harga per Lembar (Rp)", min_value=1, value=10000)
                submit = st.form_submit_button("Tambahkan Transaksi")
                
                if submit:
                    transaction = {
                        'Date': date,
                        'Ticker': ticker,
                        'Action': action,
                        'Shares': shares,
                        'Price': price,
                        'Amount': shares * price * (-1 if action == "Jual" else 1)
                    }
                    st.session_state.transactions.append(transaction)
                    st.success("Transaksi ditambahkan!")
        
        if st.session_state.transactions:
            df_transactions = pd.DataFrame(st.session_state.transactions)
            
            df_transactions['Cumulative'] = df_transactions['Amount'].cumsum()
            
            st.dataframe(df_transactions.style.format({
                'Price': 'Rp {:,.0f}',
                'Amount': 'Rp {:,.0f}',
                'Cumulative': 'Rp {:,.0f}'
            }), use_container_width=True)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_transactions['Date'],
                y=df_transactions['Cumulative'],
                mode='lines+markers',
                name='Saldo Akumulatif'
            ))
            fig.update_layout(
                title='Riwayat Saldo Investasi',
                yaxis_title='Saldo (Rp)',
                xaxis_title='Tanggal'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            total_investment = df_transactions[df_transactions['Action'] == 'Beli']['Amount'].sum()
            total_sales = abs(df_transactions[df_transactions['Action'] == 'Jual']['Amount'].sum())
            net_cashflow = df_transactions['Amount'].sum()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Pembelian", f"Rp {total_investment:,.0f}")
            col2.metric("Total Penjualan", f"Rp {total_sales:,.0f}")
            col3.metric("Saldo Saat Ini", f"Rp {net_cashflow:,.0f}")