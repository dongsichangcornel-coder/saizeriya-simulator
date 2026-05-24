import streamlit as st
import pandas as pd
from datetime import date
import math


# =========================
# 1. 2021年日期设定
# =========================

EVENT_DATE = date(2021, 6, 19)  # 2021年6月第3个周六

# 重要日期
WEB_AD_CONTRACT = date(2021, 2, 12)       # 2月第2金曜日：Web广告契约
WEB_AD_START = date(2021, 3, 12)          # 3月第2金曜日：Web广告开始
WEB_AD_END = date(2021, 5, 14)            # 5月第2金曜日：Web广告结束

PAMPHLET_PRINT_DATE = date(2021, 2, 26)  # 2月末：宣传册印刷完成
PAMPHLET_SEND_DATE = date(2021, 3, 15)   # 3月中旬：宣传册发送

RECRUIT_START = date(2021, 4, 26)        # 4月第4周月曜日：募集开始
RECRUIT_END = date(2021, 5, 14)          # 5月第2金曜日：募集结束
PARTICIPANT_FIXED_DATE = date(2021, 5, 21)  # 5月第3金曜日：参加人数确定

VENUE_31_DAYS_BEFORE = date(2021, 5, 19)
VENUE_30_DAYS_BEFORE = date(2021, 5, 20)

# case里没有明确写讲师事前会议日期，这里设为5月31日，可根据老师要求修改
PRE_MEETING_DATE = date(2021, 5, 31)

LUNCH_FREE_CANCEL_LIMIT = date(2021, 6, 16)   # 举办3日前
COFFEE_FREE_CANCEL_LIMIT = date(2021, 6, 18)  # 举办前日


# =========================
# 2. 金额设定
# =========================

VENUE_TOTAL = 400_000
VENUE_DEPOSIT = VENUE_TOTAL * 0.30

LECTURER_TOTAL = 500_000
LECTURER_CANCEL_AFTER_MEETING = 250_000

STAFF_MONTHLY_SALARY = 420_000
WORKING_DAYS_PER_MONTH = 21
STAFF_DAILY_COST = STAFF_MONTHLY_SALARY / WORKING_DAYS_PER_MONTH
STAFF_MAN_DAYS = 20

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


# =========================
# 3. 工具函数
# =========================

def yen(x):
    return f"{x:,.0f} 円"


def calculate_holding_cost(participants):
    items = []

    items.append({
        "项目": "会场费",
        "金额": VENUE_TOTAL,
        "计算过程": f"会场使用料 = {yen(VENUE_TOTAL)}"
    })

    items.append({
        "项目": "讲师费",
        "金额": LECTURER_TOTAL,
        "计算过程": f"讲师费 = {yen(LECTURER_TOTAL)}"
    })

    staff_cost = STAFF_DAILY_COST * STAFF_MAN_DAYS
    items.append({
        "项目": "员工工资",
        "金额": staff_cost,
        "计算过程": f"{yen(STAFF_MONTHLY_SALARY)} ÷ {WORKING_DAYS_PER_MONTH}日 × {STAFF_MAN_DAYS}人日 = {yen(staff_cost)}"
    })

    items.append({
        "项目": "Web广告费",
        "金额": WEB_AD_TOTAL,
        "计算过程": f"Web广告费 = {yen(WEB_AD_TOTAL)}"
    })

    pamphlet_cost = PAMPHLET_PRINT_COST + PAMPHLET_SEND_COST
    items.append({
        "项目": "宣传册费用",
        "金额": pamphlet_cost,
        "计算过程": f"印刷 {yen(PAMPHLET_PRINT_COST)} + 邮送 {yen(PAMPHLET_SEND_COST)} = {yen(pamphlet_cost)}"
    })

    textbook_cost = TEXTBOOK_UNIT * (participants + SPARE_COPIES)
    case_cost = CASE_UNIT * (participants + SPARE_COPIES)
    nameplate_cost = NAMEPLATE_UNIT * participants
    material_cost = textbook_cost + case_cost + nameplate_cost

    items.append({
        "项目": "教材・案例・名牌",
        "金额": material_cost,
        "计算过程": (
            f"教材 {TEXTBOOK_UNIT} × ({participants}+备用{SPARE_COPIES}) = {yen(textbook_cost)}；"
            f"案例 {CASE_UNIT} × ({participants}+备用{SPARE_COPIES}) = {yen(case_cost)}；"
            f"名牌 {NAMEPLATE_UNIT} × {participants} = {yen(nameplate_cost)}；"
            f"合计 = {yen(material_cost)}"
        )
    })

    lunch_count = participants + 1 + 4
    lunch_cost = LUNCH_UNIT * lunch_count
    items.append({
        "项目": "午餐费",
        "金额": lunch_cost,
        "计算过程": f"{LUNCH_UNIT} × ({participants}+讲师1+员工4) = {yen(lunch_cost)}"
    })

    coffee_units = math.ceil(COFFEE_CUPS / 10)
    coffee_cost = coffee_units * COFFEE_UNIT_PER_10_CUPS
    items.append({
        "项目": "咖啡服务",
        "金额": coffee_cost,
        "计算过程": f"{COFFEE_CUPS}杯 ÷ 10杯单位 × {yen(COFFEE_UNIT_PER_10_CUPS)} = {yen(coffee_cost)}"
    })

    total = sum(item["金额"] for item in items)
    return total, items


