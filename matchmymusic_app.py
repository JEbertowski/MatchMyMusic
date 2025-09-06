import streamlit as st
import openai
import os
import base64
from dotenv import load_dotenv
from datetime import datetime

# Load API key
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(page_title="🎵 MatchMyMusic", page_icon="🎶", layout="centered")

# --- Set background image ---
def set_background(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Dark overlay for text contrast ---
overlay_css = """
<style>
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: -1;
}
</style>
"""
st.markdown(overlay_css, unsafe_allow_html=True)

# --- Styles + frosted container start ---
st.markdown(
    """
    <style>
    .frosted-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 16px;
        color: #111 !important;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
    }

    h1 {
        text-align: center;
        color: #6c47ff !important;
        font-weight: 800;
        text-shadow: 1px 1px 3px rgba(255, 255, 255, 0.4);
    }

    p.subtitle {
        text-align: center;
        font-size: 18px;
        color: #111 !important;
        font-weight: 600;
    }

    .stAlert {
        background-color: rgba(255, 255, 255, 0.96) !important;
        color: #111 !important;
        border-left: 0.4rem solid #6c47ff;
        font-weight: 600;
        text-shadow: none;
    }

    .stTextInput > label {
        color: #111 !important;
        font-weight: 700 !important;
    }

    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.97) !important;
        color: #111 !important;
        font-weight: 600;
        border: 1px solid #ccc;
    }

    .stButton button {
        color: #111 !important;
        font-weight: 700;
        background-color: #ffffff !important;
        border: 1px solid #aaa;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.15);
    }

    .stMarkdown, .css-1v0mbdj, .css-ffhzg2 {
        color: #111 !important;
        font-weight: 600;
        text-shadow: 0 0 1px rgba(255, 255, 255, 0.5);
    }

    .stApp {
        -webkit-font-smoothing: antialiased;
    }
    </style>

    <div class="frosted-box">
        <h1>🎵 MatchMyMusic</h1>
        <p class="subtitle">Describe your <b>mood, vibe, or moment</b> — and I’ll match you with the perfect song.</p>
    """,
    unsafe_allow_html=True
)

# --- Set the background image ---
set_background("MMM_Background.png")

# --- Initialize session state ---
if "recommendation_history" not in st.session_state:
    st.session_state.recommendation_history = []

if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

# --- Sidebar history ---
with st.sidebar:
    st.markdown("## 📜 History")
    if st.session_state.recommendation_history:
        for item in reversed(st.session_state.recommendation_history):
            st.markdown(f"""
                - 🕒 **{item['timestamp']}**
                - 💬 *{item['input']}*
                - 🎧 {item['recommendation']}
                ---
            """)
    else:
        st.info("No recommendations yet.")

# --- User input ---
user_input = st.text_input("💬 How are you feeling or what are you doing right now?", placeholder="e.g. I'm cleaning and need something upbeat")
feedback_placeholder = st.empty()

# --- Prompt builder ---
def build_prompt(user_input):
    return f"""You are a helpful music recommendation assistant.

The user will describe a mood, moment, or situation. Based on that, recommend a song that fits best. Your suggestion should include the song title, artist, and a 1-sentence explanation of why it fits the user's mood.

Respond in the format:
"I recommend '[Song Title]' by [Artist] because [reason]."

User input: "{user_input}"
"""

# --- Call OpenAI ---
def recommend_song(user_input):
    prompt = build_prompt(user_input)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )
    return response.choices[0].message.content.strip()

# --- Recommendation button ---
if st.button("🎧 Get Recommendation", use_container_width=True):
    if not user_input:
        st.warning("Please describe your mood or activity.")
    else:
        with st.spinner("Finding the perfect track... 🎶"):
            try:
                result = recommend_song(user_input)
                st.markdown("### ✅ Your Song Recommendation")
                st.success(result)

                # Save to history
                st.session_state.recommendation_history.append({
                    "input": user_input,
                    "recommendation": result,
                    "timestamp": datetime.now().strftime("%b %d, %Y %I:%M %p")
                })

                # Feedback
                with feedback_placeholder.container():
                    st.markdown("### Was this recommendation helpful?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("👍 Yes", key="upvote"):
                            st.success("Thanks for the feedback! 👍")
                            st.session_state.feedback_log.append({
                                "input": user_input,
                                "recommendation": result,
                                "feedback": "👍"
                            })
                    with col2:
                        if st.button("👎 No", key="downvote"):
                            st.info("Sorry to hear that! 👎")
                            st.session_state.feedback_log.append({
                                "input": user_input,
                                "recommendation": result,
                                "feedback": "👎"
                            })

            except Exception as e:
                st.error("⚠️ Something went wrong. Please try again.")
                st.exception(e)

# --- Close frosted container ---
st.markdown("</div>", unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; font-size: 14px;'>Built with ❤️ using Streamlit and GPT-3.5 | <i>by Justin Ebertowski</i></p>",
    unsafe_allow_html=True
)
