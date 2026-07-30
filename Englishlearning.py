import json
import os
from openai import OpenAI

# 1. 初始化客户端（换成你刚刚测试成功的 API Key）
client = OpenAI(
    api_key="sk-8af6747811354405b2dd56738b0609b5am", 
    base_url="https://api.deepseek.com"
)

# 定义本地保存单词的数据库文件名
DB_FILE = "my_english_words.json"

def load_database():
    """读取本地单词库文件"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_database(db):
    """按首字母排序并保存到本地 JSON 文件"""
    sorted_db = dict(sorted(db.items()))
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_db, f, ensure_ascii=False, indent=4)

def generate_word_card(word):
    """调用大模型，让 AI 自动生成单词的音标、意思、词组、用法和例句"""
    prompt = f"""
    请为英语单词 "{word}" 提供详细的学习卡片信息，必须严格按照以下 JSON 格式返回，不要包含任何 markdown 代码块标记或其他多余废话：
    {{
      "word": "{word}",
      "phonetic": "国际音标（英/美）",
      "meaning": "中文意思（包含词性，如 n. / v.）",
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
        
        # 清理可能存在的 markdown 符号
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        return json.loads(content)
    except Exception as e:
        print(f"生成单词 [{word}] 失败: {e}")
        return None

def main():
    print("=== 欢迎使用 AI 英语单词本小工具 ===")
    print("提示：随时输入 q 可以退出程序。\n")
    
    while True:
        word = input("请输入你想整理的英文生词: ").strip()
        if word.lower() == 'q':
            print("再见！继续加油背单词哦！")
            break
        if not word:
            continue
            
        db = load_database()
        first_letter = word[0].upper()
        
        # 检查是否已经存在
        if first_letter in db and any(item['word'].lower() == word.lower() for item in db[first_letter]):
            print(f"-> 提示：单词 '{word}' 已经在你的单词本中了！\n")
            continue
            
        print(f"-> 正在呼叫 AI 自动生成 '{word}' 的音标、例句和用法...")
        card_data = generate_word_card(word)
        
        if card_data:
            if first_letter not in db:
                db[first_letter] = []
            db[first_letter].append(card_data)
            save_database(db)
            print(f"-> 成功！'{word}' 已自动归档至首字母组 [{first_letter}]。\n")
            print(json.dumps(card_data, ensure_ascii=False, indent=2))
            print("-" * 40 + "\n")

if __name__ == "__main__":
    main()