import streamlit as st
import base64

class UIHelper:
    def __init__(self):
        pass

    def setup_pwa(self):
        """Setup for PWA"""
        self._add_pwa_meta()
        
        # Generate manifest (in a real app, save as an external file)
        manifest = self._create_manifest()
        st.session_state.manifest = manifest
        self._add_pwa_install_button()

    def _add_pwa_meta(self):
        """Adds meta tags for PWA"""
        pwa_meta = """
            <link rel="manifest" href="manifest.json">
            <meta name="mobile-web-app-capable" content="yes">
            <meta name="apple-mobile-web-app-capable" content="yes">
            <meta name="application-name" content="Stock Analysis">
            <meta name="apple-mobile-web-app-title" content="Stock Analysis">
            <meta name="theme-color" content="#1e3a8a">
            <meta name="msapplication-navbutton-color" content="#1e3a8a">
            <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1, viewport-fit=cover">
            <link rel="apple-touch-icon" href="icon-192x192.png">
        """
        st.markdown(pwa_meta, unsafe_allow_html=True)

    def _create_manifest(self):
        """Creates the manifest.json file for PWA"""
        manifest = {
            "name": "Stock Analysis Toolkit Pro+",
            "short_name": "Stock Analysis",
            "start_url": ".",
            "display": "standalone",
            "theme_color": "#1e3a8a",
            "background_color": "#ffffff",
            "icons": [
                {
                    "src": "icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        }
        return manifest

    def _add_pwa_install_button(self):
        """Adds the PWA installation button"""
        pwa_install_script = """
        <script>
            let deferredPrompt;
            const installButton = document.createElement('button');
            installButton.id = 'installButton';
            installButton.innerHTML = '📱';
            installButton.title = 'Install App';
            document.body.appendChild(installButton);
            
            window.addEventListener('beforeinstallprompt', (e) => {
                e.preventDefault();
                deferredPrompt = e;
                installButton.style.display = 'block';
            });
            
            installButton.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const { outcome } = await deferredPrompt.userChoice;
                    console.log(`User response to the install prompt: ${outcome}`);
                    deferredPrompt = null;
                    installButton.style.display = 'none';
                }
            });
            
            window.addEventListener('appinstalled', () => {
                console.log('PWA was installed');
                installButton.style.display = 'none';
                deferredPrompt = null;
            });
        </script>
        """
        st.markdown(pwa_install_script, unsafe_allow_html=True)

    def inject_responsive_css(self):
        """Injects responsive CSS for mobile devices"""
        mobile_css = """
        <style>
            /* Responsive sidebar */
            @media (max-width: 768px) {
                .sidebar .sidebar-content {
                    width: 100% !important;
                    max-width: 100% !important;
                }
                
                div[data-testid="stSidebarUserContent"] {
                    padding: 1rem 0.5rem !important;
                }
                
                div[data-testid="stVerticalBlock"] > div {
                    padding: 0.5rem !important;
                }
                
                /* More compact menu */
                .sidebar .stSelectbox, .sidebar .stTextInput, .sidebar .stButton {
                    margin-bottom: 0.5rem !important;
                }
                
                /* Smaller header */
                .main h1 {
                    font-size: 1.5rem !important;
                }
                
                /* Metric columns become vertical */
                .stMetric {
                    width: 100% !important;
                    margin-bottom: 0.5rem !important;
                }
                
                /* Smaller charts */
                .stPlotlyChart {
                    height: 300px !important;
                }
                
                /* Hide complex elements on mobile */
                .mobile-hide {
                    display: none !important;
                }
            }
            
            /* Tablet view */
            @media (min-width: 769px) and (max-width: 1024px) {
                .stMetric {
                    width: 50% !important;
                }
            }
            
            /* PWA install button */
            #installButton {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background-color: #1e3a8a;
                color: white;
                border: none;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                z-index: 1000;
                display: none; /* Hidden by default */
            }
            
            /* Mobile-friendly display for all sizes */
            .mobile-optimized {
                padding: 0.5rem !important;
            }
            
            .mobile-full-width {
                width: 100% !important;
            }
            
            .mobile-collapsible {
                margin-bottom: 0.5rem !important;
            }
            
            /* Responsive tables */
            .dataframe {
                font-size: 0.8rem !important;
            }
        </style>
        """
        st.markdown(mobile_css, unsafe_allow_html=True)

    def display_sidebar(self, api_manager):
        st.sidebar.title("📋 Menu Analisis")
        st.sidebar.header("Konfigurasi API")

        if not api_manager.get_fmp_api_key():
            fmp_api_key = st.sidebar.text_input("Masukkan API Key FMP", type="password", key="fmp_api_key_input_ui")
            if st.sidebar.button("Simpan API Key FMP", key="save_fmp_api_key_ui"):
                api_manager.set_fmp_api_key(fmp_api_key)
                st.success("API Key FMP disimpan!")
                st.rerun()

        if not api_manager.get_news_api_key():
            news_api_key = st.sidebar.text_input("Masukkan NewsAPI Key", type="password", key="news_api_key_input_ui")
            if st.sidebar.button("Simpan NewsAPI Key", key="save_news_api_key_ui"):
                api_manager.set_news_api_key(news_api_key)
                st.success("NewsAPI Key disimpan!")
                st.rerun()

        st.sidebar.header("Portfolio")
        uploaded_file = st.sidebar.file_uploader("Upload Portfolio", type=["csv", "xlsx"])
        
        menu_options = [
            "Dashboard Portfolio",
            "Analisis DCA",
            "Prediksi Harga Saham",
            "Valuasi Saham",
            "Tracking Modal",
            "Rekomendasi Pembelian",
            "Market News & Sentiment",
            "Smart Assistant & Rekomendasi AI",
            "Komparasi Saham"
        ]
        selected_menu = st.sidebar.selectbox("Pilih Fitur:", menu_options)
        
        return selected_menu, uploaded_file
