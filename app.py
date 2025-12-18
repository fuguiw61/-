import streamlit as st
from openai import OpenAI
import json
import random

# --- 1. 页面基础配置 (必须放在第一行) ---
st.set_page_config(
    page_title="AI 高情商聊天嘴替",
    page_icon="🦈",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. 自定义 CSS 美化 ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px;
        border-radius: 10px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
        color: white;
    }
    .chat-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 5px solid #4CAF50;
    }
    .analysis-text {
        font-size: 0.9em;
        color: #555;
        font-style: italic;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏：设置与指南 ---
with st.sidebar:
    st.image("https://chat.deepseek.com/favicon.svg", width=50)
    st.title("⚙️ 全局设置")
    
    # API Key 输入框
    api_key = st.text_input("请输入 DeepSeek API Key", type="password", 
                            placeholder="sk-xxxxxxxx",
                            help="请去 platform.deepseek.com 申请")
    
    st.markdown("---")
    st.markdown("### 📖 使用指南")
    st.info("""
    1. **复制** 让你头大的聊天内容。
    2. **选择** 对方是谁、你想要什么风格。
    3. (可选) **备注** 你的真实意图（比如：想拒绝但不敢说）。
    4. 点击生成，**一键复制** 回复！
    """)
    st.caption("Powered by DeepSeek-V3")

# --- 4. 主界面内容 ---
st.title("🦈 你的专属高情商嘴替")
st.subheader("拒绝内耗，让 AI 帮你回消息")

# --- 5. 增强版选项配置 ---
# 定义更丰富的人物关系
relations_map = {
    "职场/商务": ["严厉的老板 👔", "推卸责任的同事 😒", "难搞的甲方 💰", "甚至不想回复的乙方 📉", "求职面试官 🤝"],
    "情感/恋爱": ["正在暧昧的对象 💕", "热恋中的伴侣 👩‍❤️‍👨", "正在冷战的对象 ❄️", "想分手的对象 💔", "前任 👻"],
    "社交/生活": ["很久没见的朋友 🙋‍♂️", "催婚/催生的亲戚 👵", "借钱的朋友 💸", "杠精/键盘侠 ⌨️", "普通的礼貌回复 👋"]
}

# 定义更丰富的风格
styles_list = [
    "高情商/得体 (不出错) ✨",
    "幽默/风趣 (破冰专用) 😂",
    "委婉/含蓄 (给面子) 🍃",
    "不卑不亢 (职场防御) 🛡️",
    "阴阳怪气 (优雅回怼) ⚔️",
    "撒娇/软萌 (斩男/女) 🐱",
    "糊弄文学 (不想聊了) 🌚",
    "发疯文学 (情绪宣泄) 🤯"
]

# 布局：两列选择器
col1, col2 = st.columns(2)

with col1:
    # 二级联动选择（简化处理，直接展平）
    category = st.selectbox("当前场景类别", list(relations_map.keys()))
    relationship = st.selectbox("具体对方是谁？", relations_map[category])

with col2:
    selected_style = st.selectbox("你希望用什么语气？", styles_list)

# 输入区域
incoming_msg = st.text_area("对方发来了什么？(直接粘贴)", height=100, placeholder="例如：这周六都要加班，大家没意见吧？")
user_intent = st.text_input("你心里的真实想法是？(AI会帮你润色)", placeholder="例如：不想去，想请假，但不敢直说...")

# --- 6. 核心逻辑：调用 DeepSeek ---
def get_deepseek_reply(api_key, msg, intent, relation, style):
    if not api_key:
        return None, "请先在左侧侧边栏填入 API Key 🔑"
    
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    # 更加专业的提示词工程 (Prompt Engineering)
    system_prompt = f"""
    你是一位精通心理学和沟通技巧的社交专家。
    【任务】
    针对用户提供的“对方发来的话”和“用户真实意图”，生成 3 个不同角度的回复建议。
    
    【当前情境】
    - 人物关系：{relation}
    - 目标风格：{style}
    
    【输出要求】
    1. 必须输出为纯 JSON 格式。
    2. JSON 需包含一个列表 "options"，每个对象包含：
       - "title": (字符串) 策略名称，如“以退为进法”
       - "content": (字符串) 直接可发送的回复内容
       - "analysis": (字符串) 简短解析，为什么这么回有效
    3. 回复内容要口语化、符合所选风格，不要像机器人。
    """
    
    user_message = f"对方说：'{msg}'\n我的真实意图：'{intent}'"
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=1.3, # 稍微调高温度，让回复更有灵性和创意
            stream=False
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

# --- 7. 生成按钮与结果展示 ---
if st.button("✨ 帮我生成神回复", use_container_width=True):
    if not incoming_msg:
        st.warning("⚠️ 哪怕只发了一个句号，你也得告诉我对方说了啥呀！")
    else:
        with st.spinner("DeepSeek 大脑正在飞速运转中..."):
            res_text, error = get_deepseek_reply(api_key, incoming_msg, user_intent, relationship, selected_style)
            
            if error:
                st.error(f"出错了：{error}")
            else:
                try:
                    # 数据清洗：防止大模型偶尔输出 markdown 标记
                    clean_json = res_text.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    
                    # 兼容性处理
                    options = data.get("options", data) if isinstance(data, dict) else data
                    
                    st.success(f"已生成 3 种 [{selected_style}] 风格的回复：")
                    
                    # 循环展示卡片
                    for i, opt in enumerate(options):
                        # 使用 HTML/CSS 自定义卡片样式
                        st.markdown(f"""
                        <div class="chat-card">
                            <h4 style="margin-top:0;">💡 方案 {i+1}: {opt.get('title', '未命名策略')}</h4>
                            <div class="analysis-text">🧠 策略分析: {opt.get('analysis', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 使用 Streamlit 原生代码块，方便一键复制
                        st.code(opt.get('content', ''), language="text")
                        
                except Exception as e:
                    st.error("AI 返回的格式有点问题，只能显示原文了：")
                    st.code(res_text)