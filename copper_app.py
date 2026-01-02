import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# --- 頁面設定 ---
st.set_page_config(page_title="電機材料-銅價決策系統", layout="wide")

# --- 側邊欄：參數設定 ---
st.sidebar.title("⚙️ 參數設定")
ma_short = st.sidebar.slider("短期均線 (MA)", 5, 20, 5)
ma_long = st.sidebar.slider("長期均線 (MA)", 20, 60, 20)
inventory_level = st.sidebar.select_slider("目前庫存水位", options=["低", "中", "高"], value="中")

# --- 核心函數：抓取資料 ---
# --- 核心函數：抓取資料 ---
# --- 核心函數：抓取資料 ---
@st.cache_data(ttl=3600)
def get_data():
    data = pd.DataFrame()
    try:
        # 方法 1: 使用 Ticker.history (較穩定)
        # 用戶抱怨 Render 上抓不到資料，嘗試分開抓取並合併
        
        # 建立 Session (偽裝瀏覽器)
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        # 抓取銅價
        copper = yf.Ticker("HG=F", session=session)
        df_copper = copper.history(period="3mo")
        
        # 抓取匯率
        usd = yf.Ticker("TWD=X", session=session)
        df_usd = usd.history(period="3mo")
        
        if not df_copper.empty and not df_usd.empty:
            # 整理並正規化 Index (去除時區資訊以利合併)
            df_copper.index = df_copper.index.tz_localize(None)
            df_usd.index = df_usd.index.tz_localize(None)
            
            # 重新命名 Close 欄位
            df_copper = df_copper[['Close']].rename(columns={'Close': 'HG=F'})
            df_usd = df_usd[['Close']].rename(columns={'Close': 'TWD=X'})
            
            # 合併 (使用 Inner Join 確保兩者都有數據)
            data = pd.concat([df_copper, df_usd], axis=1).dropna()
        
    except Exception as e:
        print(f"Error fetching real data: {e}")
        st.warning(f"無法連線至金融資料庫 ({e})，正在切換至模擬數據模式...")

    # 方法 2: 如果抓不到 (Data Frame 為空)，產生模擬數據 (Fallback)
    if data.empty:
        st.metric("系統狀態", "⚠️ 使用離線/模擬數據", "請檢查網路")
        
        # 產生過去 90 天的日期
        dates = pd.date_range(end=datetime.now(), periods=90)
        
        # 模擬銅價 (約 4.0 ~ 4.5 USD/lb -> 轉頓約 9000~10000)
        # 這裡為了展示，先生成 lbs 再轉
        import numpy as np
        base_price = 4.2
        random_walk = np.cumsum(np.random.randn(90) * 0.05)
        mock_prices = (base_price + random_walk) # USD/lb
        
        # 模擬匯率
        base_fx = 31.5
        fx_walk = np.cumsum(np.random.randn(90) * 0.02)
        mock_fx = base_fx + fx_walk
        
        data = pd.DataFrame({
            'HG=F': mock_prices, 
            'TWD=X': mock_fx
        }, index=dates)
        
        # 模擬標題告知
        st.info("目前顯示為「模擬數據」，僅供功能測試。無法從雲端抓取即時報價。")

    return data

