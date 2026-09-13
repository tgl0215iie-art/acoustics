import streamlit as st
from acoustics import calculate_room_modes, evaluate_room
from visualize import plot_room_modes

st.set_page_config(page_title="空間聲學評估 - 駐波與空腔增益", layout="wide")

st.title("空間聲學評分 - 駐波分析 (Room Mode Analysis)")
st.markdown("本系統參考了 amroc 計算邏輯，首期專注於無聲源情況下，計算空腔內因為尺寸比例產生的駐波與頻率增益分佈。")

st.sidebar.header("輸入空間參數")
st.sidebar.markdown("請輸入房間尺寸，預設為您提供的立方體尺寸。")
l_cm = st.sidebar.number_input("長度 Length (cm)", value=390.0, step=10.0, format="%.1f")
w_cm = st.sidebar.number_input("寬度 Width (cm)", value=340.0, step=10.0, format="%.1f")
h_cm = st.sidebar.number_input("高度 Height (cm)", value=280.0, step=10.0, format="%.1f")
rt60 = st.sidebar.number_input("預估殘響時間 RT60 (s)", value=0.21, step=0.01, format="%.2f")
max_freq = st.sidebar.slider("最高計算頻率 (Hz)", min_value=100, max_value=500, value=300, step=10)

l_m = l_cm / 100.0
w_m = w_cm / 100.0
h_m = h_cm / 100.0
volume = l_m * w_m * h_m

import math
schroeder_freq = 2000 * math.sqrt(rt60 / volume) if volume > 0 else 0

st.sidebar.markdown(f"**目前體積 (Volume):** {volume:.2f} m³")
st.sidebar.markdown(f"**施羅德頻率 (Schroeder Freq):** {schroeder_freq:.1f} Hz")

# 計算駐波
df_modes = calculate_room_modes(l_m, w_m, h_m, max_freq)
score, advice = evaluate_room(l_m, w_m, h_m, schroeder_freq)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("頻率分佈圖 (Room Modes Distribution)")
    fig = plot_room_modes(df_modes, schroeder_freq)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"💡 **解讀：** \n"
            f"- 您的比例 (3.9 x 3.4 x 2.8) 改善了正立方體頻率完美重疊的問題，駐波分佈相對均勻。\n"
            f"- **施羅德頻率 ({schroeder_freq:.1f} Hz)：** 圖表中的黃色虛線。在此頻率**以下**的頻段（房間模態區），聲波呈現獨立的駐波特性，容易產生明顯的轟鳴或抵銷，是我們空腔增益需要特別處理的重點區域！")
            
    st.subheader("🏆 系統聲學評估與建議")
    if score >= 80:
        st.success(advice[0])
    elif score >= 60:
        st.warning(advice[0])
    else:
        st.error(advice[0])
        
    for text in advice[1:]:
        st.write(text)

with col2:
    st.subheader(f"計算結果 (<= {max_freq} Hz)")
    st.dataframe(df_modes, height=450, use_container_width=True)
