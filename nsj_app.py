import streamlit as st
import pandas as pd
from datetime import date
import math


# =========================================================
# 1. 日期设定 / 日付設定
# =========================================================

EVENT_DATE = date(2021, 6, 19)  # セミナー開催日：2021年6月第3土曜日

# 题目指定时点 / 問題文指定タイミング
TIMING_A = date(2020, 12, 18)  # 半年前：2020年12月第3金曜日
TIMING_B = date(2021, 3, 19)   # 3ヵ月前：2021年3月第3金曜日
TIMING_C = date(2021, 5, 21)   # 1ヵ月前：2021年5月第3金曜日
TIMING_D = date(2021, 6, 18)   # 前日：2021年6月第3金曜日

# 根据题目重新设定 / 問題文に合わせた設定
VENUE_RESERVATION_DATE = TIMING_A       # 会场预约已完成
PRE_MEETING_DATE = TIMING_A             # 大泽教授MTG已完成
WEB_AD_CONTRACT = TIMING_A              # 广告契约已完成
LECTURER_ADVANCE_PAYMENT_DATE = date(2020, 12, 31)  # 前金支付日，仅作为现金流说明

# 其他日期 / その他の日程
WEB_AD_START = date(2021, 3, 12)        # Web广告开始日
PAMPHLET_PRINT_DATE = date(2021, 2, 26)
PAMPHLET_SEND_DATE = TIMING_B           # 3ヵ月前にはパンフレット郵送済み
RECRUIT_START = date(2021, 4, 26)
RECRUIT_END = date(2021, 5, 14)
PARTICIPANT_FIXED_DATE = TIMING_C       # 5月第3金曜日に人数确定
VENUE_FULL_PAYMENT_DATE = TIMING_C      # 1ヵ月前には会場費全額支払い済み

LUNCH_FREE_CANCEL_LIMIT = date(2021, 6, 16)   # 举办3日前
COFFEE_FREE_CANCEL_LIMIT = date(2021, 6, 18)  # 举办前日


# =========================================================
# 2. 金额设定 / 金額設定
# =========================================================

VENUE_TOTAL = 400_000
VENUE_DEPOSIT = VENUE_TOTAL * 0.30

LECTURER_TOTAL = 500_000
LECTURER_CANCEL_AFTER_MEETING = 250_000
LECTURER_ADVANCE = 100_000

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
# 3. Streamlit 页面设定 / Page Setting
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
# 5. 咖啡费用计算 / Coffee Cost
# =========================================================

def calculate_coffee_cost(selected_coffee_cups):
    order_cups = selected_coffee_cups
    order_units = order_cups // 10
    coffee_cost = order_units * COFFEE_UNIT_PER_10_CUPS

    process = L(
        f"选择咖啡杯数 = {order_cups}杯；咖啡只能10杯单位订购；"
        f"{order_units}单位 × {yen(COFFEE_UNIT_PER_10_CUPS)} = {yen(coffee_cost)}",
        f"選択したコーヒー杯数 = {order_cups}杯；コーヒーは10杯単位で注文；"
        f"{order_units}単位 × {yen(COFFEE_UNIT_PER_10_CUPS)} = {yen(coffee_cost)}"
    )

    return coffee_cost, order_cups, process


# =========================================================
# 6. 成本组件计算 / Cost Components
# =========================================================

