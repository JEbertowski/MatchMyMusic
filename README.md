# 🎵 MatchMyMusic  

✨ **An AI-powered music recommendation experience** ✨  
Describe your mood or situation, and MatchMyMusic pairs you with the perfect song. Complete with 🎨 album art and 🎧 Spotify preview. Built with Streamlit, GPT-3.5, and the Spotify Web API.  

---

## 🚀 Live Demo  
👉 [Try the app live on Streamlit](https://matchmymusic.streamlit.app)  

---

## 🖼️ Screenshots  

<table>
  <tr>
    <td align="center">
      <img width="450" alt="PC Version" src="https://github.com/user-attachments/assets/880506e3-bd8a-49e1-83bd-113549ef07b0" />
      <br><sub>💻 Desktop Version</sub>
    </td>
    <td align="center">
      <img width="250" alt="Mobile Version" src="https://github.com/user-attachments/assets/6556d238-f6ed-4335-849b-4f724cbaad78" />
      <br><sub>📱 Mobile Version</sub>
    </td>
  </tr>
</table>  

*(📜 History on the left | 🎶 Recommendation UI in the center | 🎨 Album cover + 🎧 Spotify preview)*  

---

## 🔎 How It Works  

1. ✍️ **Enter your mood or activity** (e.g., “needing an upbeat workout jam”)  
2. 🤖 Sent to **OpenAI GPT-3.5**, which suggests a song  
3. 🎼 Song + artist are searched via **Spotify Web API**  
4. 🖼️ App displays:  
   - 🎨 Album cover  
   - 🔗 Spotify link  
   - 🎧 30-sec audio preview  
5. 🕒 Your recommendation is saved in **history** for later reference  

---

## ✨ Features  

- 🤖 **GPT-based recommendations** — creative and context-aware  
- 🎧 **Spotify integration** — album covers + audio previews  
- 📜 **History sidebar** — revisit past suggestions anytime  
- 👍👎 **Feedback logging** — track which recs hit the mark  
- 📱 **Mobile-friendly UI** — optimized with responsive CSS  
- 🔒 **Secure secrets management** — powered by Streamlit’s `st.secrets`  

---

## 🛠️ Tech Stack  

| 🔧 Purpose            | ⚡ Tools                                                                 |
|-----------------------|-------------------------------------------------------------------------|
| 🌐 Web framework      | [Streamlit](https://streamlit.io/)                                      |
| 🤖 AI Recommendations | [OpenAI GPT-3.5](https://openai.com/)                                   |
| 🎧 Music API          | [Spotify Web API](https://developer.spotify.com/documentation/web-api/) |
| 🎨 Visual design      | Custom CSS (frosted glass effect, background, mobile tweaks)            |
| 🚀 Deployment         | GitHub + Streamlit Community Cloud                                     |

---

## 💻 Usage  

1. **Clone the repository**  
   git clone https://github.com/JEbertowski/MatchMyMusic.git
   cd MatchMyMusic

2. **Create and activate a virtual environment**
python -m venv .venv
source .venv/bin/activate   # On Mac/Linux
.venv\Scripts\activate      # On Windows

3. **Install dependencies**
pip install -r requirements.txt

4. **Set up secrets**
OPENAI_API_KEY = "your_openai_key_here"
SPOTIFY_CLIENT_ID = "your_spotify_client_id_here"
SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret_here"

5. **Run the app locally**
streamlit run matchmymusic_app.py

6. **Open http://localhost:8501 in your browser and enjoy** 🎶


📜 License
MIT © 2025 Justin Ebertowski
