import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime, date

# ================== PAGE CONFIG ==================
st.set_page_config(page_title="The Emerging Icons", page_icon="⭐", layout="wide")

# ================== SESSION STATE ==================
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False
if "admin_user" not in st.session_state:
    st.session_state["admin_user"] = None
if "story_id" not in st.session_state:
    st.session_state["story_id"] = None

# ================== DATABASE ==================
os.makedirs("images", exist_ok=True)
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables if not exists
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

# Add expiry_date safely
try:
    cursor.execute("ALTER TABLE stories ADD COLUMN expiry_date TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

# Default admin
cursor.execute("SELECT * FROM admin")
if not cursor.fetchone():
    default_pw = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute("INSERT INTO admin VALUES (?,?)", ("admin", default_pw))
    conn.commit()

# ================== FUNCTIONS ==================
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def admin_login(user, pw):
    return cursor.execute(
        "SELECT * FROM admin WHERE username=? AND password=?",
        (user, hash_password(pw))
    ).fetchone() is not None

# ================== PREMIUM CSS ==================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    font-family:'Poppins', sans-serif;
    color:#fff;
}
h1,h2,h3 { color:#ffd700; }
.card {
    background:#1c1c1c;
    padding:25px;
    border-radius:16px;
    box-shadow:0 0 50px rgba(255,215,0,0.15);
    margin-bottom:30px;
    transition: transform 0.2s;
}
.card:hover {transform: scale(1.02);}
.logout-btn {text-align:right; margin-bottom:20px;}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown("<h1 style='text-align:center'>THE EMERGING ICONS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#ddd'>India’s Next Generation of Entrepreneurs</p>", unsafe_allow_html=True)
st.divider()

# ================== SIDEBAR ==================
menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Featured Stories", "Submit Story", "Admin Login"]
)

today = date.today().isoformat()

# ================== HOME ==================
if menu == "Home" and st.session_state["story_id"] is None:
    cursor.execute("""
        SELECT * FROM stories 
        WHERE approved=1 AND (expiry_date IS NULL OR expiry_date >= ?)
        ORDER BY created_at DESC
    """, (today,))
    stories = cursor.fetchall()
    story_to_open = None

    # Responsive grid: 3 columns
    for i in range(0, len(stories), 3):
        cols = st.columns(3)
        for idx, s in enumerate(stories[i:i+3]):
            with cols[idx]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                if s[5] and os.path.exists(s[5]):
                    st.image(s[5], use_column_width='always')
                st.subheader(s[2])
                st.write(f"**{s[1]}**")
                st.write(s[4][:150]+"...")
                st.caption(f"❤️ {s[7]} | 👁 {s[8]}")
                if st.button("Read Full Story", key=f"read{s[0]}"):
                    story_to_open = s[0]
                st.markdown("</div>", unsafe_allow_html=True)
            cursor.execute("UPDATE stories SET views = views + 1 WHERE id=?", (s[0],))
            conn.commit()
    if story_to_open:
        st.session_state["story_id"] = story_to_open
        st.experimental_rerun()

# ================== STORY PAGE ==================
if st.session_state["story_id"]:
    sid = st.session_state["story_id"]
    cursor.execute("SELECT * FROM stories WHERE id=?", (sid,))
    story = cursor.fetchone()
    if story:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.header(story[2])
        st.subheader(story[1])
        if story[5] and os.path.exists(story[5]):
            st.image(story[5], use_column_width=True)
        st.write(story[4])
        st.caption(f"❤️ {story[7]} | 👁 {story[8]}")
        if st.button("❤️ Like Story"):
            cursor.execute("UPDATE stories SET likes = likes + 1 WHERE id=?", (sid,))
            conn.commit()
            st.experimental_rerun()
        if st.button("⬅ Back"):
            st.session_state["story_id"] = None
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ================== FEATURED STORIES ==================
if menu == "Featured Stories":
    cursor.execute("""
        SELECT * FROM stories 
        WHERE approved=1 AND featured=1 
        AND (expiry_date IS NULL OR expiry_date >= ?)
        ORDER BY created_at DESC
    """, (today,))
    feats = cursor.fetchall()
    if feats:
        st.markdown("### Featured Stories")
        # Horizontal scroll effect using columns
        cols = st.columns(len(feats))
        for idx, s in enumerate(feats):
            with cols[idx]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                if s[5] and os.path.exists(s[5]):
                    st.image(s[5], use_column_width=True)
                st.subheader(s[2])
                st.write(f"**{s[1]}**")
                st.write(s[4][:100]+"...")
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No featured stories yet.")

# ================== SUBMIT STORY ==================
if menu == "Submit Story":
    st.subheader("Submit Your Entrepreneur Story")
    with st.form("submit_story_form"):
        name = st.text_input("Entrepreneur Name")
        title = st.text_input("Story Title")
        profile = st.text_area("Short Profile")
        story_text = st.text_area("Full Story")
        image = st.file_uploader("Upload Cover Image", ["jpg","png"])
        submit = st.form_submit_button("Submit")
        if submit:
            img_path = None
            if image:
                img_path = f"images/{datetime.now().timestamp()}_{image.name}"
                with open(img_path, "wb") as f:
                    f.write(image.read())
            cursor.execute("""
                INSERT INTO stories (name,title,profile,story,image,created_at)
                VALUES (?,?,?,?,?,?)
            """, (name, title, profile, story_text, img_path, datetime.now().isoformat()))
            conn.commit()
            st.success("Story submitted for admin approval.")

# ================== ADMIN PANEL ==================
if menu == "Admin Login":
    st.subheader("Admin Panel")
    if not st.session_state["admin_logged_in"]:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if admin_login(user, pw):
                st.session_state["admin_logged_in"] = True
                st.session_state["admin_user"] = user
                st.success(f"Login successful! Welcome, {user} ✅")
            else:
                st.error("Invalid credentials")
    else:
        # Logout button top
        st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state["admin_logged_in"] = False
            st.session_state["admin_user"] = None
            st.success("Logged out successfully")
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.info(f"You are logged in as Admin: {st.session_state['admin_user']} ✅")

        # Pending stories
        cursor.execute("SELECT * FROM stories WHERE approved=0 ORDER BY created_at DESC")
        pending = cursor.fetchall()
        for s in pending:
            with st.form(f"story_form_{s[0]}"):
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.subheader(s[2])
                st.write(f"**{s[1]}**")
                expiry_for_story = st.date_input("Set expiry date (optional)", min_value=date.today(), key=f"expiry{s[0]}")
                col1, col2 = st.columns(2)
                approve_clicked = col1.form_submit_button("Approve")
                feature_clicked = col2.form_submit_button("Feature")
                st.markdown("</div>", unsafe_allow_html=True)
                if approve_clicked:
                    cursor.execute("UPDATE stories SET approved=1, expiry_date=? WHERE id=?",
                                   (expiry_for_story.isoformat() if expiry_for_story else None, s[0]))
                    conn.commit()
                    st.success("Story approved ✅")
                    st.experimental_rerun()
                if feature_clicked:
                    cursor.execute("UPDATE stories SET featured=1, expiry_date=? WHERE id=?",
                                   (expiry_for_story.isoformat() if expiry_for_story else None, s[0]))
                    conn.commit()
                    st.success("Story featured ⭐")
                    st.experimental_rerun()
