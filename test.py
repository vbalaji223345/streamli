import streamlit as st
import pandas as pd
import requests
import time

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
    try:
        data = {
            "userId": user_id,
            "sessionId": session_id,
            "text": prompt
        }
        response = requests.post(
            "https://cognigy-endpoint-na1.nicecxone.com/2f49b31b79a21dade213025fe32b5d7acd78b733cd276dbdc77d943114f86cdb",
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

# -------------------------
# 5. SIDEBAR: Controls & Credentials (UPDATED)
# -------------------------
with st.sidebar:
    st.title("🛀 Violet Controls")
    
    # New Input Boxes for User and Session ID
    st.subheader("BBW User details")
    u_id = st.text_input("User ID", value="test-user-123")
    s_id = st.text_input("Session ID", value="test-session-001")
    
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
            avatar = "📄" if item["source"] == "csv" else "🧑‍💻"
            with st.chat_message("user", avatar=avatar):
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
    st.session_state.results.append({"source": "manual", "prompt": prompt, "response": response})
    st.rerun()

# -------------------------
# 8. CSV Batch Logic (UPDATED)
# -------------------------
if start_clicked and uploaded_file is not None:
    st.session_state.is_processing = True
    st.session_state.processing_done = False

    try:
        df = pd.read_csv(uploaded_file)
        if prompt_col not in df.columns:
            status_area.error(f"Column '{prompt_col}' not found.")
            st.session_state.is_processing = False
        else:
            total = len(df)
            status_area.info(f"Processing {total} rows...")
            
            for i, row in df.iterrows():
                p = str(row[prompt_col]).strip()
                if p:
                    # Passing the IDs from the sidebar text inputs
                    resp = call_model(p, u_id, s_id)
                    st.session_state.chat_history.append({"source": "csv", "prompt": p, "response": resp})
                    st.session_state.results.append({"source": "csv", "prompt": p, "response": resp})
                
                pct = int(((i + 1) / total) * 100)
                progress_bar.progress(pct)
                status_area.info(f"Processing: {i+1}/{total}")
            
            st.session_state.processing_done = True
            st.session_state.is_processing = False
            status_area.success("✅ Batch Complete!")
            st.rerun()

    except Exception as e:
        st.session_state.is_processing = False
        status_area.error(f"Error: {e}")
