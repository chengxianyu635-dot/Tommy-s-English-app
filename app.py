import json
import os
import random
from datetime import datetime
import streamlit as st
from openai import OpenAI

# ---------------- 1. 页面基本配置与移动端视口优化 ----------------
st.set_page_config(
    page_title="AI 英语智能灵动游乐场",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- 2. 引入字体与移动端自适应 CSS ----------------
responsive_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, p, div {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

.stat-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px;
    text-align: center;
    box-shadow: 0 4px 0 #cbd5e1;
    margin-bottom: 10px;
}
.stat-title {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 600;
}
.stat-value {
    font-size: 1.2rem;
    color: #1e293b;
    font-weight: 800;
}

div.stButton > button {
    width: 100%;
    border-radius: 12px !important;
    border: none !important;
    background: linear-gradient(180deg, #6366f1 0%, #4f46e5 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    padding: 0.6rem 1rem !important;
    box-shadow: 0 4px 0 #3730a3 !important;
}

.stExpander {
    border-radius: 12px !important;
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid #e2e8f0 !important;
    margin-bottom: 12px !important;
}

.word-badge {
    display: inline-block;
    padding: 4px 10px;
    margin: 3px;
    background: #f1f5f9;
    border-radius: 8px;
    color: #334155;
    font-size: 0.85rem;
    font-weight: 600;
}
</style>
"""
st.markdown(responsive_css, unsafe_allow_html=True)

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

api_key = "sk-8af6747811354405b2dd56738b0609b5"
try:
    if "DEEPSEEK_API_KEY" in st.secrets:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
except:
    pass

client = OpenAI(
    api_key=api_key if api_key else "sk-8af6747811354405b2dd56738b0609b5", 
    base_url="https://api.deepseek.com"
)

def generate_word_card(word):
    prompt = f"""
    请为英语单词 "{word}" 提供详细的学习卡片信息，必须严格按照以下 JSON 格式返回，不要包含 markdown 标记：
    {{
      "word": "{word}",
      "phonetic": "国际音标（英/美）",
      "meaning": "中文意思（包含词性）",
      "roots": "词根/前缀/后缀分解及逻辑",
      "memory_hook": "趣味谐音/联想/图像记忆小窍门",
      "phrases": ["常用词组1", "常用词组2"],
      "usage": "常用方法、语法考点或易混淆点说明",
      "example": "包含该单词的高频例句（附中文翻译）"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        return json.loads(content)
    except:
        return None

def generate_story_from_words(selected_words):
    try:
        prompt = f"请用以下英文单词编写一段幽默的短故事（100字左右）：{', '.join(selected_words)}。生词加粗，附带中文翻译。"
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"生成故事失败: {e}"

def evaluate_user_sentence(word, user_sentence):
    try:
        prompt = f"目标单词: '{word}'\n用户句子: '{user_sentence}'\n请像外教一样点评：1.评分(0-100) 2.语法纠错 3.地道润色。"
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"评估失败: {e}"

def generate_quiz_question(word_item):
    try:
        prompt = f"根据单词 '{word_item['word']}'({word_item['meaning']}) 出一道选择填空题。严格返回 JSON: {{\n\"question\": \"句子...\",\n\"options\": [\"正确词\", \"干扰1\", \"干扰2\", \"干扰3\"],\n\"answer\": \"正确词\",\n\"explanation\": \"解析\"\n}}"
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        return json.loads(content)
    except:
        return {"question": f"What is the meaning of {word_item['word']}?", "options": [word_item['word'], "A", "B", "C"], "answer": word_item['word'], "explanation": "默认测验"}

# ---------------- 4. 侧边栏交互 ----------------
with st.sidebar:
    st.header("🔥 连续打卡")
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
    st.header("➕ 添加生词")
    new_word = st.text_input("输入英文单词：").strip()
    if st.button("✨ AI 一键解析"):
        if not new_word:
            st.warning("请输入有效单词！")
        else:
            if not api_key:
                st.error("请先在云端 Secrets 配置 DEEPSEEK_API_KEY！")
            else:
                db = load_database()
                first_letter = new_word[0].upper()
                if first_letter in db and any(item['word'].lower() == new_word.lower() for item in db[first_letter]):
                    st.info("单词已存在！")
                else:
                    with st.spinner("AI 正在生成卡片..."):
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
st.title("🎮 英语智能词汇空间")

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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📖 词库", "🎴 闪卡", "🪄 故事", "✍️ 造句", "⚔️ 测验"
])

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
                        if item.get('roots'):
                            st.markdown(f"**【词根拆解】** 🧩 {item['roots']}")
                        if item.get('memory_hook'):
                            st.markdown(f"**【记忆窍门】** 🧠 {item['memory_hook']}")
                        
                        # ✨ 恢复的常用词组与用法考点
                        phrases = item.get('phrases', [])
                        if phrases:
                            st.markdown(f"**【常用词组】** " + " | ".join([f"`{p}`" for p in phrases]))
                        if item.get('usage'):
                            st.markdown(f"**【用法考点】** {item.get('usage', '')}")
                        
                        st.info(f"高频例句：_{item.get('example', '')}_")

with tab2:
    if not all_items: st.warning("请先添加单词。")
    else:
        if 'idx' not in st.session_state: st.session_state.idx = 0
        if 'ans' not in st.session_state: st.session_state.ans = False
        card = all_items[st.session_state.idx % len(all_items)]
        st.markdown(f"<h2 style='text-align: center;'>{card['word']}</h2>", unsafe_allow_html=True)
        if st.session_state.ans:
            st.success(card.get('meaning', ''))
        if st.button("翻转卡片"):
            st.session_state.ans = not st.session_state.ans
            st.rerun()
        if st.button("下一个"):
            st.session_state.idx += 1
            st.session_state.ans = False
            st.rerun()

with tab3:
    if len(all_words) < 2: st.warning("至少需要2个词。")
    else:
        sel = st.multiselect("选词：", all_words, default=all_words[:min(2, len(all_words))])
        if st.button("生成故事"): st.markdown(generate_story_from_words(sel))

with tab4:
    if not all_words: st.warning("请添加词汇。")
    else:
        t = st.selectbox("选词", all_words)
        s = st.text_area("造句：")
        if st.button("提交"): st.markdown(evaluate_user_sentence(t, s))

with tab5:
    if not all_items: st.warning("词库为空。")
    else:
        if st.button("换一题") or 'q' not in st.session_state:
            st.session_state.q = generate_quiz_question(random.choice(all_items))
        q = st.session_state.q
        st.subheader(q['question'])
        ans = st.radio("选项", q['options'])
        if st.button("验证"):
            if ans == q['answer']: st.success("正确！")
            else: st.error(f"错误，答案是 {q['answer']}")
