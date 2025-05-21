import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import io
import base64
import time
import shutil
import uuid

# --- Matplotlib Font Setup ---
@st.cache_resource
def setup_font():
    try:
        shutil.rmtree(matplotlib.get_cachedir(), ignore_errors=True)
    except Exception:
        pass
    try:
        fm._fontManager = fm.FontManager() 
    except Exception:
        st.warning("폰트 매니저를 새로고침하는 중 오류가 발생했어요. 기본 폰트로 진행할게요!")

    font_name_to_set = None
    korean_fonts_priority = ["NanumSquareRound", "NanumGothic", "Malgun Gothic", "AppleSDGothicNeo"]
    available_font_names = [f.name for f in fm.fontManager.ttflist]

    for font in korean_fonts_priority:
        if font in available_font_names:
            font_name_to_set = font
            break
    if not font_name_to_set:
        for font_info in fm.fontManager.ttflist:
            if any(kor_font.lower() in font_info.name.lower() for kor_font in korean_fonts_priority):
                font_name_to_set = font_info.name
                break
    
    if font_name_to_set:
        try:
            plt.rcParams['font.family'] = font_name_to_set
            plt.rcParams['axes.unicode_minus'] = False
        except Exception: 
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['axes.unicode_minus'] = False
    else: 
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False
    
    sns.set_theme(style="whitegrid", rc={"font.family": plt.rcParams.get('font.family', 'sans-serif'), "axes.unicode_minus": False})

setup_font()

