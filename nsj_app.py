import streamlit as st
import pandas as pd
from datetime import date
import math


# =========================================================
# 1. 日期设定 / 日付設定
# =========================================================

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

# Case里没有明确讲师事前会议日期，这里暂定为1月31日
PRE_MEETING_DATE = date(2021, 1, 31)

LUNCH_FREE_CANCEL_LIMIT = date(2021, 6, 16)
COFFEE_FREE_CANCEL_LIMIT = date(2021, 6, 18)


# =========================================================
# 2. 金额设定 / 金額設定
# =========================================================

VENUE_TOTAL = 400_000
VENUE_DEPOSIT = VENUE_TOTAL * 0.30

LECTURER_TOTAL = 500_000
LECTURER_CANCEL_AFTER_MEETING = 250_000

STAFF_MONTHLY_SALARY = 420_000
WORKING_DAYS_PER_MONTH = 21
STAFF_MAN_DAYS = 20
STAFF_DAILY_COST = STAFF_MONTHLY_SALARY / WORKING_DAYS_PER_MONTH
STAFF_COST = STAFF_DAILY_COST * STAFF_MAN_DAYS

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

STUDENT_CANCEL_PENALTY_RATE = 0.50


# =========================================================
# 3. 页面设定 / Page Setting
# =========================================================

st.set_page_config(
    page_title="NSJ Seminar Simulator",
    layout="wide"
)

with st.sidebar:
    language = st.radio(
        "语言 / 言語",
        ["中文", "日本語"],
        horizontal=True
    )


def L(cn, jp):
    return cn if language == "中文" else jp


def yen(x):
    return f"{x:,.0f} 円"


ITEM = L("项目", "項目")
AMOUNT = L("金额", "金額")
PROCESS = L("计算过程", "計算過程")


# =========================================================
# 4. 收入计算 / Revenue
# =========================================================

def calculate_revenue(registered_people, student_cancel_people, final_people, fee, nsj_cancel):
    penalty_revenue = student_cancel_people * fee * STUDENT_CANCEL_PENALTY_RATE

    if nsj_cancel:
        tuition_revenue = 0
        process = (
            L(
                "NSJ取消举办时，实际参加者报名费视为退还。",
                "NSJ側が開催をキャンセルする場合、実参加者の受講料は返金される前提。"
            )
            + "\n"
            + L(
                "实际参加者报名费收入 = 0 円",
                "実参加者の受講料収入 = 0 円"
            )
            + "\n"
            + L(
                f"募集期内取消报名违约金 = {student_cancel_people} × {yen(fee)} × 50% = {yen(penalty_revenue)}",
                f"募集期間中の受講生側キャンセル料 = {student_cancel_people} × {yen(fee)} × 50% = {yen(penalty_revenue)}"
            )
        )
    else:
        tuition_revenue = final_people * fee
        process = (
            L(
                f"实际参加者报名费收入 = {final_people} × {yen(fee)} = {yen(tuition_revenue)}",
                f"実参加者の受講料収入 = {final_people} × {yen(fee)} = {yen(tuition_revenue)}"
            )
            + "\n"
            + L(
                f"募集期内取消报名违约金 = {student_cancel_people} × {yen(fee)} × 50% = {yen(penalty_revenue)}",
                f"募集期間中の受講生側キャンセル料 = {student_cancel_people} × {yen(fee)} × 50% = {yen(penalty_revenue)}"
            )
        )

    total_revenue = tuition_revenue + penalty_revenue
    return total_revenue, tuition_revenue, penalty_revenue, process


# =========================================================
# 5. 咖啡费用计算 / Coffee
# =========================================================

def calculate_coffee_cost(final_people):
    coffee_people = final_people + 1 + 4
    required_cups = coffee_people
    order_units = math.ceil(required_cups / 10)
    order_cups = order_units * 10
    coffee_cost = order_units * COFFEE_UNIT_PER_10_CUPS

    process = L(
        f"需要杯数 = 实际参加人数{final_people}+讲师1+员工4 = {required_cups}杯；"
        f"只能10杯单位订购，所以订购 {order_cups}杯；"
        f"{order_units}单位 × {yen(COFFEE_UNIT_PER_10_CUPS)} = {yen(coffee_cost)}",
        f"必要杯数 = 実際受講者{final_people}+講師1+スタッフ4 = {required_cups}杯；"
        f"10杯単位でしか注文できないため、注文数は {order_cups}杯；"
        f"{order_units}単位 × {yen(COFFEE_UNIT_PER_10_CUPS)} = {yen(coffee_cost)}"
    )

    return coffee_cost, required_cups, order_cups, process


