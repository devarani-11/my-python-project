import sqlite3
import requests
import random

API_KEY = "78e816108dd44859870070b582c9205e"

# ==============================
# Database Initialization
# ==============================
def init_db():
    conn = sqlite3.connect("genai_radio.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS podcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            date TEXT,
            topics TEXT,
            filename TEXT
        )
    """)

    conn.commit()
    conn.close()

# ==============================
# Fetch Live News
# ==============================
def fetch_live_news(topic):
    url = (
        "https://newsapi.org/v2/everything?"
        f"q={topic}+India&language=en&pageSize=5&apiKey={API_KEY}"
    )

    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        titles = [a["title"] for a in data.get("articles", []) if a.get("title")]

        if not titles:
            return f"No recent updates found for {topic}."

        return f"This segment discussed {topic}. " + ". ".join(titles[:5])
    except:
        return f"Could not fetch updates for {topic}."

# ==============================
# Topic-based MCQs (NO BLANKS)
# ==============================
def generate_mcqs(selected_topics):
    mcqs = []

    # MCQ 1
    correct = random.choice(selected_topics)
    options = random.sample(
        [t for t in selected_topics if t != correct], min(2, len(selected_topics)-1)
    ) + random.sample(
        ["Science", "Health", "Economy", "Politics", "Sports"], 2
    )
    options.append(correct)
    random.shuffle(options)

    mcqs.append({
        "question": "Which topic was mainly discussed in the podcast?",
        "options": options,
        "answer": correct
    })

    # MCQ 2
    mcqs.append({
        "question": "What type of content does GenAI Radio generate?",
        "options": [
            "AI-generated news podcasts",
            "Live FM radio streams",
            "Offline music playlists",
            "Recorded classroom lectures"
        ],
        "answer": "AI-generated news podcasts"
    })

    # MCQ 3
    mcqs.append({
        "question": "Which technology converts text into speech in this application?",
        "options": [
            "Google Text-to-Speech",
            "Speech-to-Text API",
            "Manual voice recording",
            "Audio editing software"
        ],
        "answer": "Google Text-to-Speech"
    })

    # MCQ 4
    mcqs.append({
        "question": "From where is the podcast news content obtained?",
        "options": [
            "Live News API",
            "User-uploaded documents",
            "Pre-stored text files",
            "Social media comments"
        ],
        "answer": "Live News API"
    })

    # MCQ 5
    mcqs.append({
        "question": "What is the main goal of the GenAI Radio application?",
        "options": [
            "To generate personalized AI podcasts",
            "To stream live radio channels",
            "To edit professional audio tracks",
            "To download music albums"
        ],
        "answer": "To generate personalized AI podcasts"
    })

    return mcqs