# --- 核心函數：取得新聞 (模擬) ---
# --- 核心函數：取得新聞 (Google News RSS) ---
@st.cache_data(ttl=3600)
def get_news():
    news_items = []
    try:
        # Google News RSS 針對 "銅價" 關鍵字 (台灣地區)
        url = "https://news.google.com/rss/search?q=%E9%8A%85%E5%83%B9&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        
        # 設定 User-Agent 避免被擋
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # RSS namespace 可能會變，但通常 item 在 channel 下
            for item in root.findall('./channel/item')[:5]: # 取前 5 則
                title = item.find('title').text
                pubData = item.find('pubDate').text
                link = item.find('link').text
                
                # 簡單格式化日期
                try:
                    # RSS date format: "Fri, 02 Jan 2026 08:00:00 GMT" -> logic needs to be robust or simple
                    # 這裡直接用原始字串或簡單處理，避免複雜錯誤
                    date_str = pubData[:16] 
                except:
                    date_str = "Recent"

                # 簡單的情緒關鍵字標記 (僅供參考)
                sentiment = "中性"
                if any(x in title for x in ["漲", "升", "高", "熱", "強"]):
                    sentiment = "看漲"
                elif any(x in title for x in ["跌", "降", "低", "弱", "冷"]):
                    sentiment = "看跌"

                news_items.append({
                    "date": date_str,
                    "title": title,
                    "sentiment": sentiment,
                    "link": link
                })
        else:
            news_items.append({"date": "", "title": "無法取得新聞 (連線錯誤)", "sentiment": "錯誤", "link": "#"})
            
    except Exception as e:
        news_items.append({"date": "", "title": f"無法取得新聞: {str(e)}", "sentiment": "錯誤", "link": "#"})
    
    return news_items

