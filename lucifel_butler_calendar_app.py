import streamlit as st
import matplotlib.pyplot as plt
import calendar
from collections import defaultdict
from matplotlib import patches
import time
from matplotlib import rcParams
import uuid

rcParams['font.family'] = ['Times New Roman', 'Malgun Gothic']

# --- 이름 사전 ---
name_dict_grouped = {
    "Bestia": {
        "쿠로": "Kuro", "레오": "Leo", "아이작": "Isaac", "하쿠": "Haku",
        "발렌타인": "Valen", "닉": "Nick", "샤오루": "Xiaolu", "카게": "Kage", "카프카": "Kafka"
    },
    "Inferis": {
        "카이엘": "Kaiel", "루시": "Lucy", "데이": "Dei", "워커": "Walker",
        "레이": "Ray", "케로": "Kero", "렌": "Ren", "라무": "Ramu"
    },
    "Pax": {
        "로쿠": "Roku", "유키": "Yuki", "제로": "Zero", "미호": "Miho",
        "호리": "Hori", "쥬노": "Zeuno", "제리": "Jerry"
    }
}

# --- 세션 상태 초기화 ---
if "entries" not in st.session_state:
    st.session_state.entries = []

st.markdown("#### 루치펠 집사카페 캘린더 입력 시스템")



st.markdown("""######  
0. 제가 쓰려고 만든거라 오류가 있을 수 있습니다. (가끔 업데이트 예정) 마음대로 가져다 쓰세요.
1. 상단에서 연도와 월을 선택합니다.  
2. 근무자의 **원 근무지**, **이름**, **근무일**, **해당일 근무지**를 입력합니다. (중복 입력도 1번 반영)
3. 아래 **[입력 추가]** 버튼을 눌러 일정을 등록합니다. 원하시는 집사님들 한번에 출력 가능하니 모두 추가해주세요! 파견 시 이름이 파란글씨로 표기됩니다.
4. 모든 등록이 끝나면 **[📅 캘린더 출력]** 버튼으로 결과를 확인하고 다운로드할 수 있습니다.
""")

st.markdown("### 📘 어플 설명 슬라이드")

slide_images = {
    "슬라이드 1": "슬라이드1.PNG",
    "슬라이드 2": "슬라이드2.PNG",
    "슬라이드 3": "슬라이드3.PNG"
}

slide_keys = list(slide_images.keys())
selected_slide = st.select_slider("← 설명을 좌우로 넘겨보세요 →", options=slide_keys)

st.image(slide_images[selected_slide], use_container_width=True)

# --- 연도 및 월 선택: 최상단 ---
year = st.selectbox("연도 선택", list(range(2023, 2031)), index=2)
month = st.selectbox("월 선택", list(range(1, 13)), index=5)


# --- 입력 인터페이스 ---
site = st.selectbox("원 근무지", ["Bestia", "Inferis", "Pax"])
name = st.selectbox("이름", list(name_dict_grouped[site].keys()))
days_options = list(range(1, 32))
if name == "워커":
    days_options.append("💖")
selected_days = st.multiselect("근무일 선택", days_options)
deploy = st.selectbox("해당일 근무지", ["Bestia", "Inferis", "Pax"])

st.markdown("---")

# --- 입력 추가 버튼 (입력된 일정 위) ---
if not selected_days:
    st.warning("⚠️ 근무일을 선택해야 입력이 가능합니다.")
elif st.button("입력 추가"):
    if name == "워커" and "💖" in selected_days:
        st.toast("💖 워커 집사님 왕왕사랑해요 💖")
    else:
        try:
            days = [int(d) for d in selected_days if isinstance(d, int)]
            st.session_state.entries.append((site, name, days, deploy))
            st.toast(f"✅ 추가됨: ({site}, {name}, {days}, {deploy})", icon="✅")
        except:
            st.error("❌ 근무일은 숫자여야 합니다.")

# 삭제 예약용 키 초기화
if "to_delete" not in st.session_state:
    st.session_state.to_delete = None


# 일정 출력 및 삭제 버튼
if st.session_state.entries:
    st.markdown("#### 현재 입력된 일정")
    for i, (s, n, d, t) in enumerate(st.session_state.entries):
        col1, col2 = st.columns([8, 1])
        with col1:
            st.markdown(f"{n} ({d}) **{t}** 근무")
        with col2:

            if st.button("일정 삭제", key=f"del_{i}"):
                st.session_state.to_delete = i
                st.session_state["__force_rerender__"] = str(uuid.uuid4())  # 상태 변경 유도

