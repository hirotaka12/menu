import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta

WEEKDAYS = ["日", "月", "火", "水", "木", "金", "土"]

if "weekly_memo" not in st.session_state:
    st.session_state.weekly_memo = {}
if "selected_date" not in st.session_state:
    today = datetime.today()
    st.session_state.selected_date = today - timedelta(days=(today.weekday() + 1) % 7)

def get_week_dates(start_date):
    start_date -= timedelta(days=(start_date.weekday() + 1) % 7)
    return [start_date + timedelta(days=i) for i in range(7)]

def format_with_bullet(text):
    lines = text.strip().split("\n")
    return "\n".join([f"・{line.strip()}" for line in lines if line.strip()])

st.set_page_config(page_title="献立アプリ", layout="centered")
st.title("📋 献立＆買い物リスト（週間）")

new_date = st.date_input("週の日付を選んでください", st.session_state.selected_date, key="calendar_input")
selected_sunday = new_date - timedelta(days=(new_date.weekday() + 1) % 7)
if selected_sunday != st.session_state.selected_date:
    st.session_state.selected_date = selected_sunday
    st.rerun()

week_dates = get_week_dates(st.session_state.selected_date)

selected_strs = [f"{d.month}/{d.day}({WEEKDAYS[d.isoweekday() % 7]})" for d in week_dates]
selected_label = st.radio("日付を選択", selected_strs, horizontal=True)
selected_index = selected_strs.index(selected_label)
selected_date = week_dates[selected_index]
selected_str = selected_date.strftime("%Y-%m-%d")

if "last_selected" not in st.session_state or st.session_state.last_selected != selected_str:
    st.session_state.menu_input = ""
    st.session_state.shopping_input = ""
    st.session_state.last_selected = selected_str
    if selected_str in st.session_state.weekly_memo:
        st.session_state.menu_input = st.session_state.weekly_memo[selected_str].get("menu", "")
        st.session_state.shopping_input = st.session_state.weekly_memo[selected_str].get("shopping", "")

menu_input = st.text_area("🍽 献立を入力（改行可）", value=st.session_state.menu_input, key="menu_input", height=150)
shopping_input = st.text_area("🛍 買い物リストを入力（改行可）", value=st.session_state.shopping_input, key="shopping_input", height=150)

if st.button("💾 保存"):
    menu_text = format_with_bullet(menu_input)
    shopping_text = format_with_bullet(shopping_input)
    st.session_state.weekly_memo[selected_str] = {
        "menu": menu_text,
        "shopping": shopping_text
    }
    st.success(f"{selected_str} の内容を保存しました。")
    st.rerun()

# サイドバー
with st.sidebar:
    st.subheader("📅 今週の献立（閲覧）")
    menu_output = ""
    for d in week_dates:
        date_str = d.strftime("%Y-%m-%d")
        label = f"{d.month}/{d.day}({WEEKDAYS[d.weekday()]})"
        menu = st.session_state.weekly_memo.get(date_str, {}).get("menu", "")
        if menu:
            formatted = menu.replace("\n", "<br>")
            st.markdown(f"**{label}：**<br>{formatted}", unsafe_allow_html=True)
            menu_output += f"{label}\n{menu}\n\n"
        else:
            st.markdown(f"**{label}：** （未入力）")

    st.subheader("🛒 今週の買い物リスト")
    shopping_items = {}
    for d in week_dates:
        date_str = d.strftime("%Y-%m-%d")
        shopping = st.session_state.weekly_memo.get(date_str, {}).get("shopping", "")
        for line in shopping.split("\n"):
            line = line.strip().lstrip("・")
            if line:
                shopping_items.setdefault(line, []).append(date_str)

    shopping_output = ""
    for item, days in shopping_items.items():
        label = f"{item}"
        if len(days) > 1:
            label += " 🔁"
        st.checkbox(label, key=f"check_{item}")
        shopping_output += f"{item}\n"

    # 📋 コピー用ボタン（献立）
    components.html(f"""
        <button onclick="navigator.clipboard.writeText({repr(menu_output)})
                         .then(() => alert('献立をコピーしました'))"
                style="margin:10px 0;padding:10px 20px;font-size:16px;
                       border:none;background-color:#4CAF50;color:white;
                       border-radius:6px;cursor:pointer;width:100%;">
            📋 今週の献立をコピー
        </button>
    """, height=70)

    # 📋 コピー用ボタン（買い物リスト）
    components.html(f"""
        <button onclick="navigator.clipboard.writeText({repr(shopping_output)})
                         .then(() => alert('買い物リストをコピーしました'))"
                style="margin:10px 0;padding:10px 20px;font-size:16px;
                       border:none;background-color:#2196F3;color:white;
                       border-radius:6px;cursor:pointer;width:100%;">
            📋 買い物リストをコピー
        </button>
    """, height=70)
