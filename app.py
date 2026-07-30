import json
import os
import random
from datetime import datetime
import streamlit as st
from openai import OpenAI

# ---------------- 1. 页面基本配置 ----------------
st.set_page_config(
    page_title="AI 英语智能 3D 灵动游乐场",
    page_icon="🎮",
    layout="wide"
)

# ---------------- 2. 🎨 引入 Plus Jakarta Sans 字体与 3D 呼吸感 CSS ----------------
tactile_3d_css = """
<style>
/* 🔤 引入国际顶尖 Web 字体 Plus Jakarta Sans */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, p, div, input, button {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* 全局增加呼吸感间距 */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px !important;
}

/* 📊 自定义 3D 看板卡片（防止数据重叠拥挤） */
.stat-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 6px 0 #cbd5e1, 0 10px 15px rgba(0,0,0,0.05);
    margin-bottom: 12px;
}
.stat-title {
    font-size: 0.85rem;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 6px;
}
.stat-value {
    font-size: 1.6rem;
    color: #1e293b;
    font-weight: 800;
}

/* 🔘 3D 物理悬浮与凹陷按压按钮 */
div.stButton > button {
    border-radius: 14px !important;
    border: none !important;
    background: linear-gradient(180deg, #6366f1 0%, #4f46e5 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1.4rem !important;
    box-shadow: 0 6px 0 #3730a3, 0 10px 15px rgba(0,0,0,0.12) !important;
    transition: all 0.1s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    top: 0px;
    margin-top: 8px !important;
    margin-bottom: 12px !important;
}

div.stButton > button:hover {
    top: -2px;
    box-shadow: 0 8px 0 #3730a3, 0 14px 20px rgba(0,0,0,0.18) !important;
}

div.stButton > button:active {
    top: 4px !important;
    box-shadow: 0 2px 0 #3730a3, 0 4px 6px rgba(0,0,0,0.2) !important;
}

/* 🗂️ 3D 悬浮卡片 (stExpander) 增加外边距与行高 */
.stExpander {
    border-radius: 16px !important;
    background: rgba(255, 255, 255, 0.9) !important;
    backdrop-filter: blur(12px);
    border: 2px solid rgba(255, 255, 255, 0.7) !important;
    box-shadow: 0 8px 20px -5px rgba(0,0,0,0.06) !important;
    transition: all 0.25s ease !important;
    margin-bottom: 20px !important; /* 增加卡片间距 */
    padding: 6px !important;
}
.stExpander:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 25px -8px rgba(0,0,0,0.1) !important;
}

/* 🏷️ 3D 实体胶囊标签 */
.badge-tag {
    display: inline-block;
    padding: 8px 16px;
    margin: 6px;
    border-radius: 12px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 0 #cbd5e1, 0 6px 10px rgba(0,0,0,0.04);
    color: #1e293b;
    font-weight: 700;
    font-size: 0.9rem;
}

/* 🎴 3D 闪卡展示容器 */
.flashcard-box {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 24px;
    padding: 40px 20px;
    text-align: center;
    border: 3px solid #6366f1;
    box-shadow: 0 12px 0 #3730a3, 0 20px 30px rgba(0,0,0,0.1);
    margin: 24px 0;
}

/* Tab 标签页间距加大 */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 8px 16px !important;
}
</style>
"""
st.markdown(tactile_3d_css, unsafe_allow_html=True)


# ---------------- 3. 🎨 自定义背景与样式注入 ----------------
st.sidebar.header("🎨 网页风格设置")
bg_option = st.sidebar.selectbox(
    "选择背景风格",
    ["默认纯净白", "深色极客黑", "莫兰迪柔蓝", "暖阳渐变", "自定义颜色", "自定义背景图片URL"]
)

custom_css = ""
if bg_option == "默认纯净白":
    custom_css = "<style>.stApp { background-color: #F8FAFC; color: #0F172A; }</style>"
