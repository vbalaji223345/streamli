import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import requests
import time
from datetime import datetime
from zoneinfo import ZoneInfo

def generate_short_month_id(prefix):
    ist_tz = ZoneInfo("Asia/Kolkata")
    timestamp = datetime.now(ist_tz).strftime("%b%d%H%M%S")
    return f"{prefix}_{timestamp}"

# -------------------------
# 1. Page Configuration
# -------------------------
st.set_page_config(page_title="BBW Violet Chatbot", page_icon="🛀", layout="centered", initial_sidebar_state="expanded")

#to hide fork and git hub icons with full hamburger menu
lock_sidebar_css = """
    <style>

        [data-testid="stToolbar"] {
            display: none !important;
        }

        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }

        [data-testid="collapsedControl"] {
            display: none !important;
        }
    </style>
"""
st.markdown(lock_sidebar_css, unsafe_allow_html=True)

#To hide footer
hide_st_style = """
    <style>
    footer { visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style,unsafe_allow_html=True)

html(
    """
    <script>
    window.top.document.querySelectorAll('[href*="streamlit.io"]').forEach(e => e.setAttribute("style", "display: none;"));
    </script>
    """,
    height=0,
)

# -------------------------
# 2. Custom CSS
# -------------------------
st.markdown("""
  <style>
    [data-testid="stChatMessage"] {
      padding-top: 0.5rem !important;
      padding-bottom: 0.5rem !important;
    }
    .stStatusWidget { display: none !important; }
    .block-container { padding-top: 2rem !important; }
    hr { margin: 1em 0px !important; }
    .uid-tooltip-wrap {
      position: relative;
      display: inline-block;
    }
    .uid-info-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 15px;
      height: 15px;
      background: #4a9eff;
      color: white;
      border-radius: 50%;
      font-size: 10px;
      font-weight: bold;
      font-style: normal;
      cursor: pointer;
      vertical-align: middle;
      margin-left: 5px;
    }
    .uid-tooltip-text {
      visibility: hidden;
      opacity: 0;
      background: #1e2a3a;
      color: #e0e0e0;
      border-radius: 6px;
      padding: 10px 12px;
      position: absolute;
      z-index: 99999;
      left: 120%;
      top: -8px;
      width: 340px;
      font-size: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.4);
      transition: opacity 0.2s;
      pointer-events: none;
    }
    .uid-tooltip-text table {
      border-collapse: collapse;
      width: 100%;
    }
    .uid-tooltip-text th {
      color: #7ec8ff;
      padding: 3px 8px;
      text-align: left;
      border-bottom: 1px solid #3a4a5a;
    }
    .uid-tooltip-text td {
      padding: 3px 8px;
      border-bottom: 1px solid #2a3a4a;
    }
    .uid-tooltip-text .tt-title {
      font-weight: bold;
      color: #7ec8ff;
      margin-bottom: 6px;
      display: block;
    }
    .uid-tooltip-wrap:hover .uid-tooltip-text {
      visibility: visible;
      opacity: 1;
    }
    [data-testid="stChatMessage"] button {
      font-size: 8px !important;
      padding: 1px 3px !important;
      min-height: 0px !important;
      height: 22px !important;
      line-height: 1 !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
    }
  </style>
