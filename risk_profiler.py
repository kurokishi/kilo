import streamlit as st
import pandas as pd
import plotly.express as px

class RiskProfiler:
    def get_user_profile(self):
        st.subheader("📝 Profil Risiko Investor")
        
        if 'risk_profile' not in st.session_state:
            with st.form("risk_profile_form"):
                st.write("Silakan jawab pertanyaan berikut untuk menentukan profil risiko:")
                
                q1 = st.radio(
                    "1. Apa tujuan utama investasi Anda?",
                    options=[
                        ("Pelestarian modal (risiko rendah)", 1),
                        ("Pertumbuhan modal moderat", 2),
                        ("Pertumbuhan modal agresif", 3),
                        ("Pendapatan spekulatif tinggi", 4)
                    ],
                    format_func=lambda x: x[0]
                )[1]
                
                q2 = st.radio(
                    "2. Berapa lama horizon investasi Anda?",
                    options=[
                        ("Kurang dari 1 tahun", 1),
                        ("1-3 tahun", 2),
                        ("3-5 tahun", 3),
                        ("Lebih dari 5 tahun", 4)
                    ],
                    format_func=lambda x: x[0]
                )[1]
                
                q3 = st.radio(
                    "3. Bagaimana reaksi Anda terhadap penurunan 20% portofolio dalam 1 bulan?",
                    options=[
                        ("Jual semua investasi", 1),
                        ("Jual sebagian", 2),
                        ("Tahan dan pantau", 3),
                        ("Beli lebih banyak", 4)
                    ],
                    format_func=lambda x: x[0]
                )[1]
                
                q4 = st.radio(
                    "4. Pengalaman investasi Anda?",
                    options=[
                        ("Pemula (baru mulai)", 1),
                        ("Sedang (1-3 tahun)", 2),
                        ("Berpengalaman (3-5 tahun)", 3),
                        ("Sangat berpengalaman (>5 tahun)", 4)
                    ],
                    format_func=lambda x: x[0]
                )[1]
                
                submitted = st.form_submit_button("Tentukan Profil Risiko")
                
                if submitted:
                    total_score = q1 + q2 + q3 + q4
                    
                    if total_score <= 6:
                        profile = "Konservatif"
                    elif total_score <= 10:
                        profile = "Moderat"
                    elif total_score <= 14:
                        profile = "Agresif"
                    else:
                        profile = "Sangat Agresif"
                    
                    st.session_state.risk_profile = profile
                    st.success(f"Profil risiko Anda: {profile}")
                    st.rerun()
        
        if 'risk_profile' in st.session_state:
            st.info(f"Profil risiko saat ini: **{st.session_state.risk_profile}**")
            if st.button("Ubah Profil Risiko"):
                del st.session_state.risk_profile
                st.rerun()
        
        return st.session_state.get('risk_profile', None)

    def get_diversification_recommendation(self, portfolio_df, risk_profile):
        st.subheader("🌐 Rekomendasi Diversifikasi Portofolio")
        
        if not risk_profile:
            st.warning("Silakan tentukan profil risiko Anda terlebih dahulu")
            return
        
        if portfolio_df.empty:
            st.warning("Silakan upload portofolio Anda terlebih dahulu")
            return
        
        allocation_guidelines = {
            "Konservatif": {"Saham Blue Chip": 70, "Saham Pendapatan": 20, "Reksa Dana Pendapatan Tetap": 10, "Saham Growth": 0, "Saham Spekulatif": 0},
            "Moderat": {"Saham Blue Chip": 50, "Saham Pendapatan": 20, "Reksa Dana Pendapatan Tetap": 10, "Saham Growth": 15, "Saham Spekulatif": 5},
            "Agresif": {"Saham Blue Chip": 30, "Saham Pendapatan": 10, "Reksa Dana Pendapatan Tetap": 5, "Saham Growth": 40, "Saham Spekulatif": 15},
            "Sangat Agresif": {"Saham Blue Chip": 20, "Saham Pendapatan": 5, "Reksa Dana Pendapatan Tetap": 0, "Saham Growth": 50, "Saham Spekulatif": 25}
        }
        
        blue_chips = ["BBCA", "BBRI", "BBNI", "BMRI", "TLKM", "EXCL", "ASII"]
        income_stocks = ["UNVR", "ICBP", "MYOR", "INDF", "SMGR"]
        growth_stocks = ["GOTO", "ARTO", "BRIS", "ACES", "EMTK"]
        
        portfolio_df['Kategori'] = "Lainnya"
        
        for idx, row in portfolio_df.iterrows():
            ticker = row['Ticker'].replace('.JK', '')
            if ticker in blue_chips:
                portfolio_df.at[idx, 'Kategori'] = "Saham Blue Chip"
            elif ticker in income_stocks:
                portfolio_df.at[idx, 'Kategori'] = "Saham Pendapatan"
            elif ticker in growth_stocks:
                portfolio_df.at[idx, 'Kategori'] = "Saham Growth"
            else:
                portfolio_df.at[idx, 'Kategori'] = "Saham Spekulatif"
        
        total_value = portfolio_df['Current Value'].sum()
        current_allocation = portfolio_df.groupby('Kategori')['Current Value'].sum() / total_value * 100
        
        target_allocation = allocation_guidelines[risk_profile]
        
        st.write(f"### Alokasi Portofolio Saat Ini vs Rekomendasi ({risk_profile})")
        
        allocation_data = []
        for category in target_allocation:
            allocation_data.append({
                'Kategori': category,
                'Saat Ini': current_allocation.get(category, 0),
                'Target': target_allocation[category]
            })
        
        df_allocation = pd.DataFrame(allocation_data)
        
        fig = px.bar(df_allocation, x='Kategori', y=['Saat Ini', 'Target'],
                     barmode='group', title='Alokasi Portofolio Saat Ini vs Target')
        fig.update_layout(yaxis_title='Persentase (%)')
        st.plotly_chart(fig, use_container_width=True)

    def calculate_portfolio_risk_score(self, portfolio_df, fmp_provider):
        st.subheader("📊 Skor Risiko Portofolio")
        
        if portfolio_df.empty:
            st.warning("Silakan upload portofolio Anda terlebih dahulu")
            return 0
        
        if not fmp_provider.api_key:
            st.warning("Silakan masukkan API Key FMP di sidebar untuk fitur ini")
            return 0
        
        if 'Current Value' not in portfolio_df.columns:
            st.warning("Kolom 'Current Value' tidak ditemukan, menggunakan 'Avg Price' sebagai alternatif")
            portfolio_df['Current Value'] = portfolio_df['Lot Balance'] * portfolio_df['Avg Price']
        
        risk_factors = []
        
        for i, (idx, row) in enumerate(portfolio_df.iterrows()):
            ticker = row['Ticker'].replace('.JK', '')
            
            try:
                fmp_data = fmp_provider.get_fmp_data(ticker)
                if not fmp_data:
                    continue
                    
                ratios = fmp_data.get('ratios', {})
                profile = fmp_data.get('profile', {})
                quote = fmp_data.get('quote', {})
                
                beta = profile.get('beta', 1.0)
                vol = quote.get('change', 0)
                per = ratios.get('priceEarningsRatio', 15)
                der = ratios.get('debtEquityRatio', 0.5)
                size = profile.get('mktCap', 1000000000000)
                
                risk_score = 0
                
                if beta > 1.5: risk_score += 3
                elif beta > 1.2: risk_score += 2
                elif beta > 1.0: risk_score += 1
                    
                if abs(vol) > 5: risk_score += 3
                elif abs(vol) > 3: risk_score += 2
                elif abs(vol) > 1: risk_score += 1
                    
                if per > 25: risk_score += 2
                elif per > 20: risk_score += 1
                    
                if der > 2.0: risk_score += 3
                elif der > 1.5: risk_score += 2
                elif der > 1.0: risk_score += 1
                    
                if size < 500000000000: risk_score += 3
                elif size < 1000000000000: risk_score += 2
                elif size < 5000000000000: risk_score += 1
                    
                risk_factors.append({
                    'Ticker': ticker, 'Beta': beta, 'Volatilitas': vol, 'PER': per,
                    'DER': der, 'Market Cap': size, 'Skor Risiko': min(10, risk_score)
                })
                
            except Exception as e:
                st.error(f"Error menganalisis {ticker}: {str(e)}")
        
        if not risk_factors:
            st.warning("Tidak dapat menghitung skor risiko")
            return 0
        
        total_value = portfolio_df['Current Value'].sum()
        portfolio_risk_score = 0
        
        for risk_factor in risk_factors:
            ticker = risk_factor['Ticker']
            mask = portfolio_df['Ticker'].str.contains(ticker, regex=False)
            stock_value = portfolio_df.loc[mask, 'Current Value'].sum()
            
            weight = stock_value / total_value if total_value > 0 else 0
            portfolio_risk_score += risk_factor['Skor Risiko'] * weight
        
        st.metric("Skor Risiko Portofolio", f"{portfolio_risk_score:.1f}/10.0",
                 "Rendah" if portfolio_risk_score < 3 else
                 "Sedang" if portfolio_risk_score < 6 else
                 "Tinggi" if portfolio_risk_score < 8 else "Sangat Tinggi")
        
        df_risk = pd.DataFrame(risk_factors)
        st.dataframe(df_risk.style.format({
            'Beta': '{:.2f}', 'Volatilitas': '{:.2f}%', 'PER': '{:.2f}',
            'DER': '{:.2f}', 'Market Cap': 'Rp {:,.0f}'
        }).background_gradient(subset=['Skor Risiko'], cmap='YlOrRd'), use_container_width=True)
        
        return portfolio_risk_score