# --- Helper Functions ---
def get_color_palette(n):
    base_colors = ['#FF9AA2', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7', '#C7CEEA', '#B5B9FF', '#ADE8F4']
    return (base_colors * (n // len(base_colors) + 1))[:n]

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    # plt.close(fig) # 다이얼로그에서 재생성하므로, 여기서는 닫지 않거나, 상황에 따라 조절
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

def download_button_component(label, data, file_name, mime, key_suffix):
    st.download_button(
        label=label,
        data=data,
        file_name=file_name,
        mime=mime,
        key=f"download_btn_{key_suffix}",
        use_container_width=True 
    )

def explanation_box_st(html_content):
    st.markdown(f"""
    <div style="
        max-width:700px; margin:12px auto 18px auto;
        background: #f5f6fa; border-radius: 18px;
        border: 1.5px solid #e2e2e2;
        box-shadow:0 1.5px 8px #eee;
        padding:20px 18px 12px 18px;
        text-align:center; 
        font-size:1.0em;
        line-height:1.7;
        color:#444;">
        {html_content} 
    </div> 
    """, unsafe_allow_html=True)

def display_html_message(message_text, type="success", icon_char_override=None, duration_sec=1.5, is_persistent=False):
    default_icons = {"success": "✨", "warning_red_text": "⚠️", "info": "ℹ️", "error": "🔥"}
    icon_char = icon_char_override if icon_char_override is not None else default_icons.get(type, "")

    if type == "success":
        bg_color, text_color, border_color = '#d4edda', '#155724', '#c3e6cb'
        text_align_style, white_space_style, min_width_style, padding_style = "center", "nowrap", "fit-content", "10px 20px"
    elif type == "warning_red_text": 
        bg_color, border_color, text_color = 'transparent', 'transparent', '#D32F2F'
        text_align_style, white_space_style, min_width_style, padding_style = "center", "normal", "auto", "5px"
    elif type == "info":
        bg_color, text_color, border_color = '#d1ecf1', '#0c5460', '#bee5eb'
        text_align_style, white_space_style, min_width_style, padding_style = "center", "normal", "300px", "10px 15px"
    else: 
        bg_color, text_color, border_color = '#f8d7da', '#721c24', '#f5c6cb'
        text_align_style, white_space_style, min_width_style, padding_style = "center", "normal", "300px", "10px 15px"

    message_html = f"""
    <div style="
        display: flex; justify-content: center; align-items: center;
        padding: {padding_style}; margin: 10px auto; border-radius: 5px;
        background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color};
        width: {min_width_style if type == 'success' else 'fit-content'};
        min-width: {min_width_style if type != 'success' else 'auto'};
        max-width: 90%; white-space: {white_space_style};
        word-wrap: break-word; text-align: {text_align_style};">
        <span style="font-size: 1.1em; margin-right: 8px;">{icon_char}</span>
        <span style="font-size: 1.0em;">{message_text}</span>
    </div>"""
    
    if is_persistent or duration_sec == 0: # duration_sec 0이면 메시지 유지
        st.markdown(message_html, unsafe_allow_html=True)
    else:
        message_placeholder = st.empty()
        message_placeholder.markdown(message_html, unsafe_allow_html=True)
        time.sleep(duration_sec)
        message_placeholder.empty()

# --- State Initialization ---
if 'keywords_data' not in st.session_state:
    st.session_state.keywords_data = pd.DataFrame(columns=['키워드', '데이터가용성점수', '유레카지수', '덕질가능지수', '성장잠재력지수'])
if 'site_configs' not in st.session_state:
    st.session_state.site_configs = [
        {'id': str(uuid.uuid4()), 'name': 'DBpia', 'weight': 2.0, 'is_default': True, 'user_count': 0},
        {'id': str(uuid.uuid4()), 'name': 'BIGKINDS', 'weight': 1.0, 'is_default': True, 'user_count': 0},
        {'id': str(uuid.uuid4()), 'name': '교보문고', 'weight': 1.0, 'is_default': True, 'user_count': 0},
    ]
else: 
    for i in range(len(st.session_state.site_configs)):
        if 'id' not in st.session_state.site_configs[i]: st.session_state.site_configs[i]['id'] = str(uuid.uuid4())
        if 'user_count' not in st.session_state.site_configs[i]: st.session_state.site_configs[i]['user_count'] = 0
        if 'is_default' not in st.session_state.site_configs[i]: st.session_state.site_configs[i]['is_default'] = False

if 'keyword_input_val' not in st.session_state: st.session_state.keyword_input_val = ""
if 'eureka_slider_val' not in st.session_state: st.session_state.eureka_slider_val = 2
if 'fan_slider_val' not in st.session_state: st.session_state.fan_slider_val = 2
if 'potential_slider_val' not in st.session_state: st.session_state.potential_slider_val = 2
if 'data_availability_score_result' not in st.session_state: st.session_state.data_availability_score_result = None
if 'show_graph_section' not in st.session_state: st.session_state.show_graph_section = False
if 'show_large_graph_dialog' not in st.session_state: st.session_state.show_large_graph_dialog = False # 크게 보기 다이얼로그 상태

# --- Core Logic Functions ---
def calculate_data_availability_score_from_configs():
    site_contributions = []
    raw_counts_summary = {}
    for site_config in st.session_state.site_configs:
        count = int(site_config.get('user_count', 0))
        weight = float(site_config.get('weight', 1.0))
        raw_counts_summary[site_config['name']] = {'count': count, 'weight': weight}
        if count > 0:
             site_contributions.append({'name': site_config['name'], 'contribution': count * weight, 'raw_count': count, 'weight': weight})
    sorted_sites = sorted(site_contributions, key=lambda x: x['contribution'], reverse=True)
    top_sites_for_score = sorted_sites[:3]
    weighted_sum = sum(s['contribution'] for s in top_sites_for_score)
    score = 1
    if weighted_sum >= 500: score = 4
    elif weighted_sum >= 200: score = 3
    elif weighted_sum >= 50: score = 2
    return score, weighted_sum, raw_counts_summary, top_sites_for_score

def reset_inputs():
    st.session_state.keyword_input_val = ""
    for i in range(len(st.session_state.site_configs)):
        st.session_state.site_configs[i]['user_count'] = 0
    st.session_state.eureka_slider_val = 2
    st.session_state.fan_slider_val = 2
    st.session_state.potential_slider_val = 2
    st.session_state.data_availability_score_result = None

# --- Graph Generation Function ---
def generate_scatter_plot(df_data, y_col_name, title_suffix_text, fig_size=(17, 14), font_sizes_config=None):
    # font_sizes_config: {'title': 28, 'label': 25, 'tick': 20, 'quad_text': 20, 'annotate': 20}
    if font_sizes_config is None: 
        font_sizes_config = {'title': 28, 'label': 25, 'tick': 20, 'quad_text': 20, 'annotate': 20}

    fig, ax = plt.subplots(figsize=fig_size)
    
    plot_df = df_data.copy()
    base_jitter = 0.05 
    plot_df['x_jittered'] = plot_df['데이터가용성점수'].astype(float) + np.random.uniform(-base_jitter, base_jitter, size=len(plot_df))
    plot_df['y_jittered'] = plot_df[y_col_name].astype(float) + np.random.uniform(-base_jitter, base_jitter, size=len(plot_df))

    colors = get_color_palette(len(plot_df))
    sns.scatterplot(x='x_jittered', y='y_jittered', data=plot_df, s=250 * (fig_size[0]/17), 
                    hue='키워드', palette=colors, legend=False, ax=ax, alpha=0.8)

    ax.axhline(y=2.5, color='gray', linestyle='--', alpha=0.7)
    ax.axvline(x=2.5, color='gray', linestyle='--', alpha=0.7)
    
    quad_fills = {"top_left": ([0.5, 2.5], 2.5, 4.5, 'gold', 0.05), "top_right": ([2.5, 4.5], 2.5, 4.5, 'limegreen', 0.05), 
                  "bottom_left": ([0.5, 2.5], 0.5, 2.5, 'tomato', 0.05), "bottom_right": ([2.5, 4.5], 0.5, 2.5, 'dodgerblue', 0.05)}
    for x_r, y_b, y_t, c_f, a_f in quad_fills.values(): ax.fill_between(x_r, y_b, y_t, alpha=a_f, color=c_f)

    quad_texts_data = [ # 이모티콘 제거
        (1.5, 3.5, "도전적인 보석\n(자료 부족, 높은 가치)", '#b28900'), 
        (3.5, 3.5, "최고의 보석\n(자료 풍부, 높은 가치)", '#2a7d2a'), 
        (1.5, 1.5, "재고려 필요\n(자료 부족, 낮은 가치)", '#c33'), 
        (3.5, 1.5, "안정적 선택\n(자료 풍부, 낮은 가치)", '#177a8c')
    ]
    for x_txt, y_txt, lbl_txt, clr_txt in quad_texts_data: 
        ax.text(x_txt, y_txt, lbl_txt, ha='center', va='center', fontsize=font_sizes_config['quad_text'], color=clr_txt, wrap=True, linespacing=1.5)

    for _, row in plot_df.iterrows(): 
        ax.annotate(row['키워드'], (row['x_jittered'], row['y_jittered']), 
                    xytext=(0, 15 * (fig_size[0]/17)), textcoords='offset points', 
                    fontsize=font_sizes_config['annotate'], fontweight='bold', ha='center',
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.6))

    ax.set_title(f'키워드 평가 맵: 데이터 가용성 vs {title_suffix_text}', fontsize=font_sizes_config['title'], pad=30 * (fig_size[0]/17), weight='bold')
    ax.set_xlabel('데이터 가용성 점수', fontsize=font_sizes_config['label'], labelpad=25 * (fig_size[0]/17))
    ax.set_ylabel(title_suffix_text, fontsize=font_sizes_config['label'], labelpad=25 * (fig_size[0]/17))
    ax.set_xlim(0.5, 4.5); ax.set_ylim(0.5, 4.5)
    ax.set_xticks([1, 2, 3, 4]); ax.set_yticks([1, 2, 3, 4])
    ax.tick_params(axis='both', which='major', labelsize=font_sizes_config['tick'])
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout(pad=1.5 * (fig_size[0]/17)) # pad 값도 그래프 크기에 비례하도록 조정
    return fig # fig 객체 반환


# --- UI Rendering ---
st.markdown("""
    <div style="background: linear-gradient(90deg, #fccb90 0%, #d57eeb 100%);
                padding: 20px; border-radius: 15px; margin: 10px auto 25px auto; text-align: center; max-width: 100%;">
        <h1 style="color: white; text-shadow: 2px 2px 4px #000000; margin-bottom: 5px; font-size: 2.2em; word-wrap: break-word;">✨ 나만의 보석 키워드 발굴 시스템 ✨</h1>
        <h3 style="color: white; font-size: 1.3em; margin-top:0;">당신의 특별한 연구 주제, 제가 찾아드릴게요! 💎</h3>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ 검색 사이트 설정")
    st.caption("여기서 검색할 사이트와 가중치를 마음대로 바꿀 수 있어요!")
    with st.expander("➕ 새 사이트 추가하기", expanded=False):
        with st.form("new_site_form"):
            new_site_name = st.text_input("새 사이트 이름")
            new_site_weight = st.number_input("새 사이트 가중치", min_value=0.1, value=1.0, step=0.1)
            submitted_new_site = st.form_submit_button("추가")
            if submitted_new_site:
                if new_site_name.strip():
                    if any(site['name'].lower() == new_site_name.strip().lower() for site in st.session_state.site_configs):
                        st.warning(f"'{new_site_name}' 사이트는 이미 있어요!")
                    else:
                        st.session_state.site_configs.append({'id': str(uuid.uuid4()), 'name': new_site_name.strip(), 'weight': new_site_weight, 'is_default': False, 'user_count': 0})
                        st.success(f"'{new_site_name}' 사이트가 추가되었어요!")
                        st.experimental_rerun()
                else:
                    st.warning("새 사이트 이름을 입력해주세요!")
    st.markdown("---")
    st.subheader("현재 설정된 사이트 목록:")
    sites_to_delete_ids_sidebar = []
    for i, site_config_sidebar in enumerate(st.session_state.site_configs):
        with st.container():
            st.markdown(f"**{site_config_sidebar['name']}** (현재 가중치: {site_config_sidebar['weight']})")
            col1_edit, col2_edit, col3_edit = st.columns([3,2,1])
            new_name_sidebar = col1_edit.text_input(f"이름 변경##{site_config_sidebar['id']}", value=site_config_sidebar['name'], label_visibility="collapsed")
            new_weight_sidebar = col2_edit.number_input(f"가중치 변경##{site_config_sidebar['id']}", value=float(site_config_sidebar['weight']), min_value=0.1, step=0.1, label_visibility="collapsed")
            action_col = col3_edit
            if action_col.button("💾", key=f"save_sidebar_{site_config_sidebar['id']}", help="이 사이트 정보 저장"):
                is_duplicate = False
                if new_name_sidebar.strip().lower() != site_config_sidebar['name'].lower():
                    if any(s['name'].lower() == new_name_sidebar.strip().lower() for s_idx, s in enumerate(st.session_state.site_configs) if s_idx != i):
                        is_duplicate = True
                if not new_name_sidebar.strip(): st.warning(f"'{site_config_sidebar['name']}' 사이트의 이름은 비워둘 수 없어요!")
                elif is_duplicate: st.warning(f"'{new_name_sidebar.strip()}' 이름은 이미 다른 사이트가 사용 중이에요!")
                else:
                    st.session_state.site_configs[i]['name'] = new_name_sidebar.strip()
                    st.session_state.site_configs[i]['weight'] = new_weight_sidebar
                    st.success(f"'{st.session_state.site_configs[i]['name']}' 정보가 업데이트되었어요!")
                    st.experimental_rerun()
            if not site_config_sidebar.get('is_default', False) or len(st.session_state.site_configs) > 1:
                if action_col.button("🗑️", key=f"delete_sidebar_{site_config_sidebar['id']}", help="이 사이트 삭제"):
                    sites_to_delete_ids_sidebar.append(site_config_sidebar['id'])
            else: action_col.caption("기본")
            st.markdown("---")
    if sites_to_delete_ids_sidebar:
        st.session_state.site_configs = [s for s in st.session_state.site_configs if s['id'] not in sites_to_delete_ids_sidebar]
        st.success("선택한 사이트가 삭제되었어요!")
        st.experimental_rerun()

st.markdown("<div style='text-align:center;'><h2 style='margin-bottom:0px;'>📝 새로운 키워드 입력</h2></div>", unsafe_allow_html=True)
st.session_state.keyword_input_val = st.text_input(
    '📌 키워드 입력:', value=st.session_state.keyword_input_val,
    placeholder='연구하고 싶은 주제 키워드를 입력하세요', key="main_keyword_input",
    label_visibility="collapsed"
).strip()

st.markdown("<div style='text-align:center;'><h3 style='font-weight:normal; margin-top:20px; margin-bottom:5px;'>각 사이트별 검색 결과 수 입력</h3></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'><p style='color:grey; font-size:0.9em; margin-bottom:15px;'>*직접 검색해서 검색 결과를 입력해보세요.</p></div>", unsafe_allow_html=True)

for site_idx, site_config_main in enumerate(st.session_state.site_configs):
    current_val_main = int(site_config_main.get('user_count', 0))
    st.session_state.site_configs[site_idx]['user_count'] = st.number_input(
        f"📚 {site_config_main['name']} (가중치: {site_config_main['weight']}):", min_value=0,
        value=current_val_main, key=f"count_input_{site_config_main['id']}", step=1
    )

calc_button_cols = st.columns([1, 1.8, 1]) 
with calc_button_cols[1]:
    if st.button('🔍 데이터 가용성 점수 계산하기', key="calc_avail_button_main", use_container_width=True):
        if not st.session_state.keyword_input_val:
            display_html_message("키워드를 입력해주세요!", type="warning_red_text", duration_sec=2)
        else:
            has_any_count = any(int(site.get('user_count',0)) > 0 for site in st.session_state.site_configs)
            if not has_any_count:
                display_html_message("검색 결과 수를 입력해주세요!", type="warning_red_text", duration_sec=2)
            else:
                with st.spinner(""): 
                    time.sleep(0.5) 
                    score, weighted_sum, raw_counts_summary, top_sites_for_score = calculate_data_availability_score_from_configs()
                    st.session_state.data_availability_score_result = (score, weighted_sum, raw_counts_summary, top_sites_for_score)
                display_html_message("분석 완료!", type="success", icon_char_override="✅", duration_sec=1)

if st.session_state.data_availability_score_result:
    score, weighted_sum, raw_counts_summary, top_sites_for_score = st.session_state.data_availability_score_result
    emoji, message, color = {
        4: ("🎉", "풍년일세! 자료가 넘쳐나서 행복한 고민이에요!", "#32CD32"),
        3: ("👌", "이 정도면 충분! 파고들 만하겠어요!", "#1E90FF"),
        2: ("💧", "가뭄의 단비... 자료가 좀 부족하지만, 희귀템을 노려볼까요?", "#FFA500"),
        1: ("🏜️", "사막인가요... 정말 특별한 각오가 필요하겠어요!", "#FF4500"),
    }.get(score, ("🤔", "음... 점수를 다시 확인해봐야겠어요.", "#808080"))
    result_html = f"""
    <div style="background-color: #f0f0f0; padding: 15px; border-radius: 10px; margin: 20px auto; text-align:center; max-width: 700px;">
        <h3 style="text-align:center;">"{st.session_state.keyword_input_val}" 키워드 분석 결과</h3>
        <h4>입력된 전체 검색 결과:</h4><ul style='list-style-position: inside; padding-left: 0; text-align: center;'>"""
    for site_name_res, data_res in raw_counts_summary.items():
        result_html += f"<li style='text-align:center; margin-left: 0;'>{site_name_res}: {data_res['count']}개 (설정 가중치: {data_res['weight']})</li>"
    result_html += "</ul>"
    if top_sites_for_score:
        result_html += "<h4>점수 계산에 반영된 상위 사이트 기여도:</h4><ul style='list-style-position: inside; padding-left: 0; text-align: center;'>"
        for site_data_res in top_sites_for_score:
            result_html += f"<li style='text-align:center; margin-left: 0;'>{site_data_res['name']}: {site_data_res['raw_count']}개 (가중치 {site_data_res['weight']} 적용, 기여도: {site_data_res['contribution']:.1f})</li>"
        result_html += "</ul>"
    else: result_html += "<p>입력된 검색 결과가 없어 점수 계산에 반영된 사이트가 없어요.</p>"
    result_html += f"""
        <p style="text-align:center;"><strong>✨ 가중치 적용 총합 (상위 사이트 기준): {weighted_sum:.1f} ✨</strong></p>
        <h2 style="color: {color}; text-align:center;">데이터 가용성 점수: {score}점 {emoji}</h2>
        <h4 style="color: {color}; text-align:center;">{message}</h4></div>"""
    st.markdown(result_html, unsafe_allow_html=True)

st.markdown("<div style='text-align:center;'><hr style='margin: 30px auto 15px auto; width: 80%;'></div>", unsafe_allow_html=True) 
st.markdown('<div style="text-align:center;"><h2 style="margin-bottom:15px;">💡 참신성/흥미도/미래가치 점수 직접 선택하기</h2></div>', unsafe_allow_html=True)
explanation_box_st("""<b>✨ 유레카 지수란? (1~4점)</b><br>"이 주제, 다른 친구들은 잘 모르는 나만의 숨겨진 보석 같아!<br>새로운 관점으로 세상을 놀라게 할 수 있을 것 같아!"<br><span style="font-size:0.9em;">4점: 완전히 새로운 발견! 아무도 연구하지 않은 분야<br>3점: 기존과는 다른 새로운 시각이 있는 주제<br>2점: 익숙하지만 나만의 독특한 관점이 있음<br>1점: 많은 사람들이 다루는 일반적인 주제</span>""")
st.session_state.eureka_slider_val = st.slider('✨ 유레카 지수:', 1, 4, st.session_state.eureka_slider_val, key="eureka_slider_main")
explanation_box_st("""<b>💓 덕질 가능 지수란? (1~4점)</b><br>"이 주제만 생각하면 밤새도록 자료를 찾아보고 싶을 만큼 너무너무 재미있고 흥미진진해!<br>내 열정을 불태울 수 있어!"<br><span style="font-size:0.9em;">4점: 완전 몰입! 이것만 생각하면 밤새 행복해짐<br>3점: 충분히 흥미롭고 파고들 가치가 있음<br>2점: 평범하게 재미있는 수준<br>1점: 별로 흥미롭지 않은 주제</span>""")
st.session_state.fan_slider_val = st.slider('💓 덕질 가능 지수:', 1, 4, st.session_state.fan_slider_val, key="fan_slider_main")
explanation_box_st("""<b>🚀 성장 잠재력 지수란? (1~4점)</b><br>"이 주제, 지금도 중요하지만 앞으로 우리 사회에 더 큰 영향을 줄 수 있는 엄청난 잠재력이 느껴져!<br>미래를 예측하고 대비하는 데 도움이 될 것 같아!"<br><span style="font-size:0.9em;">4점: 미래 사회를 바꿀 혁신적인 주제<br>3점: 앞으로 더 중요해질 가능성이 높은 주제<br>2점: 현재와 미래에 적당히 의미 있는 주제<br>1점: 미래 발전 가능성이 낮은 주제</span>""")
st.session_state.potential_slider_val = st.slider('🚀 성장 잠재력 지수:', 1, 4, st.session_state.potential_slider_val, key="potential_slider_main")

add_keyword_cols = st.columns([1, 1.8, 1]) 
with add_keyword_cols[1]:
    if st.button('✅ 키워드 추가하기', key="add_keyword_button_main_submit", use_container_width=True):
        keyword_to_add = st.session_state.keyword_input_val
        if not keyword_to_add: 
            display_html_message("키워드를 입력해주세요!", type="warning_red_text", duration_sec=2)
        elif st.session_state.data_availability_score_result is None: 
            display_html_message("먼저 '데이터 가용성 점수 계산하기' 버튼을 눌러 점수를 계산해주세요!", type="warning_red_text", icon_char_override="⚠️", duration_sec=2)
        else:
            if keyword_to_add in st.session_state.keywords_data['키워드'].values: 
                display_html_message(f"'{keyword_to_add}' 키워드는 이미 목록에 있어요!", type="warning_red_text", icon_char_override="⚠️", duration_sec=2)
            else:
                data_score_to_add, _, _, _ = st.session_state.data_availability_score_result
                new_data_entry = pd.DataFrame([{'키워드': keyword_to_add, '데이터가용성점수': data_score_to_add, '유레카지수': st.session_state.eureka_slider_val, '덕질가능지수': st.session_state.fan_slider_val, '성장잠재력지수': st.session_state.potential_slider_val}])
                st.session_state.keywords_data = pd.concat([st.session_state.keywords_data, new_data_entry], ignore_index=True)
                display_html_message(f"'{keyword_to_add}' 키워드가 추가되었어요!", type="success", icon_char_override="✨", duration_sec=1.5)
                reset_inputs()
                st.experimental_rerun()

if not st.session_state.keywords_data.empty:
    st.markdown("<div style='text-align:center;'><hr style='margin: 30px auto 15px auto; width: 80%;'></div>", unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;"><h3 style="margin-bottom:15px;">📋 지금까지 추가된 키워드 목록</h3></div>', unsafe_allow_html=True)
    
    keywords_list_for_delete = ["삭제할 키워드 선택..."] + st.session_state.keywords_data['키워드'].tolist()
    delete_cols = st.columns([0.8, 1.4, 0.8]) 
    with delete_cols[1]:
        keyword_to_delete_select = st.selectbox("삭제할 키워드 선택:", options=keywords_list_for_delete, index=0, key="delete_kw_select", label_visibility="collapsed")
        if keyword_to_delete_select != "삭제할 키워드 선택...":
            if st.button(f"🗑️ '{keyword_to_delete_select}' 삭제", key="delete_selected_keyword_button", use_container_width=True):
                st.session_state.keywords_data = st.session_state.keywords_data[st.session_state.keywords_data['키워드'] != keyword_to_delete_select].reset_index(drop=True)
                display_html_message(f"'{keyword_to_delete_select}' 키워드가 삭제되었어요!", type="info", icon_char_override="🗑️", duration_sec=1.5)
                st.session_state.delete_kw_select = "삭제할 키워드 선택..." 
                st.experimental_rerun()
    
    st.dataframe(st.session_state.keywords_data.style.background_gradient(cmap='YlGnBu', subset=['데이터가용성점수', '유레카지수', '덕질가능지수', '성장잠재력지수']).set_table_styles([{'selector': 'th', 'props': [('text-align', 'center'), ('font-size', '1.05em'), ('padding', '10px 12px')]}, {'selector': 'td', 'props': [('text-align', 'center'), ('padding', '8px 10px')]} ]).set_properties(**{'text-align': 'center', 'width': '150px'}), use_container_width=True)
            
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    
    button_row_cols = st.columns([0.4, 1.2, 0.15, 1.2, 0.4]) 
    with button_row_cols[1]:
        csv_data = st.session_state.keywords_data.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        download_button_component(label="📥 CSV 파일 다운로드", data=csv_data, file_name="키워드_분석_결과.csv", mime='text/csv', key_suffix="csv_final_v5")
    
    with button_row_cols[3]:
        excel_output = io.BytesIO()
        with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
            st.session_state.keywords_data.to_excel(writer, index=False, sheet_name='키워드분석')
        excel_data = excel_output.getvalue()
        download_button_component(label="📊 엑셀 파일 다운로드", data=excel_data, file_name="키워드_분석_결과.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', key_suffix="excel_main_final_v5")

if not st.session_state.keywords_data.empty:
    st.markdown("<div style='text-align:center;'><hr style='margin: 30px auto 15px auto; width: 80%;'></div>", unsafe_allow_html=True)
    
    # --- "그래프 크게 보기" 버튼 ---
    graph_action_cols = st.columns([1,1.8,1,1.8,1]) # 버튼 두 개를 위한 공간 (예시)
    with graph_action_cols[1]:
        if st.button('📊 모든 키워드 그래프로 보기', key="show_graph_button_main_toggle", use_container_width=True):
            st.session_state.show_graph_section = not st.session_state.get('show_graph_section', False)
            st.session_state.show_large_graph_dialog = False # 크게 보기 창은 닫기
    
    # "그래프 크게 보기" 버튼 (그래프가 활성화 되어 있을 때만 표시)
    if st.session_state.get('show_graph_section', False):
        with graph_action_cols[3]:
            if st.button("🔍 그래프 더 크게 보기", key="open_large_graph_dialog", use_container_width=True):
                st.session_state.show_large_graph_dialog = True
                st.experimental_rerun() # 다이얼로그를 즉시 띄우기 위해

elif 'show_graph_section' in st.session_state and st.session_state.keywords_data.empty:
    st.session_state.show_graph_section = False
    st.session_state.show_large_graph_dialog = False


# --- 일반 그래프 표시 로직 ---
if st.session_state.get('show_graph_section', False) and not st.session_state.get('show_large_graph_dialog', False) and not st.session_state.keywords_data.empty:
    st.markdown('<div style="text-align:center;"><h2 style="margin-bottom:15px;">📈 키워드 시각화 맵</h2></div>', unsafe_allow_html=True)
    assessment_options_graph = {'종합 점수 (평균)': 'average', '유레카 지수 (참신성)': '유레카지수', '덕질 가능 지수 (흥미도)': '덕질가능지수', '성장 잠재력 지수 (미래성)': '성장잠재력지수'}
    
    graph_select_cols = st.columns([0.5, 3, 0.5]) 
    with graph_select_cols[1]:
        selected_assessment_label_graph = st.selectbox('그래프 평가 기준 선택:', options=list(assessment_options_graph.keys()), index=0, key="graph_assessment_type_select_main", label_visibility="collapsed")
    assessment_type_graph = assessment_options_graph[selected_assessment_label_graph]

    graph_spinner_cols_main = st.columns([0.5, 3, 0.5])
    with graph_spinner_cols_main[1]:
        with st.spinner("그래프를 그리고 있어요! 예쁘게 나올 거예요! 🎨"):
            time.sleep(0.1) 
            df_graph_plot = st.session_state.keywords_data.copy()
            
            for col in ['유레카지수', '덕질가능지수', '성장잠재력지수', '데이터가용성점수']:
                df_graph_plot[col] = pd.to_numeric(df_graph_plot[col], errors='coerce')
            df_graph_plot = df_graph_plot.dropna(subset=['유레카지수', '덕질가능지수', '성장잠재력지수', '데이터가용성점수'])

            if df_graph_plot.empty:
                display_html_message("이런! 유효한 데이터가 없어서 그래프를 그릴 수 없어요.", type="warning_red_text", duration_sec=0, is_persistent=True) 
            else:
                if assessment_type_graph == 'average':
                    df_graph_plot['종합점수'] = df_graph_plot[['유레카지수', '덕질가능지수', '성장잠재력지수']].astype(float).mean(axis=1)
                    df_graph_plot['종합점수'] = df_graph_plot['종합점수'].apply(lambda x: round(x, 2) if pd.notnull(x) else np.nan)
                    y_column_graph = '종합점수'
                    title_suffix_graph = '종합 점수'
                else:
                    y_column_graph = assessment_type_graph
                    title_suffix_graph = selected_assessment_label_graph.split('(')[0].strip()
                
                df_graph_plot = df_graph_plot.dropna(subset=[y_column_graph, '데이터가용성점수'])
                if df_graph_plot.empty:
                    display_html_message("평가 기준에 따른 유효 데이터가 없어 그래프를 그릴 수 없습니다.", type="warning_red_text", duration_sec=0, is_persistent=True) 
                else:
                    # 일반 그래프 크기 및 폰트 설정
                    main_font_sizes = {'title': 28, 'label': 25, 'tick': 20, 'quad_text': 20, 'annotate': 20}
                    fig_main_graph, _ = generate_scatter_plot(df_graph_plot, y_column_graph, title_suffix_graph, 
                                                              fig_size=(17, 14), font_sizes_config=main_font_sizes) # 아가씨가 조정한 크기
                    st.pyplot(fig_main_graph)
                    plt.close(fig_main_graph) # 메모리 관리를 위해 명시적으로 닫기

                    st.markdown('<div style="text-align:center; margin-top:30px;"><h3>✨ 보석 키워드 추천 ✨</h3></div>', unsafe_allow_html=True)
                    quadrants_rec = {"🌟 최고의 보석 (자료 풍부, 높은 가치)": df_graph_plot[(df_graph_plot['데이터가용성점수'] >= 2.5) & (df_graph_plot[y_column_graph] >= 2.5)], 
                                     "💡 도전적인 보석 (자료 부족, 높은 가치)": df_graph_plot[(df_graph_plot['데이터가용성점수'] < 2.5) & (df_graph_plot[y_column_graph] >= 2.5)], 
                                     "👍 안정적 선택 (자료 풍부, 낮은 가치)": df_graph_plot[(df_graph_plot['데이터가용성점수'] >= 2.5) & (df_graph_plot[y_column_graph] < 2.5)], 
                                     "🤔 재고려 필요 (자료 부족, 낮은 가치)": df_graph_plot[(df_graph_plot['데이터가용성점수'] < 2.5) & (df_graph_plot[y_column_graph] < 2.5)]}
                    badge_colors_rec = {"🌟 최고의 보석 (자료 풍부, 높은 가치)": "#28a745", 
                                        "💡 도전적인 보석 (자료 부족, 높은 가치)": "#ffc107", 
                                        "👍 안정적 선택 (자료 풍부, 낮은 가치)": "#17a2b8", 
                                        "🤔 재고려 필요 (자료 부족, 낮은 가치)": "#dc3545"} # 이모티콘 제거된 키
                    for category_rec, keywords_in_cat_rec in quadrants_rec.items():
                        if not keywords_in_cat_rec.empty:
                            st.markdown(f'<h4 style="text-align:center; color:#555; margin-top:15px;">{category_rec.replace("🌟 ", "").replace("💡 ", "").replace("👍 ", "").replace("🤔 ", "")}</h4>', unsafe_allow_html=True) # 제목에서 이모티콘 제거
                            num_cols_rec = min(3, len(keywords_in_cat_rec)) if len(keywords_in_cat_rec) > 0 else 1
                            cols_rec = st.columns(num_cols_rec)
                            for idx_rec, (_, row_data_rec) in enumerate(keywords_in_cat_rec.iterrows()):
                                current_badge_color_rec = badge_colors_rec.get(category_rec, "#6c757d") # 직접 키로 찾기
                                with cols_rec[idx_rec % num_cols_rec]:
                                    st.markdown(f"""<div style="margin: 8px 0; padding: 12px; border-radius: 8px; background-color: #f8f9fa; border-left: 6px solid {current_badge_color_rec}; box-shadow: 2px 2px 5px #eee;"><strong style="font-size:1.1em;">{row_data_rec['키워드']}</strong><span style="float: right; padding: 3px 10px; border-radius: 12px; background-color: {current_badge_color_rec}; color: white; font-size:0.9em;">점수: {row_data_rec[y_column_graph]:.2f}</span></div>""", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True) 

# --- "그래프 크게 보기" 다이얼로그 로직 ---
if st.session_state.get('show_large_graph_dialog', False) and not st.session_state.keywords_data.empty:
    # 현재 선택된 평가 기준을 가져오기 (위의 selectbox 값 활용)
    selected_assessment_label_dialog = st.session_state.get("graph_assessment_type_select_main", list(assessment_options_graph.keys())[0]) # 기본값
    assessment_type_dialog = assessment_options_graph[selected_assessment_label_dialog]
    
    df_dialog_plot = st.session_state.keywords_data.copy()
    for col in ['유레카지수', '덕질가능지수', '성장잠재력지수', '데이터가용성점수']:
        df_dialog_plot[col] = pd.to_numeric(df_dialog_plot[col], errors='coerce')
    df_dialog_plot = df_dialog_plot.dropna(subset=['유레카지수', '덕질가능지수', '성장잠재력지수', '데이터가용성점수'])

    if not df_dialog_plot.empty:
        if assessment_type_dialog == 'average':
            df_dialog_plot['종합점수'] = df_dialog_plot[['유레카지수', '덕질가능지수', '성장잠재력지수']].astype(float).mean(axis=1)
            df_dialog_plot['종합점수'] = df_dialog_plot['종합점수'].apply(lambda x: round(x, 2) if pd.notnull(x) else np.nan)
            y_column_dialog = '종합점수'
            title_suffix_dialog = '종합 점수'
        else:
            y_column_dialog = assessment_type_dialog
            title_suffix_dialog = selected_assessment_label_dialog.split('(')[0].strip()
        
        df_dialog_plot = df_dialog_plot.dropna(subset=[y_column_dialog, '데이터가용성점수'])

        if not df_dialog_plot.empty:
            with st.dialog("산점도 그래프 크게 보기", True): # True로 width를 최대로 사용
                st.markdown(f"<h3 style='text-align:center;'>{selected_assessment_label_dialog} 기준</h3>", unsafe_allow_html=True)
                # 다이얼로그용 더 큰 그래프 크기 및 폰트 설정
                dialog_font_sizes = {'title': 32, 'label': 28, 'tick': 22, 'quad_text': 22, 'annotate': 20}
                fig_dialog_graph, _ = generate_scatter_plot(df_dialog_plot, y_column_dialog, title_suffix_dialog, 
                                                            fig_size=(22, 18), font_sizes_config=dialog_font_sizes) # 훨씬 크게!
                st.pyplot(fig_dialog_graph)
                plt.close(fig_dialog_graph) # 다이얼로그용 그래프도 닫기

                close_button_cols = st.columns([1,0.5,1]) # 닫기 버튼 중앙 정렬
                with close_button_cols[1]:
                    if st.button("닫기", key="close_dialog_button", use_container_width=True):
                        st.session_state.show_large_graph_dialog = False
                        st.experimental_rerun()
        else:
            # 이 경우는 거의 없겠지만, 만약을 위해
            if st.session_state.show_large_graph_dialog: # 다이얼로그가 열리려고 했다면
                 display_html_message("선택된 기준으로 표시할 데이터가 없어 큰 그래프를 열 수 없습니다.", type="info", duration_sec=0, is_persistent=True)
                 st.session_state.show_large_graph_dialog = False # 다이얼로그 상태 초기화


elif st.session_state.get('show_graph_section', False) and st.session_state.keywords_data.empty:
    display_html_message("앗, 그래프를 그리려면 먼저 키워드를 추가해야 해요!", type="info", duration_sec=0, is_persistent=True) 
    st.session_state.show_graph_section = False 
    st.session_state.show_large_graph_dialog = False

st.markdown("<div style='text-align:center;'><hr style='margin: 30px auto 15px auto; width: 80%;'></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:grey; font-size:0.9em;'>✨ 나만의 보석 키워드 발굴 시스템 by 꾸물 ✨<br>contact: zambi23@naver.com</p>", unsafe_allow_html=True)