# =========================================================
# 6. 正常举办成本 / Holding Cost
# =========================================================

def calculate_holding_cost(final_people):
    rows = []

    rows.append([
        L("会场费", "会場費"),
        VENUE_TOTAL,
        L(
            f"会场使用料 = {yen(VENUE_TOTAL)}",
            f"会場使用料 = {yen(VENUE_TOTAL)}"
        )
    ])

    rows.append([
        L("讲师费", "講師料"),
        LECTURER_TOTAL,
        L(
            f"讲师费 = {yen(LECTURER_TOTAL)}",
            f"講師料 = {yen(LECTURER_TOTAL)}"
        )
    ])

    rows.append([
        L("员工工资", "社内従業員給与"),
        STAFF_COST,
        L(
            f"不计算税费，只计算人工成本：{yen(STAFF_MONTHLY_SALARY)} ÷ {WORKING_DAYS_PER_MONTH}日 × {STAFF_MAN_DAYS}人日 = {yen(STAFF_COST)}",
            f"税金・追加手当は計算せず、人件費のみ計算：{yen(STAFF_MONTHLY_SALARY)} ÷ {WORKING_DAYS_PER_MONTH}日 × {STAFF_MAN_DAYS}人日 = {yen(STAFF_COST)}"
        )
    ])

    rows.append([
        L("Web广告费", "Web広告費"),
        WEB_AD_TOTAL,
        L(
            f"Web广告费 = {yen(WEB_AD_TOTAL)}",
            f"Web広告費 = {yen(WEB_AD_TOTAL)}"
        )
    ])

    pamphlet_cost = PAMPHLET_PRINT_COST + PAMPHLET_SEND_COST
    rows.append([
        L("宣传册费用", "パンフレット費"),
        pamphlet_cost,
        L(
            f"印刷费 {yen(PAMPHLET_PRINT_COST)} + 邮送费 {yen(PAMPHLET_SEND_COST)} = {yen(pamphlet_cost)}",
            f"印刷費 {yen(PAMPHLET_PRINT_COST)} + 発送費 {yen(PAMPHLET_SEND_COST)} = {yen(pamphlet_cost)}"
        )
    ])

    textbook_cost = TEXTBOOK_UNIT * (final_people + SPARE_COPIES)
    case_cost = CASE_UNIT * (final_people + SPARE_COPIES)
    nameplate_cost = NAMEPLATE_UNIT * final_people
    material_cost = textbook_cost + case_cost + nameplate_cost

    rows.append([
        L("教材・案例・名牌", "教材・ケース・ネームプレート"),
        material_cost,
        L(
            f"教材 {TEXTBOOK_UNIT} × ({final_people}+备用{SPARE_COPIES}) = {yen(textbook_cost)}；"
            f"案例 {CASE_UNIT} × ({final_people}+备用{SPARE_COPIES}) = {yen(case_cost)}；"
            f"名牌 {NAMEPLATE_UNIT} × {final_people} = {yen(nameplate_cost)}；"
            f"合计 = {yen(material_cost)}",
            f"教材 {TEXTBOOK_UNIT} × ({final_people}+予備{SPARE_COPIES}) = {yen(textbook_cost)}；"
            f"ケース {CASE_UNIT} × ({final_people}+予備{SPARE_COPIES}) = {yen(case_cost)}；"
            f"ネームプレート {NAMEPLATE_UNIT} × {final_people} = {yen(nameplate_cost)}；"
            f"合計 = {yen(material_cost)}"
        )
    ])

    lunch_count = final_people + 1 + 4
    lunch_cost = LUNCH_UNIT * lunch_count

    rows.append([
        L("午餐费", "昼食代"),
        lunch_cost,
        L(
            f"{LUNCH_UNIT} × ({final_people}+讲师1+员工4) = {yen(lunch_cost)}",
            f"{LUNCH_UNIT} × ({final_people}+講師1+スタッフ4) = {yen(lunch_cost)}"
        )
    ])

    coffee_cost, required_cups, order_cups, coffee_process = calculate_coffee_cost(final_people)

    rows.append([
        L("咖啡服务", "コーヒーサービス"),
        coffee_cost,
        coffee_process
    ])

    df = pd.DataFrame(rows, columns=[ITEM, AMOUNT, PROCESS])
    total = df[AMOUNT].sum()
    return total, df