def calculate_cancellation_cost(participants, cancel_date):
    items = []

    # 会场费
    if cancel_date <= VENUE_31_DAYS_BEFORE:
        venue_cancel = VENUE_DEPOSIT
        venue_process = f"举办31日前取消，只损失预约金：{yen(VENUE_TOTAL)} × 30% = {yen(venue_cancel)}"
    else:
        venue_cancel = VENUE_TOTAL
        venue_process = f"举办30日以内取消，会场费全额成为取消费：{yen(venue_cancel)}"

    items.append({
        "项目": "会场取消费",
        "金额": venue_cancel,
        "计算过程": venue_process
    })

    # 讲师费
    if cancel_date < PRE_MEETING_DATE:
        lecturer_cancel = 0
        lecturer_process = "事前会议前取消，讲师费 = 0 円"
    else:
        lecturer_cancel = LECTURER_CANCEL_AFTER_MEETING
        lecturer_process = f"事前会议后由NSJ取消，需承担半额讲师费 = {yen(lecturer_cancel)}"

    items.append({
        "项目": "讲师取消费",
        "金额": lecturer_cancel,
        "计算过程": lecturer_process
    })

    # 员工工资：这里按准备进度估算
    project_start = WEB_AD_CONTRACT
    total_days = (EVENT_DATE - project_start).days
    used_days = max(0, (cancel_date - project_start).days)
    ratio = min(1, used_days / total_days)
    staff_cancel = STAFF_DAILY_COST * STAFF_MAN_DAYS * ratio

    items.append({
        "项目": "员工工资",
        "金额": staff_cancel,
        "计算过程": f"按准备进度估算：{yen(STAFF_DAILY_COST)} × {STAFF_MAN_DAYS}人日 × {ratio:.2f} = {yen(staff_cancel)}"
    })

    # Web广告
    if cancel_date < WEB_AD_CONTRACT:
        web_cancel = 0
        web_process = "Web广告契约前取消，费用 = 0 円"
    elif cancel_date < WEB_AD_START:
        web_cancel = WEB_AD_ADVANCE
        web_process = f"广告开始前取消，只损失前金 = {yen(web_cancel)}"
    else:
        web_cancel = WEB_AD_TOTAL
        web_process = f"广告已经开始，需支付全额 = {yen(web_cancel)}"

    items.append({
        "项目": "Web广告取消费",
        "金额": web_cancel,
        "计算过程": web_process
    })

    # 宣传册
    if cancel_date < PAMPHLET_PRINT_DATE:
        pamphlet_cancel = 0
        pamphlet_process = "宣传册印刷前取消，费用 = 0 円"
    elif cancel_date < PAMPHLET_SEND_DATE:
        pamphlet_cancel = PAMPHLET_PRINT_COST
        pamphlet_process = f"已印刷但未邮送，只发生印刷费 = {yen(pamphlet_cancel)}"
    else:
        pamphlet_cancel = PAMPHLET_PRINT_COST + PAMPHLET_SEND_COST
        pamphlet_process = f"已邮送，印刷费+邮送费 = {yen(pamphlet_cancel)}"

    items.append({
        "项目": "宣传册取消费",
        "金额": pamphlet_cancel,
        "计算过程": pamphlet_process
    })

    # 教材、案例、名牌
    if cancel_date < PARTICIPANT_FIXED_DATE:
        material_cancel = 0
        material_process = "参加人数尚未确定，教材・案例・名牌费用 = 0 円"
    else:
        textbook_cost = TEXTBOOK_UNIT * (participants + SPARE_COPIES)
        case_cost = CASE_UNIT * (participants + SPARE_COPIES)
        nameplate_cost = NAMEPLATE_UNIT * participants
        material_cancel = textbook_cost + case_cost + nameplate_cost
        material_process = (
            f"教材 {yen(textbook_cost)} + 案例 {yen(case_cost)} + 名牌 {yen(nameplate_cost)} "
            f"= {yen(material_cancel)}"
        )

    items.append({
        "项目": "教材・案例・名牌取消费",
        "金额": material_cancel,
        "计算过程": material_process
    })

    # 午餐
    lunch_count = participants + 1 + 4
    lunch_total = LUNCH_UNIT * lunch_count

    if cancel_date <= LUNCH_FREE_CANCEL_LIMIT:
        lunch_cancel = 0
        lunch_process = "举办3日前以前取消，午餐费 = 0 円"
    else:
        lunch_cancel = lunch_total
        lunch_process = f"超过免费取消期限：{LUNCH_UNIT} × {lunch_count} = {yen(lunch_cancel)}"

    items.append({
        "项目": "午餐取消费",
        "金额": lunch_cancel,
        "计算过程": lunch_process
    })

    # 咖啡
    coffee_total = math.ceil(COFFEE_CUPS / 10) * COFFEE_UNIT_PER_10_CUPS

    if cancel_date <= COFFEE_FREE_CANCEL_LIMIT:
        coffee_cancel = 0
        coffee_process = "举办前日以前取消，咖啡服务费 = 0 円"
    else:
        coffee_cancel = coffee_total
        coffee_process = f"超过免费取消期限，咖啡服务费 = {yen(coffee_cancel)}"

    items.append({
        "项目": "咖啡取消费",
        "金额": coffee_cancel,
        "计算过程": coffee_process
    })

    total = sum(item["金额"] for item in items)
    return total, items


