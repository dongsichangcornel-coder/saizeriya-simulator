import streamlit as st
import pandas as pd
from datetime import date
import math


# =========================
# 1. 日期设定 / 日付設定
# =========================

EVENT_DATE = date(2021, 6, 19)

WEB_AD_CONTRACT = date(2021, 2, 12)
WEB_AD_START = date(2021, 3, 12)

PAMPHLET_PRINT_DATE = date(2021, 2, 26)
PAMPHLET_SEND_DATE = date(2021, 3, 15)

RECRUIT_START = date(2021, 4, 26)
RECRUIT_END = date(2021, 5, 14)
PARTICIPANT_FIXED_DATE = date(2021, 5, 21)

VENUE_31_DAYS_BEFORE = date(2021, 5, 19)
VENUE_30_DAYS_BEFORE = date(2021, 5, 20)

# case里没有明确写讲师事前会议日期，这里暂定为5月31日
# ケースでは講師との事前ミーティング日が明記されていないため、ここでは5月31日と仮定
PRE_MEETING_DATE = date(2021, 5, 31)

LUNCH_FREE_CANCEL_LIMIT = date(2021, 6, 16)
COFFEE_FREE_CANCEL_LIMIT = date(2021, 6, 18)


# =========================
# 2. 金额设定 / 金額設定
# =========================

VENUE_TOTAL = 400_000
VENUE_DEPOSIT = VENUE_TOTAL * 0.30

LECTURER_TOTAL = 500_000
LECTURER_CANCEL_AFTER_MEETING = 250_000

# 按你的要求：员工工资不作为追加成本计算
# ユーザー指定：社内従業員の給与は追加費用として計算しない
STAFF_COST = 0

WEB_AD_TOTAL = 250_000
WEB_AD_ADVANCE = 125_000

PAMPHLET_PRINT_COST = 80_000
PAMPHLET_SEND_COST = 120_000

TEXTBOOK_UNIT = 200
CASE_UNIT = 1_500
NAMEPLATE_UNIT = 100
SPARE_COPIES = 5

LUNCH_UNIT = 1_300
COFFEE_UNIT_PER_10_CUPS = 4_000
COFFEE_CUPS = 80

STUDENT_CANCEL_PENALTY_RATE = 0.50


# =========================
# 3. 工具函数 / Utility
# =========================

def yen(x):
    return f"{x:,.0f} 円"


def calculate_revenue(registered_people, student_cancel_people, final_people, fee, nsj_cancel):
    penalty_revenue = student_cancel_people * fee * STUDENT_CANCEL_PENALTY_RATE

    if nsj_cancel:
        tuition_revenue = 0
        process = (
            f"NSJ取消举办时，实际参加者报名费视为退还 / "
            f"NSJ側キャンセル時、実参加者の受講料は返金される前提："
            f"{final_people} × {yen(fee)} = 0 円\n"
            f"募集期内学生主动取消违约金 / 募集期間中の受講生側キャンセル料："
            f"{student_cancel_people} × {yen(fee)} × 50% = {yen(penalty_revenue)}"
        )
    else:
        tuition_revenue = final_people * fee
        process = (
            f"实际参加者报名费 / 実参加者の受講料："
            f"{final_people} × {yen(fee)} = {yen(tuition_revenue)}\n"
            f"募集期内学生主动取消违约金 / 募集期間中の受講生側キャンセル料："
            f"{student_cancel_people} × {yen(fee)} × 50% = {yen(penalty_revenue)}"
        )

    total_revenue = tuition_revenue + penalty_revenue
    return total_revenue, tuition_revenue, penalty_revenue, process


