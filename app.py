import json
import os
from datetime import datetime
import streamlit as st
from openai import OpenAI

# ---------------- 1. 页面基本配置 ----------------
st.set_page_config(
    page_title="AI 英语智能词汇空间",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- 2. 界面 CSS 样式 ----------------
taste_skill_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stMarkdown, p, div {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #0f172a;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1050px !important;
}

.stat-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 16px;
    text-align: left;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    margin-bottom: 12px;
}
.stat-title {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.stat-value {
    font-size: 1.35rem;
    color: #0f172a;
    font-weight: 700;
    margin-top: 4px;
}

div.stButton > button {
    width: 100%;
    border-radius: 10px !important;
    border: 1px solid #0f172a !important;
    background-color: #0f172a !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:hover {
    background-color: #334155 !important;
    border-color: #334155 !important;
}

.stExpander {
    border-radius: 12px !important;
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    margin-bottom: 14px !important;
}

.word-badge {
    display: inline-block;
    padding: 5px 12px;
    margin: 4px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    color: #334155;
    font-size: 0.85rem;
    font-weight: 500;
}
</style>
"""
st.markdown(taste_skill_css, unsafe_allow_html=True)

# ---------------- 3. 数据安全加载 ----------------
DB_FILE = "my_english_words.json"

def load_database():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_database(db):
    try:
        sorted_db = dict(sorted(db.items()))
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted_db, f, ensure_ascii=False, indent=4)
    except:
        pass

api_key = "ark-dccbbfe2-ee90-43c2-914c-7bac589bfd2d-75676"
try:
    if "DEEPSEEK_API_KEY" in st.secrets:
        api_key = st.secrets["$ARK_API_KEY"]
except:
    pass

client = OpenAI(
    api_key=api_key if api_key else "ark-dccbbfe2-ee90-43c2-914c-7bac589bfd2d-75676", 
    base_url="https://ark.cn-beijing.volces.com/api/v3/responses"
)

# 优化后的生成函数：精简提示词 + 限制 max_tokens
def generate_word_card(word):
    prompt = f"""
    请为英语单词 "{word}" 提供极简的学习卡片信息，严格按照以下 JSON 格式返回，不要包含 markdown 标记：
    {{
      "word": "{word}",
      "phonetic": "国际音标（英/美）",
      "meaning": "中文意思（包含词性）",
      "phrases": ["常用词组1", "常用词组2", "常用词组3"],
      "usage": "常用方法、语法考点或易混淆点说明",
      "example": "包含该单词的高频例句（附中文翻译）"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300  # 限制最大输出 Token，防止溢出和高额消耗
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        return json.loads(content)
    except:
        return None

# ---------------- 4. 侧边栏交互 ----------------
with st.sidebar:
    st.subheader("🔥 连续打卡")
    if 'streak_days' not in st.session_state: st.session_state.streak_days = 1
    if 'last_checkin' not in st.session_state: st.session_state.last_checkin = None
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    if st.session_state.last_checkin == today_str:
        st.success(f"今日已打卡 ({st.session_state.streak_days} 天)")
    else:
        if st.button("📅 点击打卡"):
            st.session_state.last_checkin = today_str
            st.success("打卡成功！")
            st.rerun()

    st.markdown("---")
    st.subheader("➕ 添加生词")
    new_word = st.text_input("输入英文单词：").strip()
    if st.button("✨ AI 一键解析"):
        if not new_word:
            st.warning("请输入有效单词！")
        else:
            if not api_key:
                st.error("请先配置 DEEPSEEK_API_KEY！")
            else:
                db = load_database()
                first_letter = new_word[0].upper()
                if first_letter in db and any(item['word'].lower() == new_word.lower() for item in db[first_letter]):
                    st.info("单词已存在！")
                else:
                    with st.spinner("AI 正在构建卡片..."):
                        card_data = generate_word_card(new_word)
                        if card_data:
                            if first_letter not in db: db[first_letter] = []
                            db[first_letter].append(card_data)
                            save_database(db)
                            st.success(f"成功添加！")
                            st.rerun()
                        else:
                            st.error("生成失败，请检查 API Key。")

# ---------------- 5. 主界面 ----------------
st.title("⚡ 英语智能词汇空间")
st.caption("Designed with Taste & Precision")
st.markdown(" ")

current_db = load_database()
all_items = [item for letter in current_db.keys() for item in current_db[letter]]
all_words = [item['word'] for item in all_items]
word_count = len(all_words)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-card"><div class="stat-title">已收词</div><div class="stat-value">{word_count}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div class="stat-title">勋章</div><div class="stat-value">{"新星" if word_count<5 else "达人"}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="stat-title">打卡</div><div class="stat-value">{st.session_state.streak_days}天</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-card"><div class="stat-title">目标</div><div class="stat-value">{word_count}/10</div></div>', unsafe_allow_html=True)

st.markdown("---")

# 只保留 词库 和 闪卡 两个核心 Tab
tab1, tab2 = st.tabs(["📖 词库", "🎴 闪卡"])

with tab1:
    if not current_db:
        st.info("词库空空如也，请在左侧边栏添加第一个生词！")
    else:
        search_query = st.text_input("🔍 搜索单词...", "").strip().lower()
        with st.expander("📚 全部生词速览", expanded=False):
            st.markdown("".join([f'<span class="word-badge">{w}</span>' for w in all_words]), unsafe_allow_html=True)
        
        for letter in sorted(current_db.keys()):
            matched = [item for item in current_db[letter] if not search_query or search_query in item['word'].lower()]
            if matched:
                with st.expander(f"📁 组: {letter} ({len(matched)}个)", expanded=True):
                    for item in matched:
                        st.subheader(item['word'])
                        st.caption(f"💡 {item.get('phonetic', '')}")
                        st.audio(f"https://dict.youdao.com/dictvoice?audio={item['word']}&type=2", format="audio/mp3")
                        
                        st.markdown(f"**【释义】** {item.get('meaning', '')}")
                        
                        # 仅保留常用词组
                        phrases = item.get('phrases', [])
                        if phrases:
                            st.markdown(f"**【常用词组】** " + " | ".join([f"`{p}`" for p in phrases]))
                            
                        if item.get('usage'):
                            st.markdown(f"**【用法考点】** {item.get('usage', '')}")
                        
                        st.info(f"高频例句：_{item.get('example', '')}_")
                        st.markdown("---")

with tab2:
    if not all_items: 
        st.warning("请先添加单词。")
    else:
        if 'idx' not in st.session_state: st.session_state.idx = 0
        if 'ans' not in st.session_state: st.session_state.ans = False
        card = all_items[st.session_state.idx % len(all_items)]
        st.markdown(f"<h2 style='text-align: center;'>{card['word']}</h2>", unsafe_allow_html=True)
        if st.session_state.ans:
            st.success(card.get('meaning', ''))
            if card.get('phrases'):
                st.info("常用词组: " + " | ".join(card['phrases']))
        if st.button("翻转卡片"):
            st.session_state.ans = not st.session_state.ans
            st.rerun()
        if st.button("下一个"):
            st.session_state.idx += 1
            st.session_state.ans = False
            st.rerun()
