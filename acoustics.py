import numpy as np
import pandas as pd

SPEED_OF_SOUND = 343.2  # m/s (20 degrees Celsius)

def calculate_room_modes(l, w, h, max_freq=300):
    """
    計算室內駐波模態 (Room Modes)
    l: 長度 (公尺)
    w: 寬度 (公尺)
    h: 高度 (公尺)
    max_freq: 最高計算頻率 (Hz)
    """
    modes = []
    
    # 估算迴圈的最大整數
    max_nx = int(np.ceil(max_freq * 2 * l / SPEED_OF_SOUND))
    max_ny = int(np.ceil(max_freq * 2 * w / SPEED_OF_SOUND))
    max_nz = int(np.ceil(max_freq * 2 * h / SPEED_OF_SOUND))
    
    for nx in range(max_nx + 1):
        for ny in range(max_ny + 1):
            for nz in range(max_nz + 1):
                if nx == 0 and ny == 0 and nz == 0:
                    continue
                
                freq = (SPEED_OF_SOUND / 2) * np.sqrt((nx/l)**2 + (ny/w)**2 + (nz/h)**2)
                
                if freq <= max_freq:
                    zeros = [nx, ny, nz].count(0)
                    if zeros == 2:
                        mode_type = "Axial (軸向)"
                    elif zeros == 1:
                        mode_type = "Tangential (切向)"
                    else:
                        mode_type = "Oblique (斜向)"
                        
                    modes.append({
                        "nx": nx, "ny": ny, "nz": nz,
                        "Mode": f"{nx}-{ny}-{nz}",
                        "Frequency (Hz)": round(freq, 2),
                        "Type": mode_type
                    })
                    
    df = pd.DataFrame(modes)
    if not df.empty:
        df = df.sort_values(by="Frequency (Hz)").reset_index(drop=True)
    return df

def evaluate_room(l, w, h, schroeder_freq):
    """
    評估房間比例並給予聲學建議
    """
    # 將尺寸標準化為 高度=1 的比例 (確保 l > w > h 來進行比較)
    dims = sorted([l, w, h])
    h_norm, w_norm, l_norm = dims[0], dims[1], dims[2]
    ratio_w = w_norm / h_norm
    ratio_l = l_norm / h_norm
    
    # 理想比例 (Sepmeyer)
    ideal_ratios = [
        (1.14, 1.39), # Sepmeyer A
        (1.28, 1.54), # Sepmeyer B
        (1.60, 2.33)  # Sepmeyer C
    ]
    
    # 計算與最接近理想比例的距離
    min_dist = float('inf')
    for ideal_w, ideal_l in ideal_ratios:
        dist = np.sqrt((ratio_w - ideal_w)**2 + (ratio_l - ideal_l)**2)
        if dist < min_dist:
            min_dist = dist
            
    # 如果是正立方體或接近正立方體，給予極低分
    is_cube = (abs(l - w) < 0.1 and abs(w - h) < 0.1)
    
    # 計算分數 (0-100)
    if is_cube:
        score = 30
        ratio_comment = "您的房間接近正立方體，這是聲學上最不利的形狀。駐波會在特定頻率嚴重疊加。"
    else:
        # 距離 0.0 -> 100分, 距離 0.5 -> 60分
        score = max(0, min(100, int(100 - (min_dist * 80))))
        if score >= 85:
            ratio_comment = "您的房間長寬高比例非常優秀！非常接近聲學大師 Sepmeyer 建議的黃金比例，天生具備良好的駐波均勻度。"
        elif score >= 70:
            ratio_comment = "您的房間比例良好，避開了最糟糕的頻率重疊情況。雖然不是完美黃金比例，但後期的聲學處理會相對輕鬆。"
        else:
            ratio_comment = "您的房間比例一般。某些頻段可能會有較明顯的駐波疊加，建議透過聲學裝修來改善。"

    advice = [
        f"**空間比例評分：{score} / 100**",
        f"💡 {ratio_comment}",
        f"💡 **低頻處理建議**：您的施羅德頻率為 {schroeder_freq:.1f} Hz。建議針對此頻率以下的頻段，在房間角落配置對應頻段的低頻陷阱 (Bass Traps) 來吸收多餘的空腔增益。",
        "💡 **中高頻建議**：施羅德頻率以上的中高頻，聲音較偏向直線傳播。您可以在喇叭與聆聽位置的「第一反射點」加上吸音棉或擴散板，來提升聲音的清晰度與音場定位。"
    ]
    
    return score, advice