def calculate_holding_cost(final_people):
    rows = []

    rows.append([
        "会场费 / 会場費",
        VENUE_TOTAL,
        f"会场使用料 / 会場使用料 = {yen(VENUE_TOTAL)}"
    ])

    rows.append([
        "讲师费 / 講師料",
        LECTURER_TOTAL,
        f"讲师费 / 講師料 = {yen(LECTURER_TOTAL)}"
    ])

    rows.append([
        "员工工资 / 社内従業員給与",
        STAFF_COST,
        "既有员工，无追加工资或加班费，因此追加成本 = 0 円 / "
        "既存社員のため、追加給与・残業代なし。追加費用 = 0 円"
    ])

    rows.append([
        "Web广告费 / Web広告費",
        WEB_AD_TOTAL,
        f"Web广告费 / Web広告費 = {yen(WEB_AD_TOTAL)}"
    ])

    pamphlet_cost = PAMPHLET_PRINT_COST + PAMPHLET_SEND_COST
    rows.append([
        "宣传册费用 / パンフレット費",
        pamphlet_cost,
        f"印刷 {yen(PAMPHLET_PRINT_COST)} + 邮送/発送 {yen(PAMPHLET_SEND_COST)} = {yen(pamphlet_cost)}"
    ])

    textbook_cost = TEXTBOOK_UNIT * (final_people + SPARE_COPIES)
    case_cost = CASE_UNIT * (final_people + SPARE_COPIES)
    nameplate_cost = NAMEPLATE_UNIT * final_people
    material_cost = textbook_cost + case_cost + nameplate_cost

    rows.append([
        "教材・案例・名牌 / 教材・ケース・ネームプレート",
        material_cost,
        f"教材 {TEXTBOOK_UNIT} × ({final_people}+予備{SPARE_COPIES}) = {yen(textbook_cost)}；"
        f"案例/ケース {CASE_UNIT} × ({final_people}+予備{SPARE_COPIES}) = {yen(case_cost)}；"
        f"名牌/ネームプレート {NAMEPLATE_UNIT} × {final_people} = {yen(nameplate_cost)}；"
        f"合计/合計 = {yen(material_cost)}"
    ])

    lunch_count = final_people + 1 + 4
    lunch_cost = LUNCH_UNIT * lunch_count
    rows.append([
        "午餐费 / 昼食代",
        lunch_cost,
        f"{LUNCH_UNIT} × ({final_people}+讲师/講師1+员工/スタッフ4) = {yen(lunch_cost)}"
    ])

    coffee_units = math.ceil(COFFEE_CUPS / 10)
    coffee_cost = coffee_units * COFFEE_UNIT_PER_10_CUPS
    rows.append([
        "咖啡服务 / コーヒーサービス",
        coffee_cost,
        f"{COFFEE_CUPS}杯 ÷ 10杯単位 × {yen(COFFEE_UNIT_PER_10_CUPS)} = {yen(coffee_cost)}"
    ])

    df = pd.DataFrame(rows, columns=["项目 / 項目", "金额 / 金額", "计算过程 / 計算過程"])
    total = df["金额 / 金額"].sum()
    return total, df