if st.session_state.to_delete is not None:
    idx = st.session_state.to_delete
    if 0 <= idx < len(st.session_state.entries):
        deleted_entry = st.session_state.entries[idx]
        del st.session_state.entries[idx]
        st.toast(f"🗑️ 삭제됨(잠시 후 자동 반영, 버튼 다시 안 눌러도 됩니다.): {deleted_entry[1]} ({deleted_entry[2]})", icon="🗑️")
    st.session_state.to_delete = None

# --- 캘린더 그리기 함수 ---
def draw_calendar(year, month, site_name, entries):
    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)
    cal_data = defaultdict(list)

    name_dict = {}
    for group in name_dict_grouped.values():
        name_dict.update(group)

    for orig, n, days, target in entries:
        if target != site_name:
            continue
        label = f"{name_dict.get(n, n)}"
        for d in set(days):  # 날짜 중복 제거
            # 같은 날, 같은 이름이 이미 등록되어 있으면 추가하지 않음
            if all(existing_label != label for existing_label, _ in cal_data[d]):
                cal_data[d].append((label, orig != target))

    row_heights = []
    for week in weeks:
        max_h = max((len(cal_data.get(d, [])) for d in week if d != 0), default=1)
        row_heights.append(max(1, max_h / 3.5))

    total_height = sum(row_heights)
    fig, ax = plt.subplots(figsize=(7, total_height + 1.3))
    ax.set_xlim(0, 7)
    ax.set_ylim(0, total_height + 1.1)
    ax.axis("off")

    bg_colors = {"Pax": "#fff9cc", "Inferis": "#e6f0ff", "Bestia": "#ffe6f0"}
    fig.patch.set_facecolor(bg_colors.get(site_name, "#ffffff"))
    ax.set_facecolor(bg_colors.get(site_name, "#ffffff"))

    ax.text(3.5, total_height + 0.35, f"{site_name} : {year} / {month:02d}",
            ha="center", va="bottom", fontsize=25, weight="bold")

    for i, wd in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
        ax.text(i + 0.5, total_height + 0.05, wd, ha="center", va="bottom", fontsize=11, weight="bold")

    y_base = total_height
    for row, week in enumerate(weeks):
        row_height = row_heights[row]
        for col, day in enumerate(week):
            if day == 0: continue
            entries_today = cal_data.get(day, [])
            rect = patches.FancyBboxPatch(
                (col + 0.05, y_base - row_height + 0.05), 0.9, row_height - 0.1,
                boxstyle="round,pad=0.02", linewidth=1, edgecolor='gray', facecolor='white'
            )
            ax.add_patch(rect)

            is_weekend = col == 0 or col == 6
            ax.text(col + 0.08, y_base - 0.12, f"{day}", ha="left", va="top", fontsize=8,
                    weight="bold", color="red" if is_weekend else "black")
            ax.plot([col + 0.08, col + 0.9], [y_base - 0.25, y_base - 0.25], color="black", linewidth=0.5)

            for i, (label, is_dispatched) in enumerate(entries_today):
                ax.text(col + 0.08, y_base - 0.35 - i * 0.13, label, ha="left", va="top",
                        fontsize=9, color="blue" if is_dispatched else "black")
        y_base -= row_height

    img_file = f"{site_name}_{month:02d}.png"
    plt.savefig(img_file, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    return img_file

st.markdown("###### 각 캘린더 다운로드 후 화면에서 이미지들이 사라지는데 다시 캘린더 출력 누르시면 재생성 됩니다.")
# --- 출력 버튼 및 다운로드 ---
if st.button("📅 캘린더 출력"):
    if not st.session_state.entries:
        st.warning("⚠️ 먼저 '입력 추가' 버튼을 눌러 일정을 등록해주세요.")
    else:
        for target_site in ["Pax", "Inferis", "Bestia"]:
            img_file = draw_calendar(year, month, target_site, st.session_state.entries)
            st.image(img_file, caption=f"{target_site} 근무 캘린더")
            with open(img_file, "rb") as f:
                st.download_button(
                    label=f"📥 {target_site} 다운로드",
                    data=f.read(),
                    file_name=img_file,
                    mime="image/png"
                )