# =========================
# 4. Streamlit 画面
# =========================

st.set_page_config(
    page_title="NSJ Seminar Simulator",
    layout="wide"
)

st.title("NSJ セミナー 利益・取消費用シミュレーション")
st.caption("人数・报名费・取消日期を選ぶだけで、利润/亏损和取消费用を可视化します。")

with st.sidebar:
    st.header("选择条件")

    participants = st.slider(
        "参加人数",
        min_value=1,
        max_value=50,
        value=40,
        step=1
    )

    fee = st.selectbox(
        "报名费（日元/人）",
        options=[
            25_000, 30_000, 35_000, 40_000,
            45_000, 50_000, 55_000, 60_000,
            65_000, 70_000, 75_000, 80_000
        ],
        index=7
    )

    cancel_date = st.date_input(
        "取消日期",
        value=date(2021, 5, 21),
        min_value=date(2021, 1, 1),
        max_value=EVENT_DATE
    )

    st.markdown("---")
    st.write("举办日：2021-06-19")
    st.write("人数上限：50人")


# =========================
# 5. 计算
# =========================

revenue = participants * fee

holding_cost, holding_items = calculate_holding_cost(participants)
profit = revenue - holding_cost

cancel_cost, cancel_items = calculate_cancellation_cost(participants, cancel_date)
cancel_profit = -cancel_cost