def calculate_component_rows(final_people, selected_coffee_cups, include_staff_cost, cancel_date=None):
    normal_rows = []
    cancel_rows = []
    avoidable_rows = []

    normal_total = 0
    cancel_total = 0
    avoidable_total = 0

    def add_component(label, normal_amount, normal_process, cancel_amount=None, cancel_process=None):
        nonlocal normal_total, cancel_total, avoidable_total

        normal_rows.append([label, normal_amount, normal_process])
        normal_total += normal_amount

        if cancel_date is not None:
            cancel_rows.append([label, cancel_amount, cancel_process])
            cancel_total += cancel_amount

            avoidable_amount = max(0, normal_amount - cancel_amount)
            if avoidable_amount > 0:
                avoidable_process = L(
                    f"正常举办时成本 {yen(normal_amount)} - 取消后仍需承担成本 {yen(cancel_amount)} = 可回避原价 {yen(avoidable_amount)}",
                    f"開催した場合の原価 {yen(normal_amount)} - キャンセル後も負担する原価 {yen(cancel_amount)} = 回避可能原価 {yen(avoidable_amount)}"
                )
                avoidable_rows.append([label, avoidable_amount, avoidable_process])
                avoidable_total += avoidable_amount

    # 1. 会场费 / 会場費
    normal_venue = VENUE_TOTAL
    normal_venue_process = L(
        f"正常举办时，会场使用料 = {yen(VENUE_TOTAL)}",
        f"開催する場合、会場使用料 = {yen(VENUE_TOTAL)}"
    )

    if cancel_date is not None:
        if cancel_date < VENUE_RESERVATION_DATE:
            cancel_venue = 0
            cancel_venue_process = L(
                "会场预约前取消，会场相关成本 = 0 円",
                "会場予約前のキャンセルのため、会場関連原価 = 0 円"
            )
        elif cancel_date < VENUE_FULL_PAYMENT_DATE:
            cancel_venue = VENUE_DEPOSIT
            cancel_venue_process = L(
                f"会场已预约，但尚未全额支付，只损失预约金：{yen(VENUE_TOTAL)} × 30% = {yen(cancel_venue)}",
                f"会場予約済みだが全額支払前のため、予約金のみ：{yen(VENUE_TOTAL)} × 30% = {yen(cancel_venue)}"
            )
        else:
            cancel_venue = VENUE_TOTAL
            cancel_venue_process = L(
                f"会场费已经全额支付，取消后仍需承担全额 = {yen(cancel_venue)}",
                f"会場費は全額支払済みのため、キャンセル後も全額負担 = {yen(cancel_venue)}"
            )
    else:
        cancel_venue = None
        cancel_venue_process = None

    add_component(
        L("会场费", "会場費"),
        normal_venue,
        normal_venue_process,
        cancel_venue,
        cancel_venue_process
    )

    # 2. 讲师费 / 講師料
    normal_lecturer = LECTURER_TOTAL
    normal_lecturer_process = L(
        f"正常举办时，讲师费 = {yen(LECTURER_TOTAL)}",
        f"開催する場合、講師料 = {yen(LECTURER_TOTAL)}"
    )

    if cancel_date is not None:
        if cancel_date < PRE_MEETING_DATE:
            cancel_lecturer = 0
            cancel_lecturer_process = L(
                "大泽教授线上MTG前取消，讲师取消费 = 0 円",
                "大澤氏とのオンラインMTG前のキャンセルのため、講師キャンセル料 = 0 円"
            )
        else:
            cancel_lecturer = LECTURER_CANCEL_AFTER_MEETING
            cancel_lecturer_process = L(
                f"大泽教授线上MTG后由NSJ取消，需承担讲师费半额 = {yen(cancel_lecturer)}。"
                f"前金支付日为2020-12-31，但MTG完成日已经使取消义务发生，支付日只影响现金流。",
                f"大澤氏とのMTG後にNSJ側都合でキャンセルするため、講師料半額 = {yen(cancel_lecturer)}。"
                f"前金支払日は2020-12-31だが、MTG完了日にキャンセル時の支払義務が発生しており、支払日はキャッシュフローにのみ影響する。"
            )
    else:
        cancel_lecturer = None
        cancel_lecturer_process = None

    add_component(
        L("讲师费", "講師料"),
        normal_lecturer,
        normal_lecturer_process,
        cancel_lecturer,
        cancel_lecturer_process
    )

    # 3. 员工工资 / 社内従業員給与
    if include_staff_cost:
        normal_staff = STAFF_COST
        normal_staff_process = L(
            f"选择计算员工工资。不计算税费，只计算人工成本：{yen(STAFF_MONTHLY_SALARY)} ÷ {WORKING_DAYS_PER_MONTH}日 × {STAFF_MAN_DAYS}人日 = {yen(STAFF_COST)}",
            f"社内従業員給与を計算する設定。税金・追加手当は計算せず、人件費のみ計算：{yen(STAFF_MONTHLY_SALARY)} ÷ {WORKING_DAYS_PER_MONTH}日 × {STAFF_MAN_DAYS}人日 = {yen(STAFF_COST)}"
        )

        if cancel_date is not None:
            project_start = TIMING_A
            total_days = (EVENT_DATE - project_start).days
            used_days = max(0, (cancel_date - project_start).days)
            ratio = min(1, used_days / total_days)

            cancel_staff = STAFF_COST * ratio
            cancel_staff_process = L(
                f"取消时按准备进度估算人工成本：{yen(STAFF_COST)} × {ratio:.2f} = {yen(cancel_staff)}",
                f"キャンセル時点までの準備進捗で人件費を見積もる：{yen(STAFF_COST)} × {ratio:.2f} = {yen(cancel_staff)}"
            )
        else:
            cancel_staff = None
            cancel_staff_process = None
    else:
        normal_staff = 0
        normal_staff_process = L(
            "选择不计算员工工资，因此员工工资 = 0 円",
            "社内従業員給与を計算しない設定のため、社内従業員給与 = 0 円"
        )

        if cancel_date is not None:
            cancel_staff = 0
            cancel_staff_process = L(
                "选择不计算员工工资，因此取消时员工工资 = 0 円",
                "社内従業員給与を計算しない設定のため、キャンセル時の社内従業員給与 = 0 円"
            )
        else:
            cancel_staff = None
            cancel_staff_process = None

    add_component(
        L("员工工资", "社内従業員給与"),
        normal_staff,
        normal_staff_process,
        cancel_staff,
        cancel_staff_process
    )

    # 4. Web广告费 / Web広告費
    normal_web = WEB_AD_TOTAL
    normal_web_process = L(
        f"正常举办时，Web广告费 = {yen(WEB_AD_TOTAL)}",
        f"開催する場合、Web広告費 = {yen(WEB_AD_TOTAL)}"
    )

    if cancel_date is not None:
        if cancel_date < WEB_AD_CONTRACT:
            cancel_web = 0
            cancel_web_process = L(
                "广告契约前取消，Web广告费 = 0 円",
                "広告契約前のキャンセルのため、Web広告費 = 0 円"
            )
        elif cancel_date < WEB_AD_START:
            cancel_web = WEB_AD_ADVANCE
            cancel_web_process = L(
                f"广告契约后、广告开始前取消，只损失前金 = {yen(cancel_web)}",
                f"広告契約後・広告開始前のキャンセルのため、前金のみ = {yen(cancel_web)}"
            )
        else:
            cancel_web = WEB_AD_TOTAL
            cancel_web_process = L(
                f"广告已经开始，取消后仍需支付全额 = {yen(cancel_web)}",
                f"広告開始後のキャンセルのため、全額負担 = {yen(cancel_web)}"
            )
    else:
        cancel_web = None
        cancel_web_process = None

    add_component(
        L("Web广告费", "Web広告費"),
        normal_web,
        normal_web_process,
        cancel_web,
        cancel_web_process
    )

    # 5. 宣传册费用 / パンフレット費
    normal_pamphlet = PAMPHLET_PRINT_COST + PAMPHLET_SEND_COST
    normal_pamphlet_process = L(
        f"印刷费 {yen(PAMPHLET_PRINT_COST)} + 邮送费 {yen(PAMPHLET_SEND_COST)} = {yen(normal_pamphlet)}",
        f"印刷費 {yen(PAMPHLET_PRINT_COST)} + 発送費 {yen(PAMPHLET_SEND_COST)} = {yen(normal_pamphlet)}"
    )

    if cancel_date is not None:
        if cancel_date < PAMPHLET_PRINT_DATE:
            cancel_pamphlet = 0
            cancel_pamphlet_process = L(
                "宣传册印刷前取消，宣传册费用 = 0 円",
                "パンフレット印刷前のキャンセルのため、パンフレット費 = 0 円"
            )
        elif cancel_date < PAMPHLET_SEND_DATE:
            cancel_pamphlet = PAMPHLET_PRINT_COST
            cancel_pamphlet_process = L(
                f"已印刷但未邮送，只发生印刷费 = {yen(cancel_pamphlet)}",
                f"印刷後・発送前のため、印刷費のみ = {yen(cancel_pamphlet)}"
            )
        else:
            cancel_pamphlet = normal_pamphlet
            cancel_pamphlet_process = L(
                f"宣传册已邮送，印刷费+邮送费均无法回避 = {yen(cancel_pamphlet)}",
                f"パンフレット発送済みのため、印刷費＋発送費はいずれも回避不可 = {yen(cancel_pamphlet)}"
            )
    else:
        cancel_pamphlet = None
        cancel_pamphlet_process = None

    add_component(
        L("宣传册费用", "パンフレット費"),
        normal_pamphlet,
        normal_pamphlet_process,
        cancel_pamphlet,
        cancel_pamphlet_process
    )

    # 6. 教材・案例・名牌 / 教材・ケース・ネームプレート
    textbook_cost = TEXTBOOK_UNIT * (final_people + SPARE_COPIES)
    case_cost = CASE_UNIT * (final_people + SPARE_COPIES)
    nameplate_cost = NAMEPLATE_UNIT * final_people
    normal_material = textbook_cost + case_cost + nameplate_cost

    normal_material_process = L(
        f"教材 {TEXTBOOK_UNIT} × ({final_people}+备用{SPARE_COPIES}) = {yen(textbook_cost)}；"
        f"案例 {CASE_UNIT} × ({final_people}+备用{SPARE_COPIES}) = {yen(case_cost)}；"
        f"名牌 {NAMEPLATE_UNIT} × {final_people} = {yen(nameplate_cost)}；"
        f"合计 = {yen(normal_material)}",
        f"教材 {TEXTBOOK_UNIT} × ({final_people}+予備{SPARE_COPIES}) = {yen(textbook_cost)}；"
        f"ケース {CASE_UNIT} × ({final_people}+予備{SPARE_COPIES}) = {yen(case_cost)}；"
        f"ネームプレート {NAMEPLATE_UNIT} × {final_people} = {yen(nameplate_cost)}；"
        f"合計 = {yen(normal_material)}"
    )

    if cancel_date is not None:
        if cancel_date < PARTICIPANT_FIXED_DATE:
            cancel_material = 0
            cancel_material_process = L(
                "参加人数确定前取消，教材・案例・名牌尚未订购，费用 = 0 円",
                "受講生数確定前のキャンセルのため、教材・ケース・ネームプレートは未発注、費用 = 0 円"
            )
        else:
            cancel_material = normal_material
            cancel_material_process = L(
                f"参加人数已经确定，教材・案例・名牌费用发生 = {yen(cancel_material)}",
                f"受講生数確定後のため、教材・ケース・ネームプレート費が発生 = {yen(cancel_material)}"
            )
    else:
        cancel_material = None
        cancel_material_process = None

    add_component(
        L("教材・案例・名牌", "教材・ケース・ネームプレート"),
        normal_material,
        normal_material_process,
        cancel_material,
        cancel_material_process
    )

    # 7. 午餐费 / 昼食代
    lunch_count = final_people + 1 + 4
    normal_lunch = LUNCH_UNIT * lunch_count

    normal_lunch_process = L(
        f"{LUNCH_UNIT} × ({final_people}+讲师1+员工4) = {yen(normal_lunch)}",
        f"{LUNCH_UNIT} × ({final_people}+講師1+スタッフ4) = {yen(normal_lunch)}"
    )

    if cancel_date is not None:
        if cancel_date <= LUNCH_FREE_CANCEL_LIMIT:
            cancel_lunch = 0
            cancel_lunch_process = L(
                "举办3日前以前取消，午餐费 = 0 円",
                "開催3日前までのキャンセルのため、昼食代 = 0 円"
            )
        else:
            cancel_lunch = normal_lunch
            cancel_lunch_process = L(
                f"超过免费取消期限，午餐费发生 = {yen(cancel_lunch)}",
                f"無料キャンセル期限後のため、昼食代が発生 = {yen(cancel_lunch)}"
            )
    else:
        cancel_lunch = None
        cancel_lunch_process = None

    add_component(
        L("午餐费", "昼食代"),
        normal_lunch,
        normal_lunch_process,
        cancel_lunch,
        cancel_lunch_process
    )

    # 8. 咖啡服务 / コーヒーサービス
    normal_coffee, order_cups, normal_coffee_process = calculate_coffee_cost(selected_coffee_cups)

    if cancel_date is not None:
        if cancel_date <= COFFEE_FREE_CANCEL_LIMIT:
            cancel_coffee = 0
            cancel_coffee_process = L(
                "举办前日以前取消，咖啡服务费 = 0 円",
                "開催前日までのキャンセルのため、コーヒーサービス費 = 0 円"
            )
        else:
            cancel_coffee = normal_coffee
            cancel_coffee_process = L(
                f"超过免费取消期限，选择咖啡杯数为 {order_cups}杯，费用 = {yen(cancel_coffee)}",
                f"無料キャンセル期限後。選択したコーヒー杯数は {order_cups}杯、費用 = {yen(cancel_coffee)}"
            )
    else:
        cancel_coffee = None
        cancel_coffee_process = None

    add_component(
        L("咖啡服务", "コーヒーサービス"),
        normal_coffee,
        normal_coffee_process,
        cancel_coffee,
        cancel_coffee_process
    )

    normal_df = pd.DataFrame(normal_rows, columns=[ITEM, AMOUNT, PROCESS])

    if cancel_date is not None:
        cancel_df = pd.DataFrame(cancel_rows, columns=[ITEM, AMOUNT, PROCESS])
        avoidable_df = pd.DataFrame(avoidable_rows, columns=[ITEM, AMOUNT, PROCESS])
    else:
        cancel_df = pd.DataFrame(columns=[ITEM, AMOUNT, PROCESS])
        avoidable_df = pd.DataFrame(columns=[ITEM, AMOUNT, PROCESS])

    return normal_df, normal_total, cancel_df, cancel_total, avoidable_df, avoidable_total


