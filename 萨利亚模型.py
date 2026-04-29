import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==================== 1. 语言切换器逻辑 ====================
st.set_page_config(page_title="Saizeriya 2007 Derivative Simulator", layout="wide")

lang = st.sidebar.radio("🌐 言語 / 语言切换", ["日本語", "中文"])
is_jp = (lang == "日本語")

def _t(jp_text, cn_text):
    return jp_text if is_jp else cn_text

# ==================== 2. 页面标题与说明 ====================
st.title(_t("📉 サイゼリヤ (Saizeriya) 2007年 為替デリバティブ巨額損失シミュレーター", 
            "📉 萨莉亚 (Saizeriya) 2007年汇率衍生品巨亏模拟器"))

st.markdown(_t(
    "本モデルは、2007年にサイゼリヤが金融機関と締結した致命的なクーポンスワップ（Coupon Swap）契約を再現したものです。\n左側のスライダーを操作して様々な市場環境をシミュレートし、**ラチェット条項（過去のレートがリセットされない仕組み）**がどのように損失を雪だるま式に拡大させるかをご確認いただけます。",
    "本模型重现了 2007 年萨莉亚与金融机构签订的致命的“息票互换（Coupon Swap）”衍生品合同。\n您可以通过左侧的滑块模拟各种市场环境，观察**棘轮条款（Ratchet / 历史汇率不重置机制）**是如何让亏损像滚雪球一样扩大的。"
))

# ==================== 3. 侧边栏：交互参数 ====================
st.sidebar.header(_t("⚙️ 市場パラメータ設定", "⚙️ 市场参数设置"))

initial_spot = st.sidebar.number_input(
    _t("初期実勢レート (直物為替レート JPY/AUD)", "初始现汇汇率 (JPY/AUD)"), 
    value=100.0, step=1.0)

annual_drift = st.sidebar.slider(
    _t("予想年間変動率 (ドリフト %)", "预期年化涨跌幅 (%)"), 
    min_value=-20.0, max_value=20.0, value=0.0, step=1.0) / 100

volatility = st.sidebar.slider(
    _t("市場の年間ボラティリティ (%)", "市场年化波动率 (%)"), 
    min_value=0.0, max_value=30.0, value=10.0, step=1.0) / 100

st.sidebar.markdown("---")
st.sidebar.subheader(_t("先物為替レート・パラメータ（金利差）", "远期汇率参数（利差影响）"))
jpy_rate = st.sidebar.slider(_t("日本の無リスク金利 (%)", "日本无风险利率 (%)"), 0.0, 5.0, 0.5, 0.1) / 100
aud_rate = st.sidebar.slider(_t("豪州の無リスク金利 (%)", "澳洲无风险利率 (%)"), 0.0, 10.0, 5.0, 0.1) / 100

st.sidebar.markdown("---")
st.sidebar.subheader(_t("ブラックスワン・イベント（極端な円高ショック）", "黑天鹅事件（极端日元升值冲击）"))
shock_month = st.sidebar.slider(_t("ショック発生月（何ヶ月目か）", "冲击发生月份 (第几个月)"), 0, 30, 5)
shock_magnitude = st.sidebar.slider(_t("単月の暴落幅 (%)", "单月暴跌幅度 (%)"), 0, 100, 0) / 100

# 新增：黑天鹅性质切换开关
shock_type = st.sidebar.radio(
    _t("ショックの性質", "黑天鹅冲击性质"),
    [_t("一過性の暴落（翌月反発）", "单月暴跌 (下月V型反弹，不继承)"),
     _t("恒久的な下落（以降のレートに影響）", "永久性下跌 (影响且继承后续汇率)")]
)

# 新增：合同汇率计算方式切换开关
st.sidebar.markdown("---")
st.sidebar.subheader(_t("契約レート計算方式", "合同汇率计算方式"))

contract_calc_mode = st.sidebar.radio(
    _t("暴落後の契約レート計算", "暴跌后的合同汇率计算"),
    [
        _t("通常モード：基準値以上なら78/69に戻る", "通常模式：高于基准则回到78/69"),
        _t("極端ラチェットモード：暴落後も前月契約レートから再計算", "极端棘轮模式：暴跌后继续用上月合同汇率递推")
    ]
)

