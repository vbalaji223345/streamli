import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
from zoneinfo import ZoneInfo

def generate_short_month_id(prefix):
    # Set the timezone to IST (Asia/Kolkata)
    ist_tz = ZoneInfo("Asia/Kolkata")
    timestamp = datetime.now(ist_tz).strftime("%b%d%H%M%S")
    return f"{prefix}_{timestamp}"

# -------------------------
# 1. Page Configuration
# -------------------------
st.set_page_config(page_title="BBW Violet Chatbot", page_icon="🛀", layout="centered")

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
  </style>
""", unsafe_allow_html=True)

# -------------------------
# 3. Model Logic (UPDATED)
# -------------------------
def call_model(prompt: str, user_id: str, session_id: str) -> str:
  st.session_state.api_call_count += 1
  try:
    data = {
      "userId": user_id,
      "sessionId": session_id,
      "text": prompt
    }
    response = requests.post(
      "https://cognigy-endpoint-na1.nicecxone.com/a5f82edf75b1fba8321010c6de0eee01d4d9d672ce6381361682aac5aadfda1e",# new End Point
      data=data,
      timeout=15
    )
    return response.json().get('text', "No response text found.")
  except Exception as e:
    return f"Error connecting to model: {e}"

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

# -------------------------
# 5. SIDEBAR: Controls & Credentials (UPDATED)
# -------------------------
with st.sidebar:
  st.title("🛀 Violet Controls")
  st.metric(label="🔢 API Calls This Session", value=st.session_state.api_call_count)

  st.subheader("BBW User details")
  prefix_input = st.text_input("Enter Prefix", placeholder="e.g. B")

  if st.button("🔑 Generate IDs", use_container_width=True):
    if prefix_input.strip():
      st.session_state.generated_user_id = generate_short_month_id(f"{prefix_input}_U")
      st.session_state.generated_session_id = generate_short_month_id(f"{prefix_input}_S")
    else:
      st.warning("Please enter a prefix first.")

  st.markdown("**User ID**")
  user_id_display = st.empty()
  user_id_display.caption(st.session_state.generated_user_id if st.session_state.generated_user_id else "—")

  st.markdown("**Session ID**")
  session_id_display = st.empty()
  session_id_display.caption(st.session_state.generated_session_id if st.session_state.generated_session_id else "—")

  u_id = st.session_state.generated_user_id
  s_id = st.session_state.generated_session_id
  
  st.divider()

  if st.button("🗑️ Clear All History", use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.results = []
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
st.title("🛀\🧼 BBW Violet local Chatbot")

chat_container = st.container(height=400)

with chat_container:
  if not st.session_state.chat_history:
    st.info("Chat history is empty.")
  else:
    for item in st.session_state.chat_history:
      if item.get("type") == "batch":
        with st.chat_message("user", avatar="📄"):
          st.write(item['prompt1'])
        with st.chat_message("assistant", avatar="🤖"):
          st.write(item['response1'])
        with st.chat_message("user", avatar="📄"):
          st.write(item['prompt2'])
        with st.chat_message("assistant", avatar="🤖"):
          st.write(item['response2'])
      else:
        with st.chat_message("user", avatar="🧑‍💻"):
          st.write(item['prompt'])
        with st.chat_message("assistant", avatar="🤖"):
          st.write(item['response'])

# -------------------------
# 7. Manual Input Logic (UPDATED)
# -------------------------
if prompt := st.chat_input("Message Violet..."):
  with st.spinner("Violet is thinking..."):
    # Passing the IDs from the sidebar text inputs
    response = call_model(prompt, u_id, s_id)
  
  st.session_state.chat_history.append({"source": "manual", "prompt": prompt, "response": response})
  st.session_state.results.append({"User id": u_id, "Session id": s_id, "source": "manual", "prompt1": prompt, "response1": response})
  st.rerun()

# -------------------------
# 8. CSV Batch Logic (UPDATED)
# -------------------------
if start_clicked and uploaded_file is not None:
  st.session_state.is_processing = True
  st.session_state.processing_done = False
  # st.session_state.results = []

  batch_prefix = prefix_input.strip() if prefix_input.strip() else "U"

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
        # Auto-generate unique IDs per row using same format as manual
        row_user_id = generate_short_month_id(f"{batch_prefix}_U")
        row_session_id = generate_short_month_id(f"{batch_prefix}_S")
        user_id_display.caption(row_user_id)
        session_id_display.caption(row_session_id)

        # Turn 1: greeting
        resp1 = call_model("Hi", row_user_id, row_session_id)
        time.sleep(0.3)

        # Turn 2: actual prompt
        resp2 = call_model(p, row_user_id, row_session_id)
        time.sleep(0.2)

        st.session_state.results.append({
          "User id": row_user_id,
          "Session id": row_session_id,
          "source":"csv",
          "prompt1": "Hi",
          "response1": resp1,
          "prompt2": p,
          "response2": resp2,
        })
        st.session_state.chat_history.append({
          "type": "batch",
          "user_id": row_user_id,
          "session_id": row_session_id,
          "source":"csv",
          "prompt1": "Hi",
          "response1": resp1,
          "prompt2": p,
          "response2": resp2,
        })

        progress_bar.progress(int((idx / total) * 100))
        status_area.info(f"Processing: {idx}/{total}")

      st.session_state.processing_done = True
      st.session_state.is_processing = False
      status_area.success("✅ Batch Complete!")
      st.rerun()

  except Exception as e:
    st.session_state.is_processing = False
    status_area.error(f"Error: {e}")