def calculate_cancel_cost(final_people, cancel_date):
    rows = []

    # 会场取消费
    if cancel_date <= VENUE_31_DAYS_BEFORE:
        venue_cancel = VENUE_DEPOSIT
        venue_process = (
            f"举办31日前取消，只损失预约金 / 開催31日前までのキャンセル、予約金のみ："
            f"{yen(VENUE_TOTAL)} × 30% = {yen(venue_cancel)}"
        )
    else:
        venue_cancel = VENUE_TOTAL
        venue_process = (
            f"举办30日以内取消，会场费全额成为取消费 / "
            f"開催30日以内のキャンセル、会場費全額：{yen(venue_cancel)}"
        )

    rows.append(["会场取消费 / 会場キャンセル料", venue_cancel, venue_process])

    # 讲师取消费
    if cancel_date < PRE_MEETING_DATE:
        lecturer_cancel = 0
        lecturer_process = (
            "事前会议前取消，讲师费 = 0 円 / "
            "事前ミーティング前のキャンセル、講師料 = 0 円"
        )
    else:
        lecturer_cancel = LECTURER_CANCEL_AFTER_MEETING
        lecturer_process = (
            f"事前会议后由NSJ取消，需承担半额讲师费 / "
            f"事前ミーティング後にNSJ側都合でキャンセル、講師料半額：{yen(lecturer_cancel)}"
        )

    rows.append(["讲师取消费 / 講師キャンセル料", lecturer_cancel, lecturer_process])

    # 员工工资
    rows.append([
        "员工工资 / 社内従業員給与",
        0,
        "按本次设定，员工工资不作为取消时追加费用计算 = 0 円 / "
        "既存社員の給与はキャンセル時の追加費用として計算しない = 0 円"
    ])

    # Web广告取消费
    if cancel_date < WEB_AD_CONTRACT:
        web_cancel = 0
        web_process = "Web广告契约前取消，费用 = 0 円 / Web広告契約前のキャンセル、費用 = 0 円"
    elif cancel_date < WEB_AD_START:
        web_cancel = WEB_AD_ADVANCE
        web_process = f"广告开始前取消，只损失前金 / 広告開始前のキャンセル、前金のみ：{yen(web_cancel)}"
    else:
        web_cancel = WEB_AD_TOTAL
        web_process = f"广告已经开始，需支付全额 / 広告開始後のキャンセル、全額：{yen(web_cancel)}"

    rows.append(["Web广告取消费 / Web広告キャンセル料", web_cancel, web_process])

    # 宣传册取消费
    if cancel_date < PAMPHLET_PRINT_DATE:
        pamphlet_cancel = 0
        pamphlet_process = "宣传册印刷前取消，费用 = 0 円 / パンフレット印刷前、費用 = 0 円"
    elif cancel_date < PAMPHLET_SEND_DATE:
        pamphlet_cancel = PAMPHLET_PRINT_COST
        pamphlet_process = f"已印刷但未邮送，只发生印刷费 / 印刷後・発送前、印刷費のみ：{yen(pamphlet_cancel)}"
    else:
        pamphlet_cancel = PAMPHLET_PRINT_COST + PAMPHLET_SEND_COST
        pamphlet_process = f"已邮送，印刷费+邮送费 / 発送済み、印刷費＋発送費：{yen(pamphlet_cancel)}"

    rows.append(["宣传册取消费 / パンフレットキャンセル料", pamphlet_cancel, pamphlet_process])

    # 教材取消费
    if cancel_date < PARTICIPANT_FIXED_DATE:
        material_cancel = 0
        material_process = (
            "参加人数尚未确定，教材・案例・名牌费用 = 0 円 / "
            "受講生数確定前のため、教材・ケース・ネームプレート費 = 0 円"
        )
    else:
        textbook_cost = TEXTBOOK_UNIT * (final_people + SPARE_COPIES)
        case_cost = CASE_UNIT * (final_people + SPARE_COPIES)
        nameplate_cost = NAMEPLATE_UNIT * final_people
        material_cancel = textbook_cost + case_cost + nameplate_cost
        material_process = (
            f"教材 {yen(textbook_cost)} + 案例/ケース {yen(case_cost)} "
            f"+ 名牌/ネームプレート {yen(nameplate_cost)} = {yen(material_cancel)}"
        )

    rows.append([
        "教材・案例・名牌取消费 / 教材・ケース・ネームプレートキャンセル料",
        material_cancel,
        material_process
    ])

    # 午餐取消费
    lunch_count = final_people + 1 + 4
    lunch_total = LUNCH_UNIT * lunch_count

    if cancel_date <= LUNCH_FREE_CANCEL_LIMIT:
        lunch_cancel = 0
        lunch_process = "举办3日前以前取消，午餐费 = 0 円 / 開催3日前まで、昼食代 = 0 円"
    else:
        lunch_cancel = lunch_total
        lunch_process = f"超过免费取消期限 / 無料キャンセル期限後：{LUNCH_UNIT} × {lunch_count} = {yen(lunch_cancel)}"

    rows.append(["午餐取消费 / 昼食キャンセル料", lunch_cancel, lunch_process])

    # 咖啡取消费
    coffee_total = math.ceil(COFFEE_CUPS / 10) * COFFEE_UNIT_PER_10_CUPS

    if cancel_date <= COFFEE_FREE_CANCEL_LIMIT:
        coffee_cancel = 0
        coffee_process = "举办前日以前取消，咖啡服务费 = 0 円 / 開催前日まで、コーヒーサービス費 = 0 円"
    else:
        coffee_cancel = coffee_total
        coffee_process = f"超过免费取消期限，咖啡服务费 / 無料キャンセル期限後：{yen(coffee_cancel)}"

    rows.append(["咖啡取消费 / コーヒーキャンセル料", coffee_cancel, coffee_process])

    df = pd.DataFrame(rows, columns=["项目 / 項目", "金额 / 金額", "计算过程 / 計算過程"])
    total = df["金额 / 金額"].sum()
    return total, df


# =========================
# 4. Streamlit 页面 / UI
# =========================

st.set_page_config(page_title="NSJ Seminar Simulator", layout="wide")

st.title("NSJ セミナー 利益・取消費用シミュレーション")
st.caption("人数・受講料・キャンセル有無を選ぶだけで、利益/損失と取消費用を可視化します。")
st.caption("选择人数、报名费、是否取消，即可显示利润/亏损和取消费用。")