# --- 主程式邏輯 ---
try:
    st.title("📊 電機材料 - 每日銅價決策看板")
    st.markdown(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # 1. 讀取數據
    df = get_data()
    
    # 數據檢查與列名處理
    copper_col = "HG=F"
    usd_col = "TWD=X"

    if copper_col not in df.columns or usd_col not in df.columns:
        st.error(f"數據中缺少 '{copper_col}' 或 '{usd_col}' 欄位。請檢查 yfinance 資料是否正常下載。")
        st.stop() # 停止程式運行，避免後續錯誤

    # 單位轉換: USD/lb -> USD/Ton (1 噸 = 2204.62 磅)
    df[copper_col] = df[copper_col] * 2204.62

    if df.empty or len(df) < 2: # 確保至少有兩天的數據來計算漲跌
        st.error("無法取得足夠的數據，請檢查網路連線或稍後再試。")
    else:
        # 提取最新數據
        copper_price = df[copper_col].iloc[-1]
        copper_prev = df[copper_col].iloc[-2]
        usd_twd = df[usd_col].iloc[-1]
        usd_twd_prev = df[usd_col].iloc[-2]

        # 計算漲跌幅
        copper_chg = (copper_price - copper_prev) / copper_prev * 100
        usd_chg = (usd_twd - usd_twd_prev) / usd_twd_prev * 100
        
        # 綜合成本計算 (銅價 x 匯率 = 台幣計價成本趨勢)
        twd_cost_now = copper_price * usd_twd
        twd_cost_prev = copper_prev * usd_twd_prev
        total_chg = (twd_cost_now - twd_cost_prev) / twd_cost_prev * 100

        # 計算移動平均線
        df['MA_Short'] = df[copper_col].rolling(window=ma_short).mean()
        df['MA_Long'] = df[copper_col].rolling(window=ma_long).mean()

        # 2. 決策儀表板 (Metrics)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("銅期貨 (USD/Ton)", f"${copper_price:,.2f}", f"{copper_chg:.2f}%")
        with col2:
            st.metric("美元匯率 (USD/TWD)", f"${usd_twd:.2f}", f"{usd_chg:.2f}%")
        with col3:
            st.metric("🇹🇼 台幣換算成本指標", f"{twd_cost_now:.2f}", f"{total_chg:.2f}%", 
                      help="綜合銅價與匯率的實際成本變動")

        st.divider()

        # 3. 趨勢判斷邏輯 (AI 建議)
        st.subheader("💡 今日開盤建議")

        # 取得最新均線值 (需處理 NaN)
        if len(df) >= ma_long:
            curr_ma_s = df['MA_Short'].iloc[-1]
            curr_ma_l = df['MA_Long'].iloc[-1]
            
            # 策略邏輯
            signal_score = 0
            tech_msg = ""
            
            if curr_ma_s > curr_ma_l:
                tech_msg = "短均線 > 長均線 (看漲)"
                signal_score = 1
            else:
                tech_msg = "短均線 < 長均線 (看跌)"
                signal_score = -1
                
            # 結合庫存水位
            final_advice = ""
            bg_color = "gray"
            
            if inventory_level == "低":
                if signal_score > 0: 
                    final_advice = "🟢 強力買進 (補庫存)"
                    bg_color = "#d4edda"
                else: 
                    final_advice = "🟡 分批佈局 (逢低買進)"
                    bg_color = "#fff3cd"
            elif inventory_level == "中":
                if signal_score > 0: 
                    final_advice = "🟢 適量買進"
                    bg_color = "#d4edda"
                else: 
                    final_advice = "🔴 暫緩進貨 / 觀望"
                    bg_color = "#f8d7da"
            elif inventory_level == "高":
                if signal_score > 0: 
                    final_advice = "🟡 持有觀望"
                    bg_color = "#fff3cd"
                else: 
                    final_advice = "🔴 停止進貨 (消耗庫存)"
                    bg_color = "#f8d7da"
            
            st.markdown(
                f"""
                <div style="padding: 15px; border-radius: 10px; background-color: {bg_color}; color: black; border: 1px solid #ccc;">
                    <h3 style="margin:0;">{final_advice}</h3>
                    <p style="margin:5px 0 0 0;">技術面分析: {tech_msg} | 庫存水位: {inventory_level}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )

            # --- 決策邏輯說明 ---
            with st.expander("ℹ️ 點擊查看詳細決策邏輯說明"):
                st.markdown("""
                **決策系統基於以下兩大因子綜合判斷：**
                
                1. **技術面趨勢 (移動平均線)**
                   - **看漲 (Golden Cross)**: 短期均線 (例如 5MA) 向上突破 長期均線 (例如 20MA)。代表短期動能強勁。
                   - **看跌 (Death Cross)**: 短期均線 向下穿過 長期均線。代表短期動能轉弱。
                   
                2. **庫存水位調整 (Inventory Admustment)**
                   - **低庫存**: 對價格上漲敏感，傾向積極買進或逢低佈局。
                   - **中庫存**: 穩健操作，順勢而為。
                   - **高庫存**: 風險控管優先，除非強烈看漲否則停止進貨。
                
                *注意：本系統採用 COMEX 銅期貨 (HG=F) 數據作為 LME 走勢的即時參考代理。*
                """)
            
            # 視覺化走勢
            st.write("")
            st.subheader("📈 LME/COMEX 銅價近3個月趨勢圖")
            fig = go.Figure()
            # 價格線
            fig.add_trace(go.Scatter(x=df.index, y=df[copper_col], name="銅期貨 (Proxy)", line=dict(color='#B87333', width=2)))
            # 均線
            fig.add_trace(go.Scatter(x=df.index, y=df['MA_Short'], name=f"{ma_short}MA", line=dict(color='blue', width=1, dash='dot')))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA_Long'], name=f"{ma_long}MA", line=dict(color='red', width=1, dash='dot')))
            
            fig.update_layout(
                xaxis_title="日期",
                yaxis_title="價格 (USD/Ton)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=30, b=20),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- 新聞專區 ---
            st.divider()
            st.subheader("📰 每日銅價/金屬相關新聞")
            news_list = get_news()
            
            for news in news_list:
                # 根據情緒標示顏色
                sentiment_color = "gray"
                if "看漲" in news['sentiment']: sentiment_color = "red" # 台股紅漲
                elif "看跌" in news['sentiment']: sentiment_color = "green" # 台股綠跌
                
                st.markdown(f"""
                - **{news['date']}** | <span style='color:{sentiment_color}'>[{news['sentiment']}]</span> [{news['title']}]({news['link']})
                """, unsafe_allow_html=True)
            
        else:
            st.warning("數據不足以計算設定的長期均線，請調整參數或等待累積更多數據。")

except Exception as e:
    st.error(f"系統發生錯誤: {e}")