# =========================================================
# 7. 取消费用 / Cancellation Cost
# =========================================================

def calculate_cancel_cost(final_people, cancel_date):
    rows = []

    # 会场取消费
    if cancel_date <= VENUE_31_DAYS_BEFORE:
        venue_cancel = VENUE_DEPOSIT
        venue_process = L(
            f"举办31日前取消，只损失预约金：{yen(VENUE_TOTAL)} × 30% = {yen(venue_cancel)}",
            f"開催31日前までのキャンセルのため、予約金のみ：{yen(VENUE_TOTAL)} × 30% = {yen(venue_cancel)}"
        )
    else:
        venue_cancel = VENUE_TOTAL
        venue_process = L(
            f"举办30日以内取消，会场费全额成为取消费：{yen(venue_cancel)}",
            f"開催30日以内のキャンセルのため、会場費全額：{yen(venue_cancel)}"
        )

    rows.append([
        L("会场取消费", "会場キャンセル料"),
        venue_cancel,
        venue_process
    ])

    # 讲师取消费
    if cancel_date < PRE_MEETING_DATE:
        lecturer_cancel = 0
        lecturer_process = L(
            "事前会议前取消，讲师费 = 0 円",
            "事前ミーティング前のキャンセルのため、講師料 = 0 円"
        )
    else:
        lecturer_cancel = LECTURER_CANCEL_AFTER_MEETING
        lecturer_process = L(
            f"事前会议后由NSJ取消，需承担半额讲师费 = {yen(lecturer_cancel)}",
            f"事前ミーティング後にNSJ側都合でキャンセルするため、講師料半額 = {yen(lecturer_cancel)}"
        )

    rows.append([
        L("讲师取消费", "講師キャンセル料"),
        lecturer_cancel,
        lecturer_process
    ])

    # 员工工资：取消时按准备进度估算
    project_start = WEB_AD_CONTRACT
    total_days = (EVENT_DATE - project_start).days
    used_days = max(0, (cancel_date - project_start).days)
    ratio = min(1, used_days / total_days)

    staff_cancel = STAFF_COST * ratio

    rows.append([
        L("员工工资", "社内従業員給与"),
        staff_cancel,
        L(
            f"不计算税费，只按准备进度估算人工成本：{yen(STAFF_COST)} × {ratio:.2f} = {yen(staff_cancel)}",
            f"税金・追加手当は計算せず、準備進捗に応じて人件費を見積もる：{yen(STAFF_COST)} × {ratio:.2f} = {yen(staff_cancel)}"
        )
    ])

    # Web广告取消费
    if cancel_date < WEB_AD_CONTRACT:
        web_cancel = 0
        web_process = L(
            "Web广告契约前取消，费用 = 0 円",
            "Web広告契約前のキャンセルのため、費用 = 0 円"
        )
    elif cancel_date < WEB_AD_START:
        web_cancel = WEB_AD_ADVANCE
        web_process = L(
            f"广告开始前取消，只损失前金 = {yen(web_cancel)}",
            f"広告開始前のキャンセルのため、前金のみ = {yen(web_cancel)}"
        )
    else:
        web_cancel = WEB_AD_TOTAL
        web_process = L(
            f"广告已经开始，需支付全额 = {yen(web_cancel)}",
            f"広告開始後のキャンセルのため、全額 = {yen(web_cancel)}"
        )

    rows.append([
        L("Web广告取消费", "Web広告キャンセル料"),
        web_cancel,
        web_process
    ])

    # 宣传册取消费
    if cancel_date < PAMPHLET_PRINT_DATE:
        pamphlet_cancel = 0
        pamphlet_process = L(
            "宣传册印刷前取消，费用 = 0 円",
            "パンフレット印刷前のキャンセルのため、費用 = 0 円"
        )
    elif cancel_date < PAMPHLET_SEND_DATE:
        pamphlet_cancel = PAMPHLET_PRINT_COST
        pamphlet_process = L(
            f"已印刷但未邮送，只发生印刷费 = {yen(pamphlet_cancel)}",
            f"印刷後・発送前のため、印刷費のみ = {yen(pamphlet_cancel)}"
        )
    else:
        pamphlet_cancel = PAMPHLET_PRINT_COST + PAMPHLET_SEND_COST
        pamphlet_process = L(
            f"已邮送，印刷费+邮送费 = {yen(pamphlet_cancel)}",
            f"発送済みのため、印刷費＋発送費 = {yen(pamphlet_cancel)}"
        )

    rows.append([
        L("宣传册取消费", "パンフレットキャンセル料"),
        pamphlet_cancel,
        pamphlet_process
    ])

    # 教材、案例、名牌取消费
    if cancel_date < PARTICIPANT_FIXED_DATE:
        material_cancel = 0
        material_process = L(
            "参加人数尚未确定，教材・案例・名牌费用 = 0 円",
            "受講生数確定前のため、教材・ケース・ネームプレート費 = 0 円"
        )
    else:
        textbook_cost = TEXTBOOK_UNIT * (final_people + SPARE_COPIES)
        case_cost = CASE_UNIT * (final_people + SPARE_COPIES)
        nameplate_cost = NAMEPLATE_UNIT * final_people
        material_cancel = textbook_cost + case_cost + nameplate_cost
        material_process = L(
            f"教材 {yen(textbook_cost)} + 案例 {yen(case_cost)} + 名牌 {yen(nameplate_cost)} = {yen(material_cancel)}",
            f"教材 {yen(textbook_cost)} + ケース {yen(case_cost)} + ネームプレート {yen(nameplate_cost)} = {yen(material_cancel)}"
        )

    rows.append([
        L("教材・案例・名牌取消费", "教材・ケース・ネームプレートキャンセル料"),
        material_cancel,
        material_process
    ])

    # 午餐取消费
    lunch_count = final_people + 1 + 4
    lunch_total = LUNCH_UNIT * lunch_count

    if cancel_date <= LUNCH_FREE_CANCEL_LIMIT:
        lunch_cancel = 0
        lunch_process = L(
            "举办3日前以前取消，午餐费 = 0 円",
            "開催3日前までのキャンセルのため、昼食代 = 0 円"
        )
    else:
        lunch_cancel = lunch_total
        lunch_process = L(
            f"超过免费取消期限：{LUNCH_UNIT} × {lunch_count} = {yen(lunch_cancel)}",
            f"無料キャンセル期限後：{LUNCH_UNIT} × {lunch_count} = {yen(lunch_cancel)}"
        )

    rows.append([
        L("午餐取消费", "昼食キャンセル料"),
        lunch_cancel,
        lunch_process
    ])

    # 咖啡取消费
    coffee_total, required_cups, order_cups, coffee_base_process = calculate_coffee_cost(final_people)

    if cancel_date <= COFFEE_FREE_CANCEL_LIMIT:
        coffee_cancel = 0
        coffee_process = L(
            "举办前日以前取消，咖啡服务费 = 0 円",
            "開催前日までのキャンセルのため、コーヒーサービス費 = 0 円"
        )
    else:
        coffee_cancel = coffee_total
        coffee_process = L(
            f"超过免费取消期限，需要杯数 {required_cups}杯，10杯单位订购为 {order_cups}杯，咖啡服务费 = {yen(coffee_cancel)}",
            f"無料キャンセル期限後。必要杯数 {required_cups}杯、10杯単位のため注文数は {order_cups}杯、コーヒーサービス費 = {yen(coffee_cancel)}"
        )

    rows.append([
        L("咖啡取消费", "コーヒーキャンセル料"),
        coffee_cancel,
        coffee_process
    ])

    df = pd.DataFrame(rows, columns=[ITEM, AMOUNT, PROCESS])
    total = df[AMOUNT].sum()
    return total, df