with st.sidebar:
    st.header("选择条件 / 条件選択")

    registered_people = st.slider(
        "报名人数 / 申込人数",
        min_value=30,
        max_value=60,
        value=40,
        step=1
    )

    fee = st.selectbox(
        "报名费（日元/人） / 受講料（円/人）",
        options=[
            25_000, 30_000, 35_000, 40_000,
            45_000, 50_000, 55_000, 60_000,
            65_000, 70_000, 75_000, 80_000
        ],
        index=7
    )

    student_cancel_people = st.slider(
        "募集期内取消报名人数 / 募集期間中の受講生側キャンセル人数",
        min_value=0,
        max_value=registered_people,
        value=0,
        step=1
    )

    final_people = registered_people - student_cancel_people

    cancel_choice = st.radio(
        "NSJ是否取消举办？ / NSJ側が開催をキャンセルするか？",
        ["不取消 / キャンセルしない", "取消 / キャンセルする"],
        index=0
    )

    nsj_cancel = cancel_choice.startswith("取消")

    if nsj_cancel:
        cancel_date = st.date_input(
            "NSJ取消日期 / NSJキャンセル日",
            value=date(2021, 5, 21),
            min_value=date(2021, 1, 1),
            max_value=EVENT_DATE
        )
    else:
        cancel_date = None

    st.markdown("---")
    st.write(f"举办日 / 開催日：{EVENT_DATE}")
    st.write(f"报名人数 / 申込人数：{registered_people} 人")
    st.write(f"募集期内取消 / 募集期間中キャンセル：{student_cancel_people} 人")
    st.write(f"实际参加人数 / 実際受講者数：{final_people} 人")


# =========================
# 5. 计算 / Calculation
# =========================

revenue, tuition_revenue, penalty_revenue, revenue_process = calculate_revenue(
    registered_people,
    student_cancel_people,
    final_people,
    fee,
    nsj_cancel
)

holding_cost, holding_df = calculate_holding_cost(final_people)
holding_profit = revenue - holding_cost

if nsj_cancel:
    cancel_cost, cancel_df = calculate_cancel_cost(final_people, cancel_date)
    cancel_result = revenue - cancel_cost
else:
    cancel_cost = 0
    cancel_df = pd.DataFrame(columns=["项目 / 項目", "金额 / 金額", "计算过程 / 計算過程"])
    cancel_result = None


# =========================
# 6. 结果展示 / Results
# =========================

col1, col2, col3, col4 = st.columns(4)

col1.metric("总收入 / 総収入", yen(revenue))
col2.metric("正常举办总成本 / 開催総費用", yen(holding_cost))
col3.metric("正常举办利润/亏损 / 開催利益・損失", yen(holding_profit))

if nsj_cancel:
    col4.metric("取消时净结果 / キャンセル時純損益", yen(cancel_result))
else:
    col4.metric("取消状态 / キャンセル状態", "不取消 / なし")

st.info("收入计算 / 収入計算：\n" + revenue_process)

if not nsj_cancel:
    if holding_profit >= 0:
        st.success(f"不取消并正常举办时盈利 / 開催した場合の利益：{yen(holding_profit)}")
    else:
        st.error(f"不取消并正常举办时亏损 / 開催した場合の損失：{yen(abs(holding_profit))}")
else:
    if holding_profit >= cancel_result:
        st.info("金额判断：正常举办比取消更有利。/ 金額判断：開催した方がキャンセルより有利。")
    else:
        st.warning("金额判断：取消比正常举办更有利。/ 金額判断：キャンセルした方が開催より有利。")


# =========================
# 7. 图表 / Charts
# =========================

st.subheader("一、举办 vs 取消 可视化比较 / 開催 vs キャンセルの可視化比較")

if nsj_cancel:
    summary_df = pd.DataFrame({
        "项目 / 項目": [
            "总收入 / 総収入",
            "正常举办总成本 / 開催総費用",
            "正常举办利润/亏损 / 開催利益・損失",
            "取消费用 / キャンセル費用",
            "取消时净结果 / キャンセル時純損益"
        ],
        "金额 / 金額": [
            revenue,
            holding_cost,
            holding_profit,
            -cancel_cost,
            cancel_result
        ]
    })
else:
    summary_df = pd.DataFrame({
        "项目 / 項目": [
            "总收入 / 総収入",
            "正常举办总成本 / 開催総費用",
            "正常举办利润/亏损 / 開催利益・損失"
        ],
        "金额 / 金額": [
            revenue,
            holding_cost,
            holding_profit
        ]
    })

st.bar_chart(summary_df.set_index("项目 / 項目"))


st.subheader("二、正常举办成本构成 / 開催時の費用構成")
st.bar_chart(holding_df.set_index("项目 / 項目")["金额 / 金額"])
st.dataframe(holding_df, use_container_width=True)


st.subheader("三、取消费用构成 / キャンセル費用構成")