""", unsafe_allow_html=True)

# -------------------------
# 3. Model Logic (UPDATED)
# -------------------------
def call_model(prompt: str, user_id: str, session_id: str) -> tuple[str, float]:
  st.session_state.api_call_count += 1
  start = time.perf_counter()
  try:
    data = {
      "userId": user_id,
      "sessionId": session_id,
      "text": prompt
    }
    response = requests.post(
      "https://cognigy-endpoint-na1.nicecxone.com/6941693df79d403a8afa34f8c98242e8dd90d62546734ebf1e20870a6d143953",# new prod End Point
      data=data,
      timeout=15
    )
    latency_ms = (time.perf_counter() - start) * 1000
    return response.json().get('text', "No response text found."), latency_ms
  except Exception as e:
    latency_ms = (time.perf_counter() - start) * 1000
    return f"Error connecting to model: {e}", latency_ms

def latency_badge(ms: float, turn: int | None = None) -> str:
  if ms <= 3000:
    color, bg = "#1a7f37", "#dafbe1"
  elif ms <= 5000:
    color, bg = "#9a6700", "#fff8c5"
  else:
    color, bg = "#cf222e", "#ffebe9"
  label = f"{ms:.0f} ms" if ms < 1000 else f"{ms/1000:.2f} s"
  turn_tag = f'<span style="color:#888;font-weight:400;">Turn {turn}&nbsp;&nbsp;</span>' if turn is not None else ""
  return (
    f'<span style="display:inline-flex;align-items:center;gap:4px;padding:2px 10px;border-radius:12px;'
    f'font-size:11px;font-weight:600;color:{color};background:{bg};'
    f'border:1px solid {color}33;font-family:monospace;margin-top:4px;">'
    f'{turn_tag}⏱ {label}</span>'
  )

# -------------------------
# 4. Session State Initialization
# -------------------------
if "chat_history" not in st.session_state:
  st.session_state.chat_history = []
if "results" not in st.session_state:
  st.session_state.results = []
if "processing_done" not in st.session_state:
  st.session_state.processing_done = False
if "is_processing" not in st.session_state:
  st.session_state.is_processing = False
if "generated_user_id" not in st.session_state:
  st.session_state.generated_user_id = ""
if "generated_session_id" not in st.session_state:
  st.session_state.generated_session_id = ""
if "api_call_count" not in st.session_state:
  st.session_state.api_call_count = 0
if "verdicts" not in st.session_state:
  st.session_state.verdicts = {}

# -------------------------
# 5. SIDEBAR: Controls & Credentials (UPDATED)
# -------------------------
with st.sidebar:
  st.title("🛀 Violet Controls")
  st.metric(label="🔢 API Calls This Session", value=st.session_state.api_call_count)

  _latencies = [item["latency_ms"] for item in st.session_state.chat_history if "latency_ms" in item]
  if _latencies:
    _avg = sum(_latencies) / len(_latencies)
    _min, _max = min(_latencies), max(_latencies)
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg", f"{_avg/1000:.2f}s")
    col2.metric("Min", f"{_min/1000:.2f}s")
    col3.metric("Max", f"{_max/1000:.2f}s")

  st.subheader("BBW User details")
  prefix_input = st.text_input("Enter Prefix", placeholder="e.g. B")

  if st.button("🔑 Generate IDs", use_container_width=True):
    if prefix_input.strip():
      st.session_state.generated_user_id = generate_short_month_id(f"{prefix_input}_U")
      st.session_state.generated_session_id = generate_short_month_id(f"{prefix_input}_S")
    else:
      st.warning("Please enter a prefix first.")

  _uid = st.session_state.generated_user_id
  if _uid:
    _ts = _uid.rsplit('_', 1)[-1]   # e.g. "May060851047"
    _month, _day, _hour, _minute, _second = _ts[:3], _ts[3:5], _ts[5:7], _ts[7:9], _ts[9:11]
    try:
      _h = int(_hour)
      _ampm = "AM" if _h < 12 else "PM"
      _h12 = _h % 12 or 12
      _di = int(_day)
      _sfx = "th" if 11 <= _di <= 13 else ["th","st","nd","rd","th","th","th","th","th","th"][_di % 10]
      _hour_meaning = f"The hour in 24-hour time ({_h12}:00 {_ampm})"
      _day_meaning  = f"The day of the month (the {_di}{_sfx})"
    except Exception:
      _hour_meaning, _day_meaning = "The hour in 24-hour time", "The day of the month"
    _month_meaning = f"The month ({_month})"
  else:
    _month = _day = _hour = _minute = _second = "—"
    _month_meaning, _day_meaning, _hour_meaning = "The month", "The day of the month", "The hour in 24-hour time"

  st.markdown(f"""
  <div style="display:flex; align-items:center; margin-bottom:4px;">
    <strong>User ID</strong>
    <span class="uid-tooltip-wrap">
      <i class="uid-info-icon">i</i>
      <span class="uid-tooltip-text">
        <span class="tt-title">Data Breakdown</span>
        <table>
          <tr><th>Segment</th><th>Value</th><th>Meaning</th></tr>
          <tr><td>{_month}</td><td>{_month}</td><td>{_month_meaning}</td></tr>
          <tr><td>{_day}</td><td>{_day}</td><td>{_day_meaning}</td></tr>
          <tr><td>{_hour}</td><td>{_hour}</td><td>{_hour_meaning}</td></tr>
          <tr><td>{_minute}</td><td>{_minute}</td><td>The minute</td></tr>
          <tr><td>{_second}</td><td>{_second}</td><td>The second</td></tr>
        </table>
      </span>
    </span>
  </div>
  """, unsafe_allow_html=True)
  user_id_display = st.empty()
  user_id_display.caption(st.session_state.generated_user_id if st.session_state.generated_user_id else "—")

  st.markdown("**Session ID**")
  session_id_display = st.empty()
  session_id_display.caption(st.session_state.generated_session_id if st.session_state.generated_session_id else "—")

  u_id = st.session_state.generated_user_id
  s_id = st.session_state.generated_session_id
  
  st.divider()

  if st.button("Generate Id & Clear chat", use_container_width=True):
    if prefix_input.strip():
      st.session_state.generated_user_id = generate_short_month_id(f"{prefix_input}_U")
      st.session_state.generated_session_id = generate_short_month_id(f"{prefix_input}_S")
    else:
      st.warning("Please enter a prefix first.")
    st.session_state.chat_history = []
    st.session_state.results = []
    st.session_state.verdicts = {}
    st.session_state.processing_done = False
    st.session_state.is_processing = False
    st.rerun()

  if st.button("🗑️ Clear All History", use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.results = []
    st.session_state.verdicts = {}
    st.session_state.processing_done = False
    st.session_state.is_processing = False
    st.rerun()
    
  st.divider()
  
  st.subheader("📄 Batch Processing")
  uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
  prompt_col = st.text_input("Column name in CSV", value="prompt")
  
  start_clicked = st.button(
    "▶️ Start Batch Process", 
    disabled=(uploaded_file is None or st.session_state.is_processing),
    use_container_width=True,
    type="primary"
  )

  status_area = st.empty()
  progress_bar = st.empty()
  
  st.divider()
  
  if st.session_state.processing_done or len(st.session_state.results) > 0:
    res_df = pd.DataFrame(st.session_state.results)
    res_df["verdict"] = [st.session_state.verdicts.get(i, "") for i in range(len(st.session_state.results))]
    st.download_button(
      label="⬇️ Download Results (CSV)",
      data=res_df.to_csv(index=False),
      file_name="violet_responses.csv",
      mime="text/csv",
      use_container_width=True
    )

# -------------------------
# 6. MAIN WINDOW: UI
# -------------------------
st.title("🧼BBW Violet local Chatbot⁽ᵖʳᵒᵈ⁾")

chat_container = st.container(height=400)

with chat_container:
  if not st.session_state.chat_history:
    st.info("Chat history is empty.")
  else:
    _verdict_options = [
      "RAI Safe", "RAI High Risk", "RAI Low Risk",
      "Unknown", "Customer Treatment Error", "Functional Error",
    ]
    for turn, item in enumerate(st.session_state.chat_history, start=1):
      idx = turn - 1
      avatar = "📄" if item.get("type") == "batch" else "🧑‍💻"
      with st.chat_message("user", avatar=avatar):
        st.write(item['prompt'])
      with st.chat_message("assistant", avatar="🤖"):
        st.write(item['response'])
        if item.get("latency_ms") is not None:
          st.markdown(latency_badge(item["latency_ms"], turn), unsafe_allow_html=True)

        current = st.session_state.verdicts.get(idx, "")
        cols = st.columns(len(_verdict_options))
        for col, opt in zip(cols, _verdict_options):
          if col.button(opt, key=f"v_{turn}_{opt}", type="primary" if current == opt else "secondary", use_container_width=True):
            st.session_state.verdicts[idx] = "" if current == opt else opt
            st.rerun()

# -------------------------
# 7. Manual Input Logic (UPDATED)
# -------------------------
if prompt := st.chat_input("Message Violet..."):
  with st.spinner("Violet is thinking..."):
    response, latency_ms = call_model(prompt, u_id, s_id)

  st.session_state.chat_history.append({"source": "manual", "prompt": prompt, "response": response, "latency_ms": latency_ms})
  st.session_state.results.append({"User id": u_id, "Session id": s_id, "source": "manual", "prompt": prompt, "response": response, "latency (s)": round(latency_ms / 1000, 2)})
  st.rerun()

# -------------------------
# 8. CSV Batch Logic (UPDATED)
# -------------------------
if start_clicked and uploaded_file is not None:
  st.session_state.is_processing = True
  st.session_state.processing_done = False
  # st.session_state.results = []

  batch_prefix = prefix_input.strip() if prefix_input.strip() else "U"

  row_user_id = generate_short_month_id(f"{batch_prefix}_U")
  row_session_id = generate_short_month_id(f"{batch_prefix}_S")

  try:
    df = pd.read_csv(uploaded_file)
    if prompt_col not in df.columns:
      status_area.error(f"Column '{prompt_col}' not found.")
      st.session_state.is_processing = False
    else:
      prompts = [str(v).strip() for v in df[prompt_col] if str(v).strip()]
      total = len(prompts)
      status_area.info(f"Processing {total} prompts...")

      for idx, p in enumerate(prompts, start=1):

        user_id_display.caption(row_user_id)
        session_id_display.caption(row_session_id)

        resp, latency_ms = call_model(p, row_user_id, row_session_id)
        time.sleep(0.2)

        st.session_state.results.append({
          "User id": row_user_id,
          "Session id": row_session_id,
          "source": "csv",
          "prompt": p,
          "response": resp,
          "latency (s)": round(latency_ms / 1000, 2),
        })
        st.session_state.chat_history.append({
          "type": "batch",
          "user_id": row_user_id,
          "session_id": row_session_id,
          "source": "csv",
          "prompt": p,
          "response": resp,
          "latency_ms": latency_ms,
        })

        progress_bar.progress(int((idx / total) * 100))
        status_area.info(f"Processing: {idx}/{total} | Last: {latency_ms/1000:.2f}s")

      st.session_state.processing_done = True
      st.session_state.is_processing = False
      status_area.success("✅ Batch Complete!")
      st.rerun()

  except Exception as e:
    st.session_state.is_processing = False
    status_area.error(f"Error: {e}")