elif bg_option == "深色极客黑":
    custom_css = "<style>.stApp { background-color: #0E1117; color: #FAFAFA; } .stExpander { background: rgba(22, 27, 34, 0.85) !important; color: white !important; } .badge-tag { background: #161b22; color: #58a6ff; box-shadow: 0 4px 0 #30363d; } .stat-card { background: #161b22; border-color: #30363d; box-shadow: 0 6px 0 #30363d; } .stat-title { color: #8b949e; } .stat-value { color: #f0f6fc; }</style>"
elif bg_option == "莫兰迪柔蓝":
    custom_css = "<style>.stApp { background-color: #EBF2F7; color: #1E293B; }</style>"
elif bg_option == "暖阳渐变":
    custom_css = "<style>.stApp { background: linear-gradient(135deg, #FFDEE9 0%, #B5FFFC 100%); color: #2C3E50; }</style>"
elif bg_option == "自定义颜色":
    user_color = st.sidebar.color_picker("拾取喜欢的背景颜色", "#F0F2F6")
    custom_css = f"<style>.stApp {{ background-color: {user_color}; }}</style>"
elif bg_option == "自定义背景图片URL":
    img_url = st.sidebar.text_input("请输入图片 URL:", "https://images.unsplash.com/photo-1519681393784-d120267933ba")
    if img_url:
        custom_css = f"""
        <style>
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 2.5rem;
            border-radius: 24px;
            margin-top: 1rem;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }}
        </style>
        """
st.markdown(custom_css, unsafe_allow_html=True)


# ---------------- 4. 大模型客户端与数据管理 ----------------
# ⚠️ 请确保填入真实的 API Key
import streamlit as st
from openai import OpenAI

# 优先读取 Secrets 中的 Key，如果没有配置则读取本地默认 Key
api_key = st.secrets.get("DEEPSEEK_API_KEY", "你的默认KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

DB_FILE = "my_english_words.json"

def load_database():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_database(db):
    sorted_db = dict(sorted(db.items()))
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_db, f, ensure_ascii=False, indent=4)

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
    words_str = ", ".join(selected_words)
    prompt = f"请用以下英文单词编写一段幽默极富想象力的短故事（100 词左右）：{words_str}\n故事中使用的生词请加粗，并在下方附排版清晰的中文翻译。"
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def evaluate_user_sentence(word, user_sentence):
    prompt = f"目标单词: '{word}'\n用户句子: '{user_sentence}'\n请像外教一样点评：1.评分(0-100) 2.语法纠错 3.地道润色句。鼓励语气，美观排版。"
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

def generate_quiz_question(word_item):
    prompt = f"根据单词 '{word_item['word']}'({word_item['meaning']}) 出一道包含下划线 ___ 的选择填空题。严格返回 JSON: {{\n\"question\": \"句子...\",\n\"options\": [\"正确词\", \"干扰1\", \"干扰2\", \"干扰3\"],\n\"answer\": \"正确词\",\n\"explanation\": \"解析\"\n}}"
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


# ---------------- 5. 侧边栏打卡与添加生词 ----------------
st.sidebar.markdown("---")
st.sidebar.header("🔥 学习连续打卡")

if 'streak_days' not in st.session_state:
    st.session_state.streak_days = 1
if 'last_checkin' not in st.session_state:
    st.session_state.last_checkin = None

today_str = datetime.now().strftime("%Y-%m-%d")
if st.session_state.last_checkin == today_str:
    st.sidebar.success(f"🎉 今日已打卡！已连续学习 {st.session_state.streak_days} 天")
else:
    if st.sidebar.button("📅 点击完成今日学习打卡"):
        st.session_state.last_checkin = today_str
        st.sidebar.success("打卡成功！")
        st.balloons()
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("➕ 快捷添加生词")
new_word = st.sidebar.text_input("输入英文单词：").strip()