extreme_ratchet_mode = (
    contract_calc_mode == _t(
        "極端ラチェットモード：暴落後も前月契約レートから再計算",
        "极端棘轮模式：暴跌后继续用上月合同汇率递推"
    )
)

# ==================== 4. 数据生成与核心逻辑 ====================
dates_A = pd.date_range(start='2008-12-01', end='2010-11-01', freq='MS')
dates_B_part1 = pd.to_datetime(['2008-09-01', '2008-11-01', '2009-01-01', '2009-03-01'])
dates_B_part2 = pd.date_range(start='2009-04-01', end='2011-03-01', freq='MS')
dates_B = dates_B_part1.union(dates_B_part2).sort_values()

all_dates = pd.date_range(start='2008-08-01', end='2011-03-01', freq='MS')
months_total = len(all_dates)

#np.random.seed(42) 
market_rates = [initial_spot]
underlying_rates = [initial_spot] # 用于记录真实的基本面走势（不一定受黑天鹅影响）
forward_rates = [initial_spot]

for i in range(1, months_total):
    dt = i / 12
    fwd = initial_spot * ((1 + jpy_rate) / (1 + aud_rate)) ** dt
    forward_rates.append(fwd)
    
    # 按照基本面计算下一期的基础汇率
    random_shock = np.random.normal(annual_drift/12, volatility/np.sqrt(12))
    next_underlying = underlying_rates[-1] * np.exp(random_shock)
    
    # 黑天鹅逻辑判断
    if i == shock_month:
        current_actual_rate = next_underlying * (1.0 - shock_magnitude)
        
        if shock_type == _t("一過性の暴落（翌月反発）", "单月暴跌 (下月V型反弹，不继承)"):
            # 基础线不跌，下个月还是从原本的位置继续走
            underlying_rates.append(next_underlying)
        else:
            # 基础线一起被砸下去，下个月从暴跌后的位置继续走
            underlying_rates.append(current_actual_rate)
            
        market_rates.append(current_actual_rate)
    else:
        underlying_rates.append(next_underlying)
        market_rates.append(next_underlying)

market_df = pd.DataFrame({'Date': all_dates, 'Market_Rate': market_rates, 'Forward_Rate': forward_rates})

def calculate_contract(
    dates,
    plan_name,
    threshold,
    cap,
    volume=1000000,
    extreme_ratchet=False
):
    """
    threshold:
        A方案 = 78
        B方案 = 69

    cap:
        A方案 = 600
        B方案 = 500

    重要：
        合同汇率不能低于 threshold。
        A 的下限永远是 78。
        B 的下限永远是 69。

    极端棘轮模式下：
        本月合同汇率 = 上月合同汇率 × 基准汇率 / 本月市场汇率

    但计算结果仍然要限制在：
        threshold <= 合同汇率 <= cap
    """

    results = []
    prev_contract_rate = threshold
    triggered = False

    for i, date in enumerate(dates):
        current_market_rate = market_df.loc[
            market_df["Date"] == date,
            "Market_Rate"
        ].values[0]

        fwd_rate = market_df.loc[
            market_df["Date"] == date,
            "Forward_Rate"
        ].values[0]

        if i == 0:
            current_contract_rate = threshold

        else:
            if current_market_rate < threshold:
                # 一旦市场汇率跌破基准，棘轮触发
                triggered = True

                calculated_rate = prev_contract_rate * threshold / current_market_rate

                # 关键：不能低于threshold，也不能超过cap
                current_contract_rate = min(
                    max(calculated_rate, threshold),
                    cap
                )

            else:
                if extreme_ratchet and triggered:
                    # 极端棘轮模式：
                    # 即使市场汇率恢复，也继续从上月合同汇率递推
                    calculated_rate = prev_contract_rate * threshold / current_market_rate

                    # 关键：递推后仍然不能低于78/69
                    current_contract_rate = min(
                        max(calculated_rate, threshold),
                        cap
                    )

                else:
                    # 普通模式：
                    # 市场汇率恢复到基准以上，合同汇率回到下限
                    current_contract_rate = threshold

        prev_contract_rate = current_contract_rate

        pnl_jpy = (current_market_rate - current_contract_rate) * volume

        results.append({
            "Date": date,
            "Plan": plan_name,
            "Market_Rate": current_market_rate,
            "Forward_Rate": fwd_rate,
            "Contract_Rate": current_contract_rate,
            "PnL_JPY": pnl_jpy
        })

    return pd.DataFrame(results)

