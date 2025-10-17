# styles.py

import streamlit as st

def load_custom_css(theme="blue"):
    """تحميل الأنماط المخصصة حسب الثيم"""
    
    themes = {
        "blue": "#3b82f6",
        "green": "#10b981",
        "orange": "#f97316",
        "pink": "#ec4899",
        "purple": "#8b5cf6",
        "dark": "#1f2937",
    }
    
    primary_color = themes.get(theme, "#3b82f6")
    
    css = f"""
    <style>
    /* الشريط الجانبي */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {primary_color}15 0%, {primary_color}05 100%);
    }}
    
    /* العناوين */
    h1, h2, h3 {{
        color: {primary_color};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* الأزرار */
    .stButton>button {{
        border-radius: 8px;
        border: 1px solid {primary_color}30;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        background-color: {primary_color}20;
        border-color: {primary_color};
    }}
    
    /* البطاقات */
    .main-header {{
        background: linear-gradient(135deg, {primary_color}20 0%, {primary_color}10 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    .main-header h1 {{
        margin: 0;
        font-size: 2.5rem;
    }}
    
    .main-header p {{
        margin: 0.5rem 0 0 0;
        color: #6b7280;
        font-size: 1.1rem;
    }}
    
    /* الجداول */
    [data-testid="stDataFrame"] {{
        border-radius: 8px;
        overflow: hidden;
    }}
    
    /* المدخلات */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {{
        border-radius: 6px;
        border: 1px solid {primary_color}30;
    }}
    
    /* المقاييس */
    [data-testid="stMetricValue"] {{
        color: {primary_color};
        font-size: 1.8rem;
        font-weight: bold;
    }}
    
    /* التنبيهات */
    .stAlert {{
        border-radius: 8px;
    }}
    
    /* التبويبات */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {primary_color}20;
    }}
    
    /* الخطوط العربية */
    * {{
        font-family: 'Cairo', 'Segoe UI', sans-serif;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)