if st.sidebar.button("✨ 让 AI 一键解析"):
    if not new_word:
        st.sidebar.warning("请输入有效单词！")
    else:
        db = load_database()
        first_letter = new_word[0].upper()
        if first_letter in db and any(item['word'].lower() == new_word.lower() for item in db[first_letter]):
            st.sidebar.info(f"单词 '{new_word}' 已经存在！")
        else:
            with st.spinner(f"🚀 AI 正在生成卡片..."):
                card_data = generate_word_card(new_word)
                if card_data:
                    if first_letter not in db:
                        db[first_letter] = []
                    db[first_letter].append(card_data)
                    save_database(db)
                    st.sidebar.success(f"成功收集 '{new_word}'！")
                    st.toast(f"🎉 成功解锁新词汇: {new_word}!")
                    st.rerun()


# ---------------- 6. 成就仪表盘与主界面 ----------------
st.title("🎮 AI 英语智能 3D 灵动游乐场")
st.markdown(" ")

current_db = load_database()
all_items = [item for letter in current_db.keys() for item in current_db[letter]]
all_words = [item['word'] for item in all_items]
word_count = len(all_words)

# 🏆 游戏化等级
if word_count < 5:
    level_title = "🥉 词汇新星"
    next_goal = 5
elif word_count < 15:
    level_title = "🥈 词汇达人"
    next_goal = 15
elif word_count < 30:
    level_title = "🥇 词汇大师"
    next_goal = 30
else:
    level_title = "👑 词汇霸主"
    next_goal = 50

# 📊 优化版数据看板：使用 HTML 卡片彻底解决文字拥挤问题
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="stat-card"><div class="stat-title">📚 已收集词汇</div><div class="stat-value">{word_count} 个</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-card"><div class="stat-title">🏆 当前段位勋章</div><div class="stat-value">{level_title}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-card"><div class="stat-title">🔥 连续打卡</div><div class="stat-value">{st.session_state.streak_days} 天</div></div>', unsafe_allow_html=True)
with col4:
    progress_val = min(1.0, word_count / next_goal)
    st.markdown(f'<div class="stat-card"><div class="stat-title">📈 下一段位进度</div><div class="stat-value">{word_count}/{next_goal}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# 5大核心功能标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📖 3D 词库墙", 
    "🎴 Anki 闪卡复习", 
    "🪄 串词脑洞故事", 
    "✍️ AI 私教造句", 
    "⚔️ 闯关挑战赛"
])

# --- Tab 1: 3D 词库墙 ---
with tab1:
    if not current_db:
        st.info("你的单词本目前空空如也，快在左侧边栏添加第一个生词吧！")
    else:
        search_query = st.text_input("🔍 搜索单词或中文释义：", "").strip().lower()
        st.markdown(" ")
        
        with st.expander(f"📚 已解锁的 3D 生词胶囊墙 (点击展开)", expanded=False):
            badges_html = "".join([f'<span class="badge-tag">{w}</span>' for w in all_words])
            st.markdown(badges_html, unsafe_allow_html=True)
        
        st.markdown(" ")
        
        for letter in sorted(current_db.keys()):
            matched_items = [
                item for item in current_db[letter]
                if not search_query or search_query in item['word'].lower() or search_query in item.get('meaning', '').lower()
            ]
            if matched_items:
                with st.expander(f"📁 字母组: {letter} ({len(matched_items)} 个单词)", expanded=True):
                    for item in matched_items:
                        st.markdown(f"### **{item['word']}** &nbsp;&nbsp; `<span style='color:#6366f1;'>💡 {item.get('phonetic', '')}</span>`", unsafe_allow_html=True)
                        audio_url = f"https://dict.youdao.com/dictvoice?audio={item['word']}&type=2"
                        st.audio(audio_url, format="audio/mp3")
                        
                        st.markdown(f"**【释义】** {item.get('meaning', '')}")
                        if item.get('roots'):
                            st.markdown(f"**【词根拆解】** 🧩 {item['roots']}")
                        if item.get('memory_hook'):
                            st.markdown(f"**【记忆窍门】** 🧠 {item['memory_hook']}")
                        if item.get('phrases'):
                            st.markdown(f"**【常用词组】** " + " | ".join([f"`{p}`" for p in item['phrases']]))
                        st.markdown(f"**【用法考点】** {item.get('usage', '')}")
                        st.markdown(f"**【高频例句】** _{item.get('example', '')}_")
                        st.markdown("<br>", unsafe_allow_html=True)