# =========================================================
# 7. UI 输入区 / User Interface
# =========================================================

st.title(L(
    "NSJ研修会 利润・取消费用・回避可能原价模拟器",
    "NSJセミナー 利益・キャンセル費用・回避可能原価シミュレーション"
))

st.caption(L(
    "根据题目指定的四个时点，计算正常举办、取消时成本，以及回避可能原价。",
    "問題文で指定された4つのタイミングに基づき、開催時原価・キャンセル時原価・回避可能原価を計算します。"
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

    fee = st.slider(
        L("报名费（日元/人）", "受講料（円/人）"),
        min_value=25_000,
        max_value=80_000,
        value=60_000,
        step=1_000
    )

    selected_coffee_cups = st.select_slider(
        L("咖啡杯数", "コーヒー杯数"),
        options=list(range(0, 101, 10)),
        value=80
    )

    include_staff_choice = st.radio(
        L("是否计算员工工资？", "社内従業員給与を計算するか？"),
        [L("计算", "計算する"), L("不计算", "計算しない")],
        index=0
    )
    include_staff_cost = include_staff_choice == L("计算", "計算する")

    cancel_choice = st.radio(
        L("NSJ是否取消举办？", "NSJ側が開催をキャンセルするか？"),
        [L("不取消", "キャンセルしない"), L("取消", "キャンセルする")],
        index=0
    )

    nsj_cancel = cancel_choice == L("取消", "キャンセルする")

    timing_labels = {
        "a": L(
            "（a）半年前：2020-12-18；会场预约・大泽氏MTG・广告契约均已完成",
            "（a）半年前：2020-12-18；会場予約・大澤氏MTG・広告契約はすべて済み"
        ),
        "b": L(
            "（b）3个月前：2021-03-19；宣传册已邮送",
            "（b）3ヵ月前：2021-03-19；パンフレットは郵送済み"
        ),
        "c": L(
            "（c）1个月前：2021-05-21；会场费已全额支付",
            "（c）1ヵ月前：2021-05-21；会場費は全額支払い済み"
        ),
        "d": L(
            "（d）前日：2021-06-18",
            "（d）開催前日：2021-06-18"
        ),
        "custom": L(
            "自定义日期：2020年12月18日〜2021年6月19日",
            "日付を自由選択：2020年12月18日〜2021年6月19日"
        )
    }

    timing_dates = {
        "a": TIMING_A,
        "b": TIMING_B,
        "c": TIMING_C,
        "d": TIMING_D
    }

    if nsj_cancel:
        timing_choice = st.selectbox(
            L("取消时点", "キャンセル時点"),
            options=["a", "b", "c", "d", "custom"],
            format_func=lambda x: timing_labels[x],
            index=2
        )

        if timing_choice == "custom":
            cancel_date = st.date_input(
                L("NSJ取消日期", "NSJキャンセル日"),
                value=TIMING_A,
                min_value=TIMING_A,
                max_value=EVENT_DATE
            )
        else:
            cancel_date = timing_dates[timing_choice]
            st.write(L(f"选择的取消日期：{cancel_date}", f"選択されたキャンセル日：{cancel_date}"))
    else:
        cancel_date = None
        timing_choice = None

    # 如果取消日早于募集开始日，则募集期内学生取消人数固定为0
    if nsj_cancel and cancel_date < RECRUIT_START:
        student_cancel_people = 0
        st.info(L(
            "该取消时点早于募集开始日，因此募集期内取消报名人数固定为 0 人。",
            "このキャンセル時点は募集開始前のため、募集期間中の受講生側キャンセル人数は 0 人に固定されます。"
        ))
    else:
        student_cancel_people = st.slider(
            L("募集期内取消报名人数", "募集期間中の受講生側キャンセル人数"),
            min_value=0,
            max_value=registered_people,
            value=0,
            step=1
        )

    final_people = registered_people - student_cancel_people

    st.markdown("---")
    st.write(L(f"举办日：{EVENT_DATE}", f"開催日：{EVENT_DATE}"))
    st.write(L(f"报名人数：{registered_people} 人", f"申込人数：{registered_people} 人"))
    st.write(L(f"募集期内取消：{student_cancel_people} 人", f"募集期間中キャンセル：{student_cancel_people} 人"))
    st.write(L(f"实际参加人数：{final_people} 人", f"実際受講者数：{final_people} 人"))
    st.write(L(f"咖啡杯数：{selected_coffee_cups} 杯", f"コーヒー杯数：{selected_coffee_cups} 杯"))
    st.write(L(
        f"员工工资：{'计算' if include_staff_cost else '不计算'}",
        f"社内従業員給与：{'計算する' if include_staff_cost else '計算しない'}"
    ))


# =========================================================
# 8. 计算 / Calculation
# =========================================================

holding_revenue, holding_tuition_revenue, penalty_revenue, holding_revenue_process = calculate_revenue(
    registered_people,
    student_cancel_people,
    final_people,
    fee,
    nsj_cancel=False
)

cancel_revenue, cancel_tuition_revenue, cancel_penalty_revenue, cancel_revenue_process = calculate_revenue(
    registered_people,
    student_cancel_people,
    final_people,
    fee,
    nsj_cancel=True
)

normal_df, normal_total, cancel_df, cancel_total, avoidable_df, avoidable_total = calculate_component_rows(
    final_people,
    selected_coffee_cups,
    include_staff_cost,
    cancel_date=cancel_date if nsj_cancel else None
)

holding_profit = holding_revenue - normal_total

if nsj_cancel:
    cancel_result = cancel_revenue - cancel_total
else:
    cancel_result = None


# =========================================================
# 9. 结果卡片 / Result Cards
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(L("正常举办收入", "開催時収入"), yen(holding_revenue))
col2.metric(L("正常举办总成本", "開催時総原価"), yen(normal_total))
col3.metric(L("正常举办利润/亏损", "開催時利益・損失"), yen(holding_profit))

if nsj_cancel:
    col4.metric(L("回避可能原价合计", "回避可能原価合計"), yen(avoidable_total))
else:
    col4.metric(L("取消状态", "キャンセル状態"), L("不取消", "なし"))

st.info(L("正常举办时收入计算：", "開催時の収入計算：") + "\n" + holding_revenue_process)

if nsj_cancel:
    st.warning(L("取消时收入计算：", "キャンセル時の収入計算：") + "\n" + cancel_revenue_process)

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
    st.info(L(
        f"取消时净结果 = 取消时收入 {yen(cancel_revenue)} - 取消后仍需承担成本 {yen(cancel_total)} = {yen(cancel_result)}",
        f"キャンセル時純損益 = キャンセル時収入 {yen(cancel_revenue)} - キャンセル後も負担する原価 {yen(cancel_total)} = {yen(cancel_result)}"
    ))


# =========================================================
# 10. 图表 / Charts
# =========================================================

st.subheader(L("一、正常举办 vs 取消 vs 回避可能原价", "一、開催 vs キャンセル vs 回避可能原価"))

if nsj_cancel:
    summary_df = pd.DataFrame({
        ITEM: [
            L("正常举办收入", "開催時収入"),
            L("正常举办总成本", "開催時総原価"),
            L("正常举办利润/亏损", "開催時利益・損失"),
            L("取消后仍需承担成本", "キャンセル後も負担する原価"),
            L("回避可能原价", "回避可能原価"),
            L("取消时净结果", "キャンセル時純損益")
        ],
        AMOUNT: [
            holding_revenue,
            normal_total,
            holding_profit,
            cancel_total,
            avoidable_total,
            cancel_result
        ]
    })
else:
    summary_df = pd.DataFrame({
        ITEM: [
            L("正常举办收入", "開催時収入"),
            L("正常举办总成本", "開催時総原価"),
            L("正常举办利润/亏损", "開催時利益・損失")
        ],
        AMOUNT: [
            holding_revenue,
            normal_total,
            holding_profit
        ]
    })

st.bar_chart(summary_df.set_index(ITEM))


st.subheader(L("二、正常举办成本构成", "二、開催時の原価構成"))
st.bar_chart(normal_df.set_index(ITEM)[AMOUNT])
st.dataframe(normal_df, use_container_width=True)


if nsj_cancel:
    st.subheader(L("三、取消后仍需承担的成本", "三、キャンセル後も負担する原価"))
    st.bar_chart(cancel_df.set_index(ITEM)[AMOUNT])
    st.dataframe(cancel_df, use_container_width=True)

    st.subheader(L("四、回避可能原价", "四、回避可能原価"))
    if len(avoidable_df) > 0:
        st.bar_chart(avoidable_df.set_index(ITEM)[AMOUNT])
        st.dataframe(avoidable_df, use_container_width=True)
    else:
        st.write(L(
            "该时点没有可回避原价。",
            "この時点では回避可能原価はありません。"
        ))
else:
    st.subheader(L("三、取消费用与回避可能原价", "三、キャンセル費用と回避可能原価"))
    st.write(L(
        "当前选择：不取消。因此不计算取消后仍需承担的成本和回避可能原价。",
        "現在の選択：キャンセルしない。したがって、キャンセル後も負担する原価と回避可能原価は計算しません。"
    ))


# =========================================================
# 11. 具体计算过程 / Detailed Calculation
# =========================================================

st.subheader(L("五、具体计算过程", "五、具体的な計算過程"))

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
    st.write(L(
        f"咖啡杯数 = {selected_coffee_cups} 杯",
        f"コーヒー杯数 = {selected_coffee_cups} 杯"
    ))
    st.write(holding_revenue_process)

    for _, row in normal_df.iterrows():
        st.write(f"・{row[ITEM]}：{row[PROCESS]}")

    st.write(L(
        f"正常举办总成本 = {yen(normal_total)}",
        f"開催時総原価 = {yen(normal_total)}"
    ))
    st.write(L(
        f"正常举办利润/亏损 = 正常举办收入 - 正常举办总成本 = {yen(holding_revenue)} - {yen(normal_total)} = {yen(holding_profit)}",
        f"開催時利益・損失 = 開催時収入 - 開催時総原価 = {yen(holding_revenue)} - {yen(normal_total)} = {yen(holding_profit)}"
    ))

if nsj_cancel:
    with st.expander(L("查看取消时的计算过程", "キャンセル時の計算過程を見る")):
        st.write(L(f"NSJ取消日期：{cancel_date}", f"NSJキャンセル日：{cancel_date}"))
        st.write(cancel_revenue_process)

        for _, row in cancel_df.iterrows():
            st.write(f"・{row[ITEM]}：{row[PROCESS]}")

        st.write(L(
            f"取消后仍需承担的成本合计 = {yen(cancel_total)}",
            f"キャンセル後も負担する原価合計 = {yen(cancel_total)}"
        ))
        st.write(L(
            f"取消时净结果 = 取消时收入 - 取消后仍需承担成本 = {yen(cancel_revenue)} - {yen(cancel_total)} = {yen(cancel_result)}",
            f"キャンセル時純損益 = キャンセル時収入 - キャンセル後も負担する原価 = {yen(cancel_revenue)} - {yen(cancel_total)} = {yen(cancel_result)}"
        ))

    with st.expander(L("查看回避可能原价的计算过程", "回避可能原価の計算過程を見る")):
        if len(avoidable_df) > 0:
            for _, row in avoidable_df.iterrows():
                st.write(f"・{row[ITEM]}：{row[PROCESS]}")
            st.write(L(
                f"回避可能原价合计 = {yen(avoidable_total)}",
                f"回避可能原価合計 = {yen(avoidable_total)}"
            ))
        else:
            st.write(L(
                "该时点没有可回避原价。",
                "この時点では回避可能原価はありません。"
            ))

with st.expander(L("查看不亏损条件", "損益分岐条件を見る")):
    if final_people > 0:
        break_even_fee = math.ceil(normal_total / final_people)
        st.write(L(
            f"不亏损最低报名费 = 正常举办总成本 ÷ 实际参加人数 = {yen(normal_total)} ÷ {final_people} = {yen(break_even_fee)} / 人",
            f"損益分岐受講料 = 開催時総原価 ÷ 実際受講者数 = {yen(normal_total)} ÷ {final_people} = {yen(break_even_fee)} / 人"
        ))

    break_even_people = math.ceil(normal_total / fee)
    st.write(L(
        f"在报名费为 {yen(fee)} 的情况下，不亏损最低人数 = {break_even_people} 人",
        f"受講料が {yen(fee)} の場合、損益分岐人数 = {break_even_people} 人"
    ))


# =========================================================
# 12. 重要日期 / Important Dates
# =========================================================

st.subheader(L("六、重要日期", "六、重要日程"))

date_df = pd.DataFrame({
    L("日期", "日付"): [
        TIMING_A,
        LECTURER_ADVANCE_PAYMENT_DATE,
        WEB_AD_START,
        PAMPHLET_PRINT_DATE,
        TIMING_B,
        RECRUIT_START,
        RECRUIT_END,
        TIMING_C,
        LUNCH_FREE_CANCEL_LIMIT,
        TIMING_D,
        EVENT_DATE
    ],
    L("含义", "意味"): [
        L("题目（a）：半年前；会场预约、大泽氏MTG、广告契约均已完成", "問題（a）：半年前；会場予約・大澤氏MTG・広告契約はすべて済み"),
        L("大泽教授前金支付日；只影响现金流，不改变回避可能原价判断", "大澤氏への前金支払日；キャッシュフローにのみ影響し、回避可能原価の判断は変えない"),
        L("Web广告开始", "Web広告開始"),
        L("宣传册印刷完成", "パンフレット印刷完了"),
        L("题目（b）：3个月前；宣传册已邮送", "問題（b）：3ヵ月前；パンフレットは郵送済み"),
        L("募集开始", "募集開始"),
        L("募集结束", "募集終了"),
        L("题目（c）：1个月前；会场费已全额支付、参加人数确定", "問題（c）：1ヵ月前；会場費は全額支払い済み・受講生数確定"),
        L("午餐免费取消期限", "昼食無料キャンセル期限"),
        L("题目（d）：举办前日；咖啡仍可免费取消", "問題（d）：開催前日；コーヒーはまだ無料キャンセル可能"),
        L("举办日", "開催日")
    ]
})

st.dataframe(date_df, use_container_width=True)
