import re
import base64
from datetime import datetime
from urllib.parse import quote

import streamlit as st
import openai
import requests


# ----------------------------- OpenAI client -----------------------------
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ----------------------------- Page config ------------------------------
st.set_page_config(page_title="🎵 MatchMyMusic", page_icon="🎶", layout="centered")


# --------------------------- Background image ---------------------------
def set_background(image_file: str):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
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
        unsafe_allow_html=True,
    )


# ------------------- Global overlay for text contrast -------------------
st.markdown(
    """
    <style>
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.5);
        z-index: -1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------- Core UI / Typography ------------------------
st.markdown(
    """
    <style>
    .frosted-box {
        background: rgba(255,255,255,0.95);
        padding: 2rem;
        border-radius: 16px;
        color: #111 !important;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
    }
    h1 {
        text-align: center;
        color: #6c47ff !important;
        font-weight: 800;
        text-shadow: 1px 1px 3px rgba(255,255,255,0.4);
    }
    p.subtitle {
        text-align: center;
        font-size: 18px;
        color: #111 !important;
        font-weight: 600;
    }
    .stAlert {
        background-color: rgba(255,255,255,0.97) !important;
        color: #111 !important;
        border-left: .4rem solid #6c47ff;
        font-weight: 600;
        text-shadow: none;
    }
    .stTextInput > label { color:#111 !important; font-weight:700 !important; }
    .stTextInput input {
        background-color: rgba(255,255,255,0.97) !important;
        color:#111 !important;
        font-weight:600;
        border: 1px solid #ccc;
    }
    .stButton button {
        color:#111 !important; font-weight:700;
        background:#fff !important; border:1px solid #aaa;
        box-shadow: 2px 2px 5px rgba(0,0,0,.15);
    }
    .stMarkdown, .css-1v0mbdj, .css-ffhzg2 {
        color:#111 !important; font-weight:600;
        text-shadow: 0 0 1px rgba(255,255,255,.5);
    }
    .stApp { -webkit-font-smoothing: antialiased; }

    /* -------- Mobile-friendly tweaks -------- */
    @media (max-width: 768px) {
      .frosted-box { padding: 1rem !important; border-radius: 12px !important; font-size: 15px !important; }
      h1 { font-size: 28px !important; }
      .stTextInput > div > div input { font-size: 15px !important; }
      .stButton button { width: 100% !important; padding: .75rem 1rem !important; }
      .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
      /* Hide sidebar on phones (uncomment to keep it visible) */
      [data-testid="stSidebar"] { display: none; }
      [data-testid="stAppViewBlockContainer"] { margin-left: 0 !important; }
    }
    </style>

    <div class="frosted-box">
        <h1>🎵 MatchMyMusic</h1>
        <p class="subtitle">Describe your <b>mood, vibe, or moment</b> — and I’ll match you with the perfect song.</p>
    """,
    unsafe_allow_html=True,
)


# --------------------------- Background asset ---------------------------
set_background("MMM_Background.png")


# ----------------------------- Session state ----------------------------
if "recommendation_history" not in st.session_state:
    st.session_state.recommendation_history = []
if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []


# -------------------------------- Sidebar -------------------------------
with st.sidebar:
    st.markdown("## 📜 History")
    if st.session_state.recommendation_history:
        for item in reversed(st.session_state.recommendation_history):
            st.markdown(
                f"""
                - 🕒 **{item['timestamp']}**
                - 💬 *{item['input']}*
                - 🎧 {item['recommendation']}
                ---
                """
            )
    else:
        st.info("No recommendations yet.")

    # --- optional debug toggle ---
    DEBUG_SPOTIFY = st.checkbox("🔧 Debug Spotify", value=False)


# --------------------------- Input / Prompting --------------------------
user_input = st.text_input(
    "💬 How are you feeling or what are you doing right now?",
    placeholder="e.g. I'm cleaning and need something upbeat",
)
feedback_placeholder = st.empty()


def build_prompt(user_input: str) -> str:
    return f"""You are a helpful music recommendation assistant.

The user will describe a mood, moment, or situation. Based on that, recommend a song that fits best. Your suggestion should include the song title, artist, and a 1-sentence explanation of why it fits the user's mood.

Respond in the format:
"I recommend '[Song Title]' by [Artist] because [reason]."

User input: "{user_input}"
"""


def recommend_song(user_input: str) -> str:
    prompt = build_prompt(user_input)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )
    return response.choices[0].message.content.strip()


# --------------------------- Spotify helpers (improved) ---------------------------
def get_spotify_token():
    """Client Credentials flow — no user login."""
    cid = st.secrets.get("SPOTIFY_CLIENT_ID")
    csecret = st.secrets.get("SPOTIFY_CLIENT_SECRET")
    if not cid or not csecret:
        return None  # secrets missing

    try:
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(cid, csecret),
            timeout=15,
        )
        r.raise_for_status()
        return r.json().get("access_token")
    except Exception:
        return None


def _spotify_search(token: str, query: str, limit: int = 5):
    url = f"https://api.spotify.com/v1/search?q={quote(query)}&type=track&limit={limit}"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=15)
    if not r.ok:
        return []
    return r.json().get("tracks", {}).get("items", []) or []


def search_spotify_track(song_title: str, artist: str):
    """
    Try multiple queries; prefer the first result with a preview_url.
    Returns (track_name, artist_name, album_image_url, preview_url, spotify_url) or None.
    """
    token = get_spotify_token()
    if not token:
        return None

    queries = [
        f'track:"{song_title}" artist:"{artist}"',
        f'{song_title} {artist}',
        f'track:"{song_title}"',
        song_title,
    ]

    best_item = None
    for q in queries:
        items = _spotify_search(token, q, limit=5)
        if not items:
            continue

        # Prefer an item with a 30s preview
        for it in items:
            if it.get("preview_url"):
                best_item = it
                break

        # Otherwise take the first item
        if not best_item:
            best_item = items[0]

        if best_item:
            break

    if not best_item:
        return None

    img = best_item["album"]["images"][0]["url"] if best_item["album"]["images"] else None
    return (
        best_item["name"],
        best_item["artists"][0]["name"],
        img,
        best_item.get("preview_url"),
        best_item["external_urls"]["spotify"],
    )


def parse_song_and_artist(reco_text: str):
    """
    Robust parse for: I recommend 'Song' by Artist because ...
    Accepts straight/curly quotes and extra punctuation.
    """
    m = re.search(
        r"I recommend\s+['“\"]?(.*?)['”\"]?\s+by\s+(.+?)\s+because",
        reco_text,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return None, None


# ----------------------------- Main action -----------------------------
if st.button("🎧 Get Recommendation", use_container_width=True):
    if not user_input:
        st.warning("Please describe your mood or activity.")
    else:
        with st.spinner("Finding the perfect track... 🎶"):
            try:
                result = recommend_song(user_input)
                st.markdown("### ✅ Your Song Recommendation")
                st.success(result)

                # --------- Try to enrich with Spotify (cover + preview) ---------
                song, artist = parse_song_and_artist(result)
                sp = None
                if song and artist:
                    try:
                        sp = search_spotify_track(song, artist)
                    except Exception:
                        sp = None

                if DEBUG_SPOTIFY:
                    st.write({"parsed_song": song, "parsed_artist": artist, "spotify_result": sp})

                if sp:
                    t_name, a_name, album_img, preview_url, sp_url = sp
                    with st.container():
                        cover_col, info_col = st.columns([1, 2])
                        with cover_col:
                            if album_img:
                                st.image(album_img, use_container_width=True)
                        with info_col:
                            st.markdown(f"**Listen on Spotify:** [{t_name} — {a_name}]({sp_url})")
                            if preview_url:
                                st.audio(preview_url)
                            else:
                                st.caption("No 30-sec preview available for this track.")

                # -------------------- Save to history --------------------
                st.session_state.recommendation_history.append(
                    {
                        "input": user_input,
                        "recommendation": result,
                        "timestamp": datetime.now().strftime("%b %d, %Y %I:%M %p"),
                    }
                )

                # -------------------- Feedback UI -----------------------
                with feedback_placeholder.container():
                    st.markdown("### Was this recommendation helpful?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("👍 Yes", key="upvote"):
                            st.success("Thanks for the feedback! 👍")
                            st.session_state.feedback_log.append(
                                {
                                    "input": user_input,
                                    "recommendation": result,
                                    "feedback": "👍",
                                }
                            )
                    with col2:
                        if st.button("👎 No", key="downvote"):
                            st.info("Sorry to hear that! 👎")
                            st.session_state.feedback_log.append(
                                {
                                    "input": user_input,
                                    "recommendation": result,
                                    "feedback": "👎",
                                }
                            )

            except Exception as e:
                st.error("⚠️ Something went wrong. Please try again.")
                st.exception(e)


# ------------------------- Close frosted container ----------------------
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------- Footer --------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align: center; font-size: 14px;'>Built with ❤️ using Streamlit, OpenAI, and the Spotify Web API | <i>by Justin Ebertowski</i></p>",
    unsafe_allow_html=True,
)
