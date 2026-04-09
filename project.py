import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="BBW Violet local Chatbot", layout="centered")
st.title("🛀\🧼 BBW Violet local Chatbot")

# -------------------------
# Model call (REPLACE THIS)
# -------------------------
def call_model(prompt: str) -> str:

    data={
        "userId": "test-user-123",
        "sessionId": "test-session-001",
        "text": prompt
        }
    response=requests.post("https://cognigy-endpoint-na1.nicecxone.com/2f49b31b79a21dade213025fe32b5d7acd78b733cd276dbdc77d943114f86cdb",data=data)
    return f"Model response for: {response.json()['text']}"

# -------------------------
# Session State
# -------------------------
if "chat_history" not in st.session_state:
    # For UI display (manual + csv)
    st.session_state.chat_history = []

if "results" not in st.session_state:
    # For downloadable results (mainly csv batch, but can include manual too)
    st.session_state.results = []

if "processing_done" not in st.session_state:
    st.session_state.processing_done = False

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# -------------------------
# Top Controls: Clear Chat
# -------------------------
col_a, col_b = st.columns([1, 3])

with col_a:
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.results = []
        st.session_state.processing_done = False
        st.session_state.is_processing = False
        st.rerun()

with col_b:
    st.caption("Upload CSV + Start for batch prompts, or use manual chat input below.")

st.divider()

# -------------------------
# CSV Upload + Start
# -------------------------
uploaded_file = st.file_uploader("📄 Upload CSV", type=["csv"])
prompt_col = st.text_input("Prompt column name in CSV", value="prompt")

start_clicked = st.button("▶️ Start CSV Run", disabled=(uploaded_file is None or st.session_state.is_processing))

# Placeholder for progress and live updates
progress_bar = st.empty()
status_text = st.empty()

# -------------------------
# Manual Chat (Input at top-ish)
# -------------------------
with st.form("manual_chat_form", clear_on_submit=True):
    user_input = st.text_input("Type a message (manual):")
    send_clicked = st.form_submit_button("Send")

if send_clicked and user_input.strip():
    prompt = user_input.strip()
    response = call_model(prompt)

    st.session_state.chat_history.append({"source": "manual", "prompt": prompt, "response": response})
    st.session_state.results.append({"source": "manual", "prompt": prompt, "response": response})

# -------------------------
# Scrollable Chat Display (Below)
# -------------------------
chat_box = st.container(height=420)

def render_chat():
    with chat_box:
        if not st.session_state.chat_history:
            st.info("No messages yet. Send a manual message or run CSV batch.")
        else:
            for item in st.session_state.chat_history:
                src = "🧑 Manual" if item["source"] == "manual" else "📄 CSV"
                st.markdown(f"**{src} Prompt:** {item['prompt']}")
                st.markdown(f"**🤖 Response:** {item['response']}")
                st.markdown("---")

render_chat()

# -------------------------
# CSV Batch Processing
# -------------------------
if start_clicked and uploaded_file is not None:
    st.session_state.is_processing = True
    st.session_state.processing_done = False

    try:
        df = pd.read_csv(uploaded_file)

        if prompt_col not in df.columns:
            st.session_state.is_processing = False
            st.error(f"Column '{prompt_col}' not found in CSV. Available columns: {list(df.columns)}")
            st.stop()

        total = len(df)
        if total == 0:
            st.session_state.is_processing = False
            st.warning("CSV has no rows to process.")
            st.stop()

        progress = st.progress(0)
        status_text.info("Starting CSV processing...")

        # Process row by row
        for i, row in df.iterrows():
            prompt = str(row[prompt_col]).strip()

            # Skip empty prompts safely
            if not prompt:
                continue

            # Call model
            response = call_model(prompt)

            # Append to UI chat
            st.session_state.chat_history.append({"source": "csv", "prompt": prompt, "response": response})

            # Append to results (for download)
            st.session_state.results.append({"source": "csv", "prompt": prompt, "response": response})

            # Update progress + status
            pct = int(((i + 1) / total) * 100)
            progress.progress(min(pct, 100))
            status_text.info(f"Processing CSV row {i+1}/{total}...")

            # Re-render chat so you see updates live
            render_chat()

            # Small delay to simulate model latency (optional)
            time.sleep(0.05)

        st.session_state.processing_done = True
        status_text.success("✅ CSV processing completed.")
        st.session_state.is_processing = False

    except Exception as e:
        st.session_state.is_processing = False
        st.error(f"Error while processing CSV: {e}")

st.divider()

# -------------------------
# Download Button (Only after CSV completion)
# -------------------------
if st.session_state.processing_done:
    # Download BOTH prompts + responses (includes manual + csv by default)
    result_df = pd.DataFrame(st.session_state.results)

    st.download_button(
        label="⬇️ Download Prompts + Responses (CSV)",
        data=result_df.to_csv(index=False),
        file_name="prompts_and_responses.csv",
        mime="text/csv"
    )
else:
    st.caption("Download will appear after CSV execution completes ✅")