# --- Tab 2: Anki 闪卡复习模式 ---
with tab2:
    st.header("🎴 Anki 式 3D 闪卡高效复习")
    st.write("尝试先在脑海中回忆单词含义，点击翻转查看是否正确！")
    
    if not all_items:
        st.warning("词库为空，先去添加几个生词吧！")
    else:
        if 'card_idx' not in st.session_state:
            st.session_state.card_idx = 0
        if 'show_answer' not in st.session_state:
            st.session_state.show_answer = False
            
        current_card = all_items[st.session_state.card_idx % len(all_items)]
        
        st.markdown(f"""
        <div class="flashcard-box">
            <h1 style="font-size: 3.5rem; color: #4f46e5; margin-bottom: 8px;">{current_card['word']}</h1>
            <p style="font-size: 1.2rem; color: #64748b;">💡 {current_card.get('phonetic', '')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 翻转卡片 (查看答案)"):
                st.session_state.show_answer = not st.session_state.show_answer
        with c2:
            if st.button("➡️ 下一个单词"):
                st.session_state.card_idx += 1
                st.session_state.show_answer = False
                st.rerun()

        if st.session_state.show_answer:
            st.success(f"**【释义】** {current_card.get('meaning', '')}")
            if current_card.get('memory_hook'):
                st.info(f"🧠 **记忆窍门**：{current_card['memory_hook']}")
            st.write(f"例句：_{current_card.get('example', '')}_")

# --- Tab 3: 串词成章写故事 ---
with tab3:
    st.header("🪄 将生词变成脑洞故事")
    if len(all_words) < 2:
        st.warning("请至少收集 2 个单词后再开启故事模式哦！")
    else:
        selected_story_words = st.multiselect("勾选 2~5 个词汇：", all_words, default=all_words[:min(3, len(all_words))])
        if st.button("🚀 启动 AI 灵感撰写故事"):
            if not selected_story_words:
                st.warning("请选择单词！")
            else:
                with st.spinner("✨ AI 正在编织故事中..."):
                    story_res = generate_story_from_words(selected_story_words)
                    st.success("生成成功！")
                    st.markdown(story_res)

# --- Tab 4: AI 造句私教 ---
with tab4:
    st.header("✍️ 实时造句诊断室")
    if not all_words:
        st.warning("请先添加生词！")
    else:
        target_word = st.selectbox("选择你想练习的单词：", all_words)
        user_sent = st.text_area(f"用 '{target_word}' 造一个英文句子：", placeholder="Type your sentence here...")
        if st.button("📝 提交给 AI 外教评审"):
            if not user_sent.strip():
                st.warning("请输入句子！")
            else:
                with st.spinner("👩‍🏫 AI 外教批改中..."):
                    eval_res = evaluate_user_sentence(target_word, user_sent)
                    st.markdown(eval_res)

# --- Tab 5: 闯关挑战赛 ---
with tab5:
    st.header("⚔️ 词汇实时闯关挑战")
    if not all_items:
        st.warning("词库为空，先添加一些单词吧！")
    else:
        if st.button("🎲 换一道挑战题") or 'current_quiz' not in st.session_state:
            random_item = random.choice(all_items)
            with st.spinner("🎲 AI 正在现场出题..."):
                st.session_state.current_quiz = generate_quiz_question(random_item)

        quiz = st.session_state.get('current_quiz')
        if quiz:
            st.subheader(f"❓ 请填空：{quiz['question']}")
            user_choice = st.radio("请选择正确单词：", quiz['options'], key="quiz_choice")
            
            if st.button("🎯 验证答案"):
                if user_choice == quiz['answer']:
                    st.balloons()
                    st.success("🎉 太棒了，完全正确！")
                else:
                    st.error(f"❌ 遗憾答错！正确答案是：**{quiz['answer']}**")
                st.info(f"💡 **考点解析**：{quiz['explanation']}")
