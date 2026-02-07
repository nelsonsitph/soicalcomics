import streamlit as st
import requests
import json
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from io import BytesIO
import numpy as np

# --- 1. 現代化 UI：Threads 黑化極簡風格 (加強版) ---
st.set_page_config(page_title="Grok Social Lab", layout="wide")

st.markdown("""
    <style>
    /* 全局背景 */
    .stApp { background-color: #000; color: #fff; font-family: -apple-system, sans-serif; }
    
    /* 狀態燈號 */
    .status-dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; border: 1px solid #555; }
    .status-on { background-color: #00ff00; box-shadow: 0 0 10px #00ff00; }
    .status-off { background-color: #222; }
    
    /* 卡片式容器 */
    .card { background-color: #121212; padding: 30px; border-radius: 24px; border: 1px solid #262626; margin-bottom: 30px; }
    
    /* 顯眼的生成按鈕 */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #0095F6, #00C2FF);
        color: white;
        border: none;
        padding: 15px 30px;
        font-size: 18px;
        font-weight: 700;
        border-radius: 12px;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 149, 246, 0.3);
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 149, 246, 0.5);
    }

    /* 下載按鈕樣式 */
    .download-btn {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold;
    }

    /* 情感標籤 */
    .emotion-tag { display: inline-block; padding: 6px 12px; border-radius: 15px; font-size: 13px; margin-right: 8px; font-weight: bold; color: #fff; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 純 Grok (xAI) API 呼叫 (不使用 OpenAI 函式庫) ---
def grok_chat(prompt, system_message):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {st.secrets['GROK_API_KEY']}", "Content-Type": "application/json"}
    data = {
        "model": "grok-4",
        "messages": [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']

def grok_image(prompt):
    url = "https://api.x.ai/v1/images/generate"
    headers = {"Authorization": f"Bearer {st.secrets['GROK_API_KEY']}", "Content-Type": "application/json"}
    data = {"model": "grok-imagine-image", "prompt": prompt, "n": 1, "size": "1024x1024"}
    
    response = requests.post(url, headers=headers, json=data)
    res_json = response.json()
    
    if response.status_code == 200 and 'data' in res_json:
        return res_json['data'][0]['url']
    else:
        st.error(f"⚠️ 影像生成失敗: {res_json.get('error', '請檢查餘額或 API 設定')}")
        return None

# --- 3. 狀態初始化 ---
if "lights" not in st.session_state:
    st.session_state.lights = {"event": False, "dev": False, "trigger": False, "cons": False}
if "comic_img" not in st.session_state:
    st.session_state.comic_img = None

# --- 4. 介面佈局 ---
st.title("✨ Grok 社交解讀實驗室")
st.caption("Educational Psychologist Professional Suite • 2026 Edition")

# --- Step 1: 情境解讀與自動分析 ---
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Step 1: 社交情境重構")
    
    # 動態燈號顯示
    l1, l2, l3, l4 = st.columns(4)
    st_map = {True: "status-on", False: "status-off"}
    l1.markdown(f'<span class="status-dot {st_map[st.session_state.lights["event"]]}"></span> 環境/時間', unsafe_allow_html=True)
    l2.markdown(f'<span class="status-dot {st_map[st.session_state.lights["dev"]]}"></span> 行為發展', unsafe_allow_html=True)
    l3.markdown(f'<span class="status-dot {st_map[st.session_value["lights"]["trigger"] if "lights" in st.session_state else False]}"></span> 引爆點', unsafe_allow_html=True)
    # 修正一個變數引用錯誤
    l3.markdown(f'<span class="status-dot {st_map[st.session_state.lights["trigger"]]}"></span> 引爆點', unsafe_allow_html=True)
    l4.markdown(f'<span class="status-dot {st_map[st.session_state.lights["cons"]]}"></span> 事件後果', unsafe_allow_html=True)

    user_story = st.text_area("請口述或輸入社交事件內容...", height=120, placeholder="例如：小息在操場玩球時，我突然搶了同學的球，同學生氣地推了我，結果大家都哭了。")

    if user_story:
        with st.spinner("Grok 正在分析行為鏈 (Cognitive Analysis)..."):
            sys_p = "你是一位教育心理學家。請分析故事是否包含以下四個元素，僅以 JSON 格式輸出：{'event':bool, 'dev':bool, 'trigger':bool, 'cons':bool}"
            try:
                analysis = grok_chat(user_story, sys_p)
                st.session_state.lights = json.loads(analysis.replace("'", '"'))
            except: pass

    # 改為下拉式選單 (Selectbox)
    style = st.selectbox("🎨 選擇漫畫風格", ["火柴人 (Stick Figure)", "可愛貼紙 (Cute Sticker)", "日系漫畫 (Manga)", "美式漫畫 (Comic)"])

    st.write("") # 間距
    if st.button("🚀 生成無臉漫畫畫板 (Generate Comic)"):
        with st.spinner("Grok 正在為您繪製專屬社交場景..."):
            prompt = f"A 4-panel comic storyboard, style: {style}. Story: {user_story}. IMPORTANT: Characters MUST have BLANK FACES. Include EMPTY large speech and thought bubbles."
            img_url = grok_image(prompt)
            if img_url:
                st.session_state.comic_img = Image.open(BytesIO(requests.get(img_url).content))
    st.markdown('</div>', unsafe_allow_html=True)

# --- Step 2: 互動創作區 (Canvas) ---
if st.session_state.comic_img:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Step 2: 情感投射與創作")
    st.markdown("請在下方畫板為角色添上**五官表情**、繪製**對話/想法**，並以顏色標記**情緒**。")
    
    col_tools, col_canvas = st.columns([1, 3])
    
    with col_tools:
        st.markdown("**🎨 臨床繪圖指南**")
        st.markdown('<span class="emotion-tag" style="background-color:#FF3B30;">🔴 憤怒/敵意</span>', unsafe_allow_html=True)
        st.markdown('<span class="emotion-tag" style="background-color:#007AFF;">🔵 傷心/憂鬱</span>', unsafe_allow_html=True)
        st.markdown('<span class="emotion-tag" style="background-color:#FFCC00; color:#000;">🟡 緊張/驚慌</span>', unsafe_allow_html=True)
        st.markdown('<span class="emotion-tag" style="background-color:#4CD964;">🟢 快樂/友善</span>', unsafe_allow_html=True)
        
        st.write("---")
        # 繪圖工具選單
        tool = st.radio("選擇繪圖工具", ["freedraw (表情/泡泡)", "text (寫下文字)", "circle (情緒圈選)", "line (指引線)"])
        stroke_color = st.color_picker("選擇顏色", "#FF3B30")
        stroke_width = st.slider("筆觸大小", 1, 15, 4)
        
        st.warning("💡 **操作秘訣：**\n1. 用 `freedraw` 畫出眼神與嘴巴。\n2. 用 `circle` 在角色頭部畫一圈情緒顏色。\n3. 用 `text` 在氣泡內寫入內容。")

    with col_canvas:
        # 互動畫布
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_image=st.session_state.comic_img,
            drawing_mode=tool,
            key="social_canvas",
            height=700,
            width=700,
            update_streamlit=True,
        )

    # --- Step 3: 輸出成果 ---
    st.markdown("---")
    st.subheader("Step 3: 儲存與回顧")
    if canvas_result.image_data is not None:
        # 將畫布內容合成並準備下載
        res_img = Image.fromarray(canvas_result.image_data.astype("uint8")).convert("RGB")
        buf = BytesIO()
        res_img.save(buf, format="JPEG")
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.download_button(
                label="💾 點此下載我的社交故事 (Download JPG)",
                data=buf.getvalue(),
                file_name="social_story_result.jpg",
                mime="image/jpeg",
                help="點擊下載完整作品到您的電腦或手機"
            )
    st.markdown('</div>', unsafe_allow_html=True)