# =========================================================
# 8. UI 输入区 / User Interface
# =========================================================

st.title(L(
    "NSJ研修会 利润・取消费用模拟器",
    "NSJセミナー 利益・キャンセル費用シミュレーション"
))

st.caption(L(
    "选择人数、报名费、是否取消，即可显示利润/亏损和取消费用。",
    "人数・受講料・キャンセル有無を選ぶだけで、利益/損失とキャンセル費用を可視化します。"
))

with st.sidebar:
    st.header(L("选择条件", "条件選択"))

    registered_people = st.slider(
        L("报名人数", "申込人数"),
        min_value=30,
        max_value=60,
        value=40,
        step=1
    )

    fee = st.selectbox(
        L("报名费（日元/人）", "受講料（円/人）"),
        options=[
            25_000, 30_000, 35_000, 40_000,
            45_000, 50_000, 55_000, 60_000,
            65_000, 70_000, 75_000, 80_000
        ],
        index=7
    )

    student_cancel_people = st.slider(
        L("募集期内取消报名人数", "募集期間中の受講生側キャンセル人数"),
        min_value=0,
        max_value=registered_people,
        value=0,
        step=1
    )

    final_people = registered_people - student_cancel_people

    cancel_choice = st.radio(
        L("NSJ是否取消举办？", "NSJ側が開催をキャンセルするか？"),
        [L("不取消", "キャンセルしない"), L("取消", "キャンセルする")],
        index=0
    )

    nsj_cancel = cancel_choice == L("取消", "キャンセルする")

    if nsj_cancel:
        cancel_date = st.date_input(
            L("NSJ取消日期", "NSJキャンセル日"),
            value=date(2021, 5, 21),
            min_value=date(2021, 1, 1),
            max_value=EVENT_DATE
        )
    else:
        cancel_date = None

    st.markdown("---")
    st.write(L(f"举办日：{EVENT_DATE}", f"開催日：{EVENT_DATE}"))
    st.write(L(f"报名人数：{registered_people} 人", f"申込人数：{registered_people} 人"))
    st.write(L(f"募集期内取消：{student_cancel_people} 人", f"募集期間中キャンセル：{student_cancel_people} 人"))
    st.write(L(f"实际参加人数：{final_people} 人", f"実際受講者数：{final_people} 人"))


