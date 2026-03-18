# --- OPTIMIERTE NEWS-FUNKTION ---
@st.cache_data(ttl=1800)
def get_stock_news(ticker):
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        # Nur Einträge behalten, die wirklich Inhalt haben
        valid_news = [n for n in news if n.get('title') or n.get('summary')]
        return valid_news[:8]
    except Exception:
        return []

# --- OPTIMIERTER ANZEIGE-BLOCK (in c_news) ---
with c_news:
    name_display = TICKER_NAMES.get(selected_stock, selected_stock)
    st.subheader(f"🗞️ {name_display} News")
    news_items = get_stock_news(selected_stock)
    
    if news_items:
        html = ""
        for n in news_items:
            link = n.get('link') or n.get('resolvedUrl') or "#"
            # Fallback-Kette: Titel -> Zusammenfassung -> Standardtext
            title = n.get('title') or n.get('summary') or "Link zum Artikel"
            # Kürzen, falls der Text zu lang für den Ticker ist
            display_title = (title[:75] + '..') if len(title) > 75 else title
            
            html += f'<div class="news-item"><a href="{link}" target="_blank" style="color:#1E90FF; text-decoration:none; font-weight:500;">{display_title}</a></div>'
        
        # Der Ticker läuft nur, wenn auch wirklich Links da sind
        st.markdown(f'<div class="news-container"><div class="news-scroll">{html}{html}</div></div>', unsafe_allow_html=True)
    else:
        st.info(f"Momentan keine Live-News für {name_display} verfügbar. Versuche es später erneut oder wähle eine andere Aktie.")