plan_A_str = _t('プランA (基準78, 上限600)', '方案A (基准78, 上限600)')
plan_B_str = _t('プランB (基準69, 上限500)', '方案B (基准69, 上限500)')

df_A = calculate_contract(
    dates_A,
    plan_A_str,
    threshold=78,
    cap=600,
    volume=1000000,
    extreme_ratchet=extreme_ratchet_mode
)

df_B = calculate_contract(
    dates_B,
    plan_B_str,
    threshold=69,
    cap=500,
    volume=1000000,
    extreme_ratchet=extreme_ratchet_mode
)

df_A['Cumulative_PnL'] = df_A['PnL_JPY'].cumsum()
df_B['Cumulative_PnL'] = df_B['PnL_JPY'].cumsum()

df_all = pd.concat([df_A, df_B]).sort_values('Date')
df_all['Cumulative_PnL'] = df_all['PnL_JPY'].cumsum()

# ==================== 5. 图表可视化 ====================
st.subheader(_t("📊 シミュレーション結果", "📊 模拟结果"))

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=market_df['Date'], y=market_df['Market_Rate'], mode='lines+markers', name=_t('実勢為替レート (Spot)', '实际市场汇率 (Spot)'), line=dict(color='blue', width=2)))
fig1.add_trace(go.Scatter(x=market_df['Date'], y=market_df['Forward_Rate'], mode='lines', name=_t('理論上の先物レート (Forward)', '理论远期汇率 (Forward)'), line=dict(color='gray', dash='dash')))
fig1.add_trace(go.Scatter(x=df_A['Date'], y=df_A['Contract_Rate'], mode='lines+markers', name=_t('プランA 適用レート', '方案A 实际合同汇率'), line=dict(color='red')))
fig1.add_trace(go.Scatter(x=df_B['Date'], y=df_B['Contract_Rate'], mode='lines+markers', name=_t('プランB 適用レート', '方案B 实际合同汇率'), line=dict(color='orange')))

fig1.add_hline(y=78, line_dash="dot", annotation_text=_t("プランA 基準値 78", "方案A 基准线 78"), annotation_position="bottom right")
fig1.add_hline(y=69, line_dash="dot", annotation_text=_t("プランB 基準値 69", "方案B 基准线 69"), annotation_position="bottom right")
fig1.update_layout(title=_t("為替レートの推移：市場レート vs 強制適用される契約レート", "汇率走势：市场汇率 vs 强制执行的合同汇率"), yaxis_title=_t("円 / 1豪ドル", "日元 / 1澳元"), hovermode="x unified")
st.plotly_chart(fig1, width='stretch')

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df_all['Date'], y=df_all['Cumulative_PnL'], fill='tozeroy', name=_t('累計損益 (円)', '累计盈亏 (日元)'), line=dict(color='purple', width=3)))
fig2.update_layout(title=_t("期間内の総損益（累計）", "期间内总营业亏损（累计）"), yaxis_title=_t("円 (JPY)", "日元 (JPY)"), hovermode="x unified")
st.plotly_chart(fig2, width='stretch')

# ==================== 新增图表：A/B各自累计损益 ====================
st.subheader(_t("📈 プランA・Bの累計損益", "📈 A/B方案各自累计盈亏"))

fig3 = go.Figure()

fig3.add_trace(
    go.Scatter(
        x=df_A['Date'],
        y=df_A['Cumulative_PnL'],
        mode='lines+markers',
        name=_t('プランA 累計損益', '方案A 累计盈亏'),
        line=dict(color='red', width=3)
    )
)

fig3.add_trace(
    go.Scatter(
        x=df_B['Date'],
        y=df_B['Cumulative_PnL'],
        mode='lines+markers',
        name=_t('プランB 累計損益', '方案B 累计盈亏'),
        line=dict(color='orange', width=3)
    )
)

fig3.update_layout(
    title=_t("プランA・B別の累計損益推移", "A/B方案分别累计盈亏走势"),
    yaxis_title=_t("円 (JPY)", "日元 (JPY)"),
    hovermode="x unified"
)

st.plotly_chart(fig3, width='stretch')

