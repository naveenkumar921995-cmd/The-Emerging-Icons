import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime

# ================== BASIC CONFIG ==================
st.set_page_config(
    page_title="The Emerging Icons",
    page_icon="⭐",
    layout="wide"
)

# ================== DATABASE ==================
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    title TEXT,
    profile TEXT,
    story TEXT,
    image TEXT,
    featured INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    approved INTEGER DEFAULT 0,
    created_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
    username TEXT,
    password TEXT
)
""")

# create default admin
cursor.execute("SELECT * FROM admin")
if not cursor.fetchone():
    password = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute("INSERT INTO admin VALUES (?,?)", ("admin", password))
    conn.commit()

# ================== FUNCTIONS ==================
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def admin_login(user, pw):
    cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (user, hash_password(pw)))
    return cursor.fetchone()

def luxury_css():
    st.markdown("""
    <style>
    body {
        background-color:#0e0e0e;
        color:#ffffff;
        font-family:'Georgia', serif;
    }
    .card {
        background:#151515;
        padding:25px;
        border-radius:16px;
        box-shadow:0 0 40px rgba(255,215,0,0.12);
        margin-bottom:30px;
    }
    h1,h2,h3 {
        color:#d4af37;
    }
    .metric {
        color:#999;
        font-size:14px;
    }
    </style>
    """, unsafe_allow_html=True)

luxury_css()

# ================== HEADER ==================
st.markdown("<h1 style='text-align:center'>THE EMERGING ICONS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#aaa'>India’s Next Generation of Entrepreneurs</p>", unsafe_allow_html=True)
st.divider()

# ================== SIDEBAR ==================
menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Featured Stories", "Submit Story", "Admin Login"]
)

# ================== HOME ==================
if menu == "Home":
    cursor.execute("SELECT * FROM stories WHERE approved=1 ORDER BY created_at DESC")
    stories = cursor.fetchall()

    for s in stories:
        cursor.execute("UPDATE stories SET views = views + 1 WHERE id=?", (s[0],))
        conn.commit()

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col1, col2 = st.columns([1,3])

        if s[5] and os.path.exists(s[5]):
            col1.image(s[5], width=220)

        col2.subheader(s[2])
        col2.write(f"**{s[1]}**")
        col2.write(s[4][:280] + "...")
        col2.caption(f"❤️ {s[7]}  | 👁 {s[8]}")

        if col2.button("Read Full Story", key=f"read{s[0]}"):
            st.session_state["story_id"] = s[0]
            st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ================== STORY PAGE ==================
if "story_id" in st.session_state:
    sid = st.session_state["story_id"]
    cursor.execute("SELECT * FROM stories WHERE id=?", (sid,))
    story = cursor.fetchone()

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header(story[2])
    st.subheader(story[1])

    if story[5] and os.path.exists(story[5]):
        st.image(story[5], width=500)

    st.write(story[4])
    st.caption(f"❤️ {story[7]}  | 👁 {story[8]}")

    if st.button("❤️ Like Story"):
        cursor.execute("UPDATE stories SET likes = likes + 1 WHERE id=?", (sid,))
        conn.commit()
        st.experimental_rerun()

    if st.button("⬅ Back"):
        del st.session_state["story_id"]
        st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ================== FEATURED ==================
if menu == "Featured Stories":
    cursor.execute("SELECT * FROM stories WHERE approved=1 AND featured=1")
    feats = cursor.fetchall()

    for s in feats:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader(s[2])
        st.write(f"**{s[1]}**")
        st.write(s[4][:300] + "...")
        st.markdown("</div>", unsafe_allow_html=True)

# ================== SUBMIT ==================
if menu == "Submit Story":
    st.subheader("Submit Your Entrepreneur Story")

    with st.form("submit"):
        name = st.text_input("Entrepreneur Name")
        title = st.text_input("Story Title")
        profile = st.text_area("Short Profile")
        story = st.text_area("Full Story")
        image = st.file_uploader("Upload Cover Image", ["jpg","png"])
        submit = st.form_submit_button("Submit")

        if submit:
            img_path = None
            if image:
                img_path = f"images/{datetime.now().timestamp()}_{image.name}"
                with open(img_path,"wb") as f:
                    f.write(image.read())

            cursor.execute("""
            INSERT INTO stories (name,title,profile,story,image,created_at)
            VALUES (?,?,?,?,?,?)
            """,(name,title,profile,story,img_path,datetime.now().isoformat()))
            conn.commit()
            st.success("Story submitted for admin approval.")

# ================== ADMIN ==================
if menu == "Admin Login":
    st.subheader("Admin Panel")

    if "admin" not in st.session_state:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")

        if st.button("Login"):
            if admin_login(user,pw):
                st.session_state["admin"] = True
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

    else:
        cursor.execute("SELECT * FROM stories WHERE approved=0")
        pending = cursor.fetchall()

        for s in pending:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader(s[2])
            st.write(s[1])

            if st.button("Approve", key=f"a{s[0]}"):
                cursor.execute("UPDATE stories SET approved=1 WHERE id=?", (s[0],))
                conn.commit()
                st.experimental_rerun()

            if st.button("Feature", key=f"f{s[0]}"):
                cursor.execute("UPDATE stories SET featured=1 WHERE id=?", (s[0],))
                conn.commit()
                st.experimental_rerun()

            st.markdown("</div>", unsafe_allow_html=True)
