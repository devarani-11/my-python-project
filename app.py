import streamlit as st
import sqlite3
from datetime import datetime
from gtts import gTTS
from genai_radio_functions import init_db, fetch_live_news, generate_mcqs

# ==============================
# App Configuration
# ==============================
st.set_page_config(page_title="GenAI Radio", page_icon="🎙", layout="centered")
init_db()

# ==============================
# Landing Page
# ==============================
def landing_page():
    st.title("🎙 GenAI Radio")
    st.write("AI-powered personalized podcast with quiz")

    if st.button("Continue"):
        st.session_state.page = "login"
        st.rerun()

# ==============================
# Login Page
# ==============================
def login_page():
    st.subheader("Login / Sign Up")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.warning("Please enter all fields")
            return

        conn = sqlite3.connect("genai_radio.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        if user and user[2] != password:
            st.error("Incorrect password")
            conn.close()
            return

        if not user:
            c.execute(
                "INSERT INTO users (username, password) VALUES (?,?)",
                (username, password)
            )
            conn.commit()

        conn.close()
        st.session_state.username = username
        st.session_state.page = "podcast"
        st.rerun()

# ==============================
# Podcast Page
# ==============================
def podcast_page():
    st.subheader(f"Welcome, {st.session_state.username}")

    topics = [
        "Current Affairs", "Sports", "AI Technology",
        "Entertainment", "Psychology", "History", "Politics"
    ]

    selected_topics = st.multiselect("Select exactly 3 topics", topics)

    if st.button("Generate Podcast"):
        if len(selected_topics) != 3:
            st.warning("Please select exactly 3 topics")
            return

        podcast_text = "Welcome to your AI-generated podcast.\n\n"
        for topic in selected_topics:
            podcast_text += fetch_live_news(topic) + "\n\n"
        podcast_text += "Thank you for listening."

        filename = f"podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        gTTS(text=podcast_text, lang="en").save(filename)

        conn = sqlite3.connect("genai_radio.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO podcasts (username, date, topics, filename)
            VALUES (?, ?, ?, ?)
        """, (
            st.session_state.username,
            datetime.now().isoformat(),
            ", ".join(selected_topics),
            filename
        ))
        conn.commit()
        conn.close()

        st.session_state.audio = filename
        st.session_state.selected_topics = selected_topics
        st.session_state.page = "player"
        st.rerun()

# ==============================
# Player Page
# ==============================
def player_page():
    st.subheader("🎧 Your Podcast")
    st.audio(st.session_state.audio)

    if st.button("Take Quiz"):
        st.session_state.page = "quiz"
        st.session_state.mcqs = None
        st.rerun()

# ==============================
# Quiz Page (WITH ANSWERS SHOWN)
# ==============================
def quiz_page():
    st.subheader("🧠 Quiz")

    if st.session_state.mcqs is None:
        st.session_state.mcqs = generate_mcqs(
            st.session_state.selected_topics
        )
        st.session_state.answers = []
        st.session_state.qindex = 0

    mcqs = st.session_state.mcqs
    i = st.session_state.qindex

    # ======================
    # RESULTS PAGE
    # ======================
    if i >= len(mcqs):
        score = 0
        st.subheader("📊 Quiz Results")

        for idx, q in enumerate(mcqs):
            user_ans = st.session_state.answers[idx]
            correct_ans = q["answer"]

            st.write(f"**Q{idx+1}. {q['question']}**")

            if user_ans == correct_ans:
                st.success(f"✅ Your answer: {user_ans}")
                score += 1
            else:
                st.error(f"❌ Your answer: {user_ans}")
                st.info(f"✔ Correct answer: {correct_ans}")

            st.markdown("---")

        st.success(f"🏆 Final Score: {score} / {len(mcqs)}")
        return

    # ======================
    # QUESTIONS PAGE
    # ======================
    q = mcqs[i]
    st.write(f"Q{i+1}. {q['question']}")
    choice = st.radio("Choose one:", q["options"], key=i)

    if st.button("Next"):
        st.session_state.answers.append(choice)
        st.session_state.qindex += 1
        st.rerun()

# ==============================
# Navigation
# ==============================
def main():
    if "page" not in st.session_state:
        st.session_state.page = "landing"

    pages = {
        "landing": landing_page,
        "login": login_page,
        "podcast": podcast_page,
        "player": player_page,
        "quiz": quiz_page
    }

    pages[st.session_state.page]()

if __name__ == "__main__":
    main()