import streamlit as st
from openai import OpenAI
import json
import time

# --- 1. 核心配置 (必须第一行) ---
st.set_page_config(
    page_title="AI 嘴替 Pro",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. 注入 iOS 风格 CSS (核心美化) ---
st.markdown("""
<style>
    /* 全局重置与背景 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 隐藏 Streamlit 自带杂项 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 容器卡片化 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 600px;
    }

    /* 标题样式 */
    .app-header {
        text-align: center;
        margin-bottom: 30px;
        animation: fadeIn 0.8s ease;
    }
    .app-header h1 {
        font-weight: 800;
        font-size: 28px;
        background: -webkit-linear-gradient(45deg, #007AFF, #5856D6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .app-header p {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }

    /* 输入框美化 - 拟态风格 */
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease;
        font-size: 16px;
        padding: 15px;
    }
    .stTextArea textarea:focus {
        border-color: #007AFF !important;
        box-shadow: 0 4px 20px rgba(0,122,255,0.15) !important;
    }

    /* 胶囊选择器美化 (Streamlit Radio/Selectbox Hack) */
    div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
    }
    div[role="radiogroup"] label {
        background-color: white;
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid #eee;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        transition: all 0.2s;
        font-size: 14px;
        cursor: pointer;
    }
    div[role="radiogroup"] label:hover {
        transform: translateY(-2px);
        border-color: #007AFF;
    }

    /* 按钮美化 - 悬浮渐变 */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #007AFF, #00C6FF);
        color: white;
        border: none;
        padding: 14px 24px;
        border-radius: 50px;
        font-size: 18px;
        font-weight: 600;
        letter-spacing: 0.5px;
        box-shadow: 0 10px 20px rgba(0,122,255,0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 25px rgba(0,122,255,0.4);
    }
    .stButton > button:active {
        transform: scale(0.95);
    }

    /* 结果气泡卡片 */
    .result-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border-left: 5px solid #007AFF;
        animation: slideUp 0.5s ease;
    }
    .result-tag {
        display: inline-block;
        background: #F0F8FF;
        color: #007AFF;
        padding: 4px 10px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .result-content {
        font-size: 16px;
        color: #333;
        line-height: 1.6;
        margin-bottom: 10px;
    }
    .result-analysis {
        font-size: 13px;
        color: #888;
        border-top: 1px dashed #eee;
        padding-top: 10px;
    }

    /* 动画定义 */
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    @keyframes slideUp {
        from {transform: translateY(20px); opacity: 0;}
        to {transform: translateY(0); opacity: 1;}
    }
    
    /* 隐藏 Code Block 的丑陋边框 */
    .stCode {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 头部区域 ---
st.markdown("""
<div class="app-header">
    <h1>💬 Chat Genius</h1>
    <p>你的高情商 AI 嘴替 · 专治不会聊天</p>
</div>
""", unsafe_allow_html=True)

# --- 4. 逻辑配置 (Key 管理) ---
api_key = None
try:
    if "DEEPSEEK_API_KEY" in st.secrets:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
except:
    pass

if not api_key:
    # 使用 Expander 隐藏丑陋的输入框
    with st.expander("🔐 首次使用请设置 API Key"):
        api_key = st.text_input("", type="password", placeholder="请输入 DeepSeek API Key (sk-xxx)")
        st.caption("Key 仅保存在本地浏览器，安全无虞")

# --- 5. 交互区域 (Card UI) ---

# 创建一个类似 App 原生 Tab 的容器
with st.container():
    # 场景选择 - 使用 Tabs 模拟胶囊切换
    mode = st.radio(
        "当前场景 👇",
        ["职场回复 💼", "高情商拒绝 🙅‍♂️", "恋爱/暧昧 💘", "朋友互怼 🤣", "安慰/关心 ❤️"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)

    # 输入区域
    col1, col2 = st.columns([3, 1])
    
    incoming_msg = st.text_area(
        "对方发了什么？",
        height=100,
        placeholder="长按粘贴聊天记录...\n例如：'周末有个临时的活，谁能顶一下？'",
        label_visibility="collapsed"
    )

    # 隐藏的高级选项 (风格)
    with st.expander("🎨 调整语气 (默认：得体)", expanded=False):
        style = st.select_slider(
            "选择回复力度",
            options=["极度委婉", "礼貌得体", "幽默风趣", "阴阳怪气", "发疯文学"],
            value="礼貌得体"
        )
        user_intent = st.text_input("补充你的真实想法 (可选)", placeholder="例如：我想去，但是得加钱")

# --- 6. 生成按钮 ---
st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
generate_btn = st.button("✨ 立即生成神回复")

# --- 7. AI 核心 ---
def get_response_pro(key, msg, intent, mode, style):
    if not key: return None, "请先在上方设置 API Key 🔑"
    
    client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
    
    # 精心调教的 System Prompt
    system_prompt = f"""
    你是一个深谙人性的沟通大师。
    场景：{mode}
    风格：{style}
    
    请生成 3 个不同维度的回复建议。
    要求：
    1. 必须返回纯 JSON 格式。
    2. 包含 'options' 数组，每项含 title (简短标签), content (口语化回复), analysis (策略一句话解释)。
    3. 回复内容要像真人，拒绝 AI 味。
    """
    
    user_prompt = f"对方说：{msg}\n我的意图：{intent}"
    
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=1.3
        )
        return resp.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

# --- 8. 结果展示 (流式/卡片动画) ---
if generate_btn:
    if not incoming_msg:
        st.warning("⚠️ 请先输入对方的话哦")
    else:
        # 模拟 App 加载进度条
        progress_text = "🧠 AI 正在分析潜台词..."
        my_bar = st.progress(0, text=progress_text)
        
        for percent_complete in range(100):
            time.sleep(0.01) # 假装在加载，增加仪式感
            my_bar.progress(percent_complete + 1, text=progress_text)
        
        my_bar.empty() # 加载完清空进度条
        
        # 真实请求
        res, err = get_response_pro(api_key, incoming_msg, user_intent, mode, style)
        
        if err:
            st.error(f"连接失败: {err}")
        else:
            try:
                clean_res = res.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_res)
                options = data.get("options", data)
                
                st.markdown("### 💡 推荐回复")
                
                for i, opt in enumerate(options):
                    # 自定义 HTML 卡片渲染
                    st.markdown(f"""
                    <div class="result-card">
                        <span class="result-tag">{opt.get('title')}</span>
                        <div class="result-content">{opt.get('content')}</div>
                        <div class="result-analysis">🎯 {opt.get('analysis')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 复制按钮 (Streamlit 唯一的原生复制方案)
                    st.code(opt.get('content'), language="text")
                    
            except:
                st.error("AI 偶尔会走神，格式乱了，直接看原文吧：")
                st.write(res)

# 底部留白，防止手机端遮挡
st.markdown("<br><br>", unsafe_allow_html=True)