# =========================================================
# 9. 计算 / Calculation
# =========================================================

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
    cancel_result = None
    cancel_df = pd.DataFrame(columns=[ITEM, AMOUNT, PROCESS])


# =========================================================
# 10. 结果卡片 / Result Cards
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(L("总收入", "総収入"), yen(revenue))
col2.metric(L("正常举办总成本", "開催総費用"), yen(holding_cost))
col3.metric(L("正常举办利润/亏损", "開催利益・損失"), yen(holding_profit))

if nsj_cancel:
    col4.metric(L("取消时净结果", "キャンセル時純損益"), yen(cancel_result))
else:
    col4.metric(L("取消状态", "キャンセル状態"), L("不取消", "なし"))

st.info(L("收入计算：", "収入計算：") + "\n" + revenue_process)

if not nsj_cancel:
    if holding_profit >= 0:
        st.success(L(
            f"不取消并正常举办时盈利：{yen(holding_profit)}",
            f"開催した場合の利益：{yen(holding_profit)}"
        ))
    else:
        st.error(L(
            f"不取消并正常举办时亏损：{yen(abs(holding_profit))}",
            f"開催した場合の損失：{yen(abs(holding_profit))}"
        ))
else:
    if holding_profit >= cancel_result:
        st.info(L(
            "金额判断：正常举办比取消更有利。",
            "金額判断：開催した方がキャンセルより有利。"
        ))
    else:
        st.warning(L(
            "金额判断：取消比正常举办更有利。",
            "金額判断：キャンセルした方が開催より有利。"
        ))


# =========================================================
# 11. 图表和表格 / Charts and Tables
# =========================================================

st.subheader(L("一、举办 vs 取消 可视化比较", "一、開催 vs キャンセルの可視化比較"))

if nsj_cancel:
    summary_df = pd.DataFrame({
        ITEM: [
            L("总收入", "総収入"),
            L("正常举办总成本", "開催総費用"),
            L("正常举办利润/亏损", "開催利益・損失"),
            L("取消费用", "キャンセル費用"),
            L("取消时净结果", "キャンセル時純損益")
        ],
        AMOUNT: [
            revenue,
            holding_cost,
            holding_profit,
            -cancel_cost,
            cancel_result
        ]
    })
else:
    summary_df = pd.DataFrame({
        ITEM: [
            L("总收入", "総収入"),
            L("正常举办总成本", "開催総費用"),
            L("正常举办利润/亏损", "開催利益・損失")
        ],
        AMOUNT: [
            revenue,
            holding_cost,
            holding_profit
        ]
    })

st.bar_chart(summary_df.set_index(ITEM))

st.subheader(L("二、正常举办成本构成", "二、開催時の費用構成"))
st.bar_chart(holding_df.set_index(ITEM)[AMOUNT])
st.dataframe(holding_df, use_container_width=True)

st.subheader(L("三、取消费用构成", "三、キャンセル費用構成"))

if nsj_cancel:
    st.bar_chart(cancel_df.set_index(ITEM)[AMOUNT])
    st.dataframe(cancel_df, use_container_width=True)