if nsj_cancel:
    st.bar_chart(cancel_df.set_index("项目 / 項目")["金额 / 金額"])
    st.dataframe(cancel_df, use_container_width=True)
else:
    st.write("当前选择：不取消。因此没有NSJ侧取消费用。/ 現在の選択：キャンセルしない。したがってNSJ側キャンセル費用は発生しません。")


# =========================
# 8. 具体计算过程 / Detailed process
# =========================

st.subheader("四、具体计算过程 / 具体的な計算過程")

with st.expander("查看正常举办时的计算过程 / 開催時の計算過程を見る"):
    st.write(f"报名人数 / 申込人数 = {registered_people} 人")
    st.write(f"募集期内取消报名人数 / 募集期間中の受講生側キャンセル人数 = {student_cancel_people} 人")
    st.write(f"实际参加人数 / 実際受講者数 = {registered_people} - {student_cancel_people} = {final_people} 人")
    st.write(revenue_process)

    for _, row in holding_df.iterrows():
        st.write(f"・{row['项目 / 項目']}：{row['计算过程 / 計算過程']}")

    st.write(f"总成本 / 総費用 = {yen(holding_cost)}")
    st.write(f"利润/亏损 / 利益・損失 = 总收入 - 总成本 = {yen(revenue)} - {yen(holding_cost)} = {yen(holding_profit)}")


if nsj_cancel:
    with st.expander("查看取消时的计算过程 / キャンセル時の計算過程を見る"):
        st.write(f"NSJ取消日期 / NSJキャンセル日：{cancel_date}")
        st.write(revenue_process)

        for _, row in cancel_df.iterrows():
            st.write(f"・{row['项目 / 項目']}：{row['计算过程 / 計算過程']}")

        st.write(f"取消费用合计 / キャンセル費用合計 = {yen(cancel_cost)}")
        st.write(f"取消时净结果 / キャンセル時純損益 = 收入 - 取消费用 = {yen(revenue)} - {yen(cancel_cost)} = {yen(cancel_result)}")
else:
    with st.expander("取消相关说明 / キャンセルに関する説明"):
        st.write("当前选择为不取消，因此不计算NSJ侧取消日期和取消费用。/ 現在はキャンセルしない設定のため、NSJ側キャンセル日は選択せず、キャンセル費用も計算しません。")


with st.expander("查看不亏损条件 / 損益分岐条件を見る"):
    if final_people > 0:
        break_even_fee = math.ceil(holding_cost / final_people)
        st.write("不亏损最低报名费 / 損益分岐受講料 = 总成本 ÷ 实际参加人数")
        st.write(f"{yen(holding_cost)} ÷ {final_people} = {yen(break_even_fee)} / 人")

    if fee > 0:
        break_even_people = math.ceil(holding_cost / fee)
        st.write("不亏损最低人数 / 損益分岐人数 = 总成本 ÷ 报名费")
        st.write(f"{yen(holding_cost)} ÷ {yen(fee)} = {break_even_people} 人")


# =========================
# 9. 重要日期 / Important dates
# =========================

st.subheader("五、重要日期 / 重要日程")

date_df = pd.DataFrame({
    "日期 / 日付": [
        WEB_AD_CONTRACT,
        PAMPHLET_PRINT_DATE,
        WEB_AD_START,
        PAMPHLET_SEND_DATE,
        RECRUIT_START,
        RECRUIT_END,
        VENUE_31_DAYS_BEFORE,
        VENUE_30_DAYS_BEFORE,
        PARTICIPANT_FIXED_DATE,
        PRE_MEETING_DATE,
        LUNCH_FREE_CANCEL_LIMIT,
        COFFEE_FREE_CANCEL_LIMIT,
        EVENT_DATE
    ],
    "含义 / 意味": [
        "Web广告契约日 / Web広告契約日",
        "宣传册印刷完成 / パンフレット印刷完了",
        "Web广告开始 / Web広告開始",
        "宣传册发送 / パンフレット発送",
        "募集开始 / 募集開始",
        "募集结束 / 募集終了",
        "会场31日前取消界限 / 会場31日前キャンセル境界",
        "会场30日以内取消开始 / 会場30日以内キャンセル開始",
        "参加人数确定 / 受講生数確定",
        "讲师事前会议日；代码中暂定 / 講師事前ミーティング日；仮定",
        "午餐免费取消期限 / 昼食無料キャンセル期限",
        "咖啡免费取消期限 / コーヒー無料キャンセル期限",
        "举办日 / 開催日"
    ]
})

st.dataframe(date_df, use_container_width=True)
