import plotly.graph_objects as go

def plot_room_modes(df, schroeder_freq=None):
    """
    繪製駐波頻率分佈圖 (類似 amroc 下方的 1D 頻譜圖)
    不同顏色的線條代表不同類型的模態。
    """
    if df.empty:
        return go.Figure()
        
    fig = go.Figure()

    color_map = {
        "Axial (軸向)": ("red", 1.0),
        "Tangential (切向)": ("blue", 0.7),
        "Oblique (斜向)": ("green", 0.4)
    }

    for mode_type, (color, height) in color_map.items():
        type_df = df[df['Type'] == mode_type]
        if not type_df.empty:
            fig.add_trace(go.Bar(
                x=type_df['Frequency (Hz)'],
                y=[height] * len(type_df),
                width=0.8,
                name=mode_type,
                marker_color=color,
                hovertemplate="Freq: %{x} Hz<br>Mode: %{customdata}<extra></extra>",
                customdata=type_df['Mode']
            ))

    if schroeder_freq is not None:
        fig.add_vline(x=schroeder_freq, line_width=2, line_dash="dash", line_color="orange",
                      annotation_text=f"Schroeder Freq ({schroeder_freq:.1f} Hz)", 
                      annotation_position="top right")

    fig.update_layout(
        title="空腔增益：室內駐波頻率分佈 (Room Modes)",
        xaxis_title="頻率 (Hz)",
        yaxis_title="影響強度權重 (示意)",
        yaxis=dict(showticklabels=False, range=[0, 1.2]),
        barmode='overlay',
        hovermode="x",
        plot_bgcolor='white'
    )
    
    # 加上網格線方便對齊
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', tick0=0, dtick=10)
    
    return fig