else:
    st.write(L(
        "当前选择：不取消。因此没有NSJ侧取消费用。",
        "現在の選択：キャンセルしない。したがってNSJ側キャンセル費用は発生しません。"
    ))


# =========================================================
# 12. 具体计算过程 / Detailed Calculation
# =========================================================

st.subheader(L("四、具体计算过程", "四、具体的な計算過程"))

with st.expander(L("查看正常举办时的计算过程", "開催時の計算過程を見る")):
    st.write(L(f"报名人数 = {registered_people} 人", f"申込人数 = {registered_people} 人"))
    st.write(L(
        f"募集期内取消报名人数 = {student_cancel_people} 人",
        f"募集期間中の受講生側キャンセル人数 = {student_cancel_people} 人"
    ))
    st.write(L(
        f"实际参加人数 = {registered_people} - {student_cancel_people} = {final_people} 人",
        f"実際受講者数 = {registered_people} - {student_cancel_people} = {final_people} 人"
    ))
    st.write(revenue_process)

    for _, row in holding_df.iterrows():
        st.write(f"・{row[ITEM]}：{row[PROCESS]}")

    st.write(L(
        f"总成本 = {yen(holding_cost)}",
        f"総費用 = {yen(holding_cost)}"
    ))
    st.write(L(
        f"利润/亏损 = 总收入 - 总成本 = {yen(revenue)} - {yen(holding_cost)} = {yen(holding_profit)}",
        f"利益・損失 = 総収入 - 総費用 = {yen(revenue)} - {yen(holding_cost)} = {yen(holding_profit)}"
    ))

if nsj_cancel:
    with st.expander(L("查看取消时的计算过程", "キャンセル時の計算過程を見る")):
        st.write(L(f"NSJ取消日期：{cancel_date}", f"NSJキャンセル日：{cancel_date}"))
        st.write(revenue_process)

        for _, row in cancel_df.iterrows():
            st.write(f"・{row[ITEM]}：{row[PROCESS]}")

        st.write(L(
            f"取消费用合计 = {yen(cancel_cost)}",
            f"キャンセル費用合計 = {yen(cancel_cost)}"
        ))
        st.write(L(
            f"取消时净结果 = 收入 - 取消费用 = {yen(revenue)} - {yen(cancel_cost)} = {yen(cancel_result)}",
            f"キャンセル時純損益 = 収入 - キャンセル費用 = {yen(revenue)} - {yen(cancel_cost)} = {yen(cancel_result)}"
        ))

with st.expander(L("查看不亏损条件", "損益分岐条件を見る")):
    if final_people > 0:
        break_even_fee = math.ceil(holding_cost / final_people)
        st.write(L(
            f"不亏损最低报名费 = 总成本 ÷ 实际参加人数 = {yen(holding_cost)} ÷ {final_people} = {yen(break_even_fee)} / 人",
            f"損益分岐受講料 = 総費用 ÷ 実際受講者数 = {yen(holding_cost)} ÷ {final_people} = {yen(break_even_fee)} / 人"
        ))

    break_even_people = math.ceil(holding_cost / fee)
    st.write(L(
        f"在报名费为 {yen(fee)} 的情况下，不亏损最低人数 = {break_even_people} 人",
        f"受講料が {yen(fee)} の場合、損益分岐人数 = {break_even_people} 人"
    ))


# =========================================================
# 13. 重要日期 / Important Dates
# =========================================================

st.subheader(L("五、重要日期", "五、重要日程"))

date_df = pd.DataFrame({
    L("日期", "日付"): [
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
    L("含义", "意味"): [
        L("Web广告契约日", "Web広告契約日"),
        L("宣传册印刷完成", "パンフレット印刷完了"),
        L("Web广告开始", "Web広告開始"),
        L("宣传册发送", "パンフレット発送"),
        L("募集开始", "募集開始"),
        L("募集结束", "募集終了"),
        L("会场31日前取消界限", "会場31日前キャンセル境界"),
        L("会场30日以内取消开始", "会場30日以内キャンセル開始"),
        L("参加人数确定", "受講生数確定"),
        L("讲师事前会议日；代码中暂定", "講師事前ミーティング日；仮定"),
        L("午餐免费取消期限", "昼食無料キャンセル期限"),
        L("咖啡免费取消期限", "コーヒー無料キャンセル期限"),
        L("举办日", "開催日")
    ]
})

st.dataframe(date_df, use_container_width=True)