break_even_fee = math.ceil(holding_cost / participants)
break_even_participants = math.ceil(holding_cost / fee)


# =========================
# 6. 结果卡片
# =========================

col1, col2, col3, col4 = st.columns(4)

col1.metric("总收入", yen(revenue))
col2.metric("正常举办总成本", yen(holding_cost))
col3.metric("正常举办利润/亏损", yen(profit))
col4.metric("取消损失", f"-{yen(cancel_cost)}")

if profit >= 0:
    st.success(f"正常举办时盈利：{yen(profit)}")
else:
    st.error(f"正常举办时亏损：{yen(abs(profit))}")

if profit >= cancel_profit:
    st.info("金额判断：正常举办比取消更有利。")
else:
    st.warning("金额判断：取消比正常举办更有利。")


# =========================
# 7. 图表
# =========================

st.subheader("一、举办 vs 取消 可视化比较")

summary_df = pd.DataFrame({
    "项目": ["总收入", "正常举办总成本", "正常举办利润/亏损", "取消损失"],
    "金额": [revenue, holding_cost, profit, -cancel_cost]
})

st.bar_chart(summary_df.set_index("项目"))


st.subheader("二、正常举办成本构成")

holding_df = pd.DataFrame(holding_items)
st.bar_chart(holding_df.set_index("项目")["金额"])

st.dataframe(
    holding_df[["项目", "金额", "计算过程"]],
    use_container_width=True
)


st.subheader("三、取消费用构成")

cancel_df = pd.DataFrame(cancel_items)
st.bar_chart(cancel_df.set_index("项目")["金额"])

st.dataframe(
    cancel_df[["项目", "金额", "计算过程"]],
    use_container_width=True
)


# =========================
# 8. 具体计算过程
# =========================

st.subheader("四、具体计算过程")

with st.expander("查看正常举办时的计算过程"):
    st.write(f"收入 = 参加人数 × 报名费 = {participants} × {yen(fee)} = {yen(revenue)}")
    for item in holding_items:
        st.write(f"・{item['项目']}：{item['计算过程']}")
    st.write(f"总成本 = {yen(holding_cost)}")
    st.write(f"利润/亏损 = 收入 - 总成本 = {yen(revenue)} - {yen(holding_cost)} = {yen(profit)}")

with st.expander("查看取消时的计算过程"):
    st.write(f"取消日期：{cancel_date}")
    for item in cancel_items:
        st.write(f"・{item['项目']}：{item['计算过程']}")
    st.write(f"取消费用合计 = {yen(cancel_cost)}")
    st.write(f"取消时收入按 0 计算，因此损失 = -{yen(cancel_cost)}")

with st.expander("查看不亏损条件"):
    st.write(f"不亏损最低报名费 = 总成本 ÷ 参加人数")
    st.write(f"{yen(holding_cost)} ÷ {participants} = {yen(break_even_fee)} / 人")
    st.write("")
    st.write(f"在报名费为 {yen(fee)} 的情况下，不亏损最低人数 = 总成本 ÷ 报名费")
    st.write(f"{yen(holding_cost)} ÷ {yen(fee)} = {break_even_participants} 人")


# =========================
# 9. 重要日期表
# =========================

st.subheader("五、重要日期")

date_df = pd.DataFrame({
    "日期": [
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
    "含义": [
        "Web广告契约日",
        "宣传册印刷完成",
        "Web广告开始",
        "宣传册发送",
        "募集开始",
        "募集结束",
        "会场31日前取消界限",
        "会场30日以内取消开始",
        "参加人数确定",
        "讲师事前会议日；代码中暂定",
        "午餐免费取消期限",
        "咖啡免费取消期限",
        "セミナー举办日"
    ]
})

st.dataframe(date_df, use_container_width=True)