# ==================== 6. 核心数据与解析 ====================
total_pnl_A = df_A['PnL_JPY'].sum()
total_pnl_B = df_B['PnL_JPY'].sum()
total_loss = total_pnl_A + total_pnl_B

max_loss_A = df_A['PnL_JPY'].min()
max_loss_B = df_B['PnL_JPY'].min()
max_loss_val = df_all['PnL_JPY'].min()

col1, col2, col3 = st.columns(3)

col1.metric(
    _t("プランA 総損益", "方案A 总盈亏"),
    f"¥ {total_pnl_A:,.0f}"
)

col2.metric(
    _t("プランB 総損益", "方案B 总盈亏"),
    f"¥ {total_pnl_B:,.0f}"
)

col3.metric(
    _t("A+B 総損益", "A+B 总盈亏"),
    f"¥ {total_loss:,.0f}"
)

col4, col5, col6 = st.columns(3)

col4.metric(
    _t("プランA 最悪単月損失", "方案A 最惨单月亏损"),
    f"¥ {max_loss_A:,.0f}"
)

col5.metric(
    _t("プランB 最悪単月損失", "方案B 最惨单月亏损"),
    f"¥ {max_loss_B:,.0f}"
)

col6.metric(
    _t("最高適用レート", "最高合同汇率"),
    f"{df_all['Contract_Rate'].max():.2f} JPY/AUD"
)

st.subheader(_t("📋 プラン別損益明細", "📋 按方案区分的盈亏明细"))

summary_df = pd.DataFrame({
    _t("項目", "项目"): [
        _t("プランA", "方案A"),
        _t("プランB", "方案B"),
        _t("合計", "合计")
    ],
    _t("総損益（円）", "总盈亏（日元）"): [
        total_pnl_A,
        total_pnl_B,
        total_loss
    ],
    _t("最悪単月損失（円）", "最惨单月亏损（日元）"): [
        max_loss_A,
        max_loss_B,
        max_loss_val
    ],
    _t("最高契約レート", "最高合同汇率"): [
        df_A['Contract_Rate'].max(),
        df_B['Contract_Rate'].max(),
        df_all['Contract_Rate'].max()
    ]
})

st.dataframe(summary_df, width='stretch')

jp_desc = """
### 💡 モデルの解説（金融的背景）
1. **損益の可視化：** 紫色のエリアグラフは、毎回の為替交換における `(市場価格 - 契約価格) * 1,000,000` をリアルタイムで計算・累計しています。
2. **為替変動の影響：** 左側の「予想年間変動率」を調節してみてください。+5%に設定しても、「ボラティリティ」が存在する限り、わずかな下落で契約レートが上限に達するリスクがあります。
3. **先物レート（Forward Rate）の罠：** グラフ中の灰色の破線は**理論上の先物レート**です。豪州の金利が高く、日本が低いため、先物レートは必然的に右肩下がりになります。
4. **V字回復の罠（一過性の暴落）：** 「一過性の暴落」モードでショック幅を大きくしてみてください。**市場レート（青線）が翌月にV字回復したとしても、契約レート（赤/オレンジ線）は高いままです。** ラチェット条項により、一度でも基準値を割ると過去の損失がロックされるという、このデリバティブの最も恐ろしい性質が確認できます。
"""

cn_desc = """
### 💡 模型深度解析（金融背景）
1. **盈亏可视化：** 紫色区域图表实时计算了每一次换汇的 `(市场价 - 合同约定价) * 1,000,000` 并进行累计。只要不跌破基准，萨莉亚就是赚的；一旦跌破，就是无底洞。
2. **汇率波动的影响：** 即使您将“预期年化涨跌幅”设定为 +5%（牛市），只要“波动率”拉高，一次日常的下跳就会触发上限阀门。
3. **远期汇率的陷阱：** 图表中的灰色虚线是**理论远期汇率**。投行利用两国的利差必然性，将一份“必输的对赌”包装成了理财。
4. **V型反弹的夺命陷阱：** 请选择“单月暴跌 (下月V型反弹)”并拉大暴跌幅度。您会震惊地发现：**即便市场蓝线在暴跌后瞬间反弹回原位，红色和黄色的合同价依然死死地锁在高位！** 因为棘轮条款只认单月最低点，无论事后怎么涨，高昂的换汇成本已被永久固化。
"""

st.markdown(_t(jp_desc, cn_desc))