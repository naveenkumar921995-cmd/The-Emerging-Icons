import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime, date

# ================== FOLDERS ==================
os.makedirs("data", exist_ok=True)
os.makedirs("images", exist_ok=True)

DB_PATH = "data/data.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# ================== TABLE CREATION ==================
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
    cursor.execute(
        "INSERT INTO admin VALUES (?,?)",
        ("admin", hashlib.sha256("admin123".encode()).hexdigest())
    )
    conn.commit()

# ================== SESSION STATE ==================
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False
if "admin_user" not in st.session_state:
    st.session_state["admin_user"] = None
if "story_id" not in st.session_state:
    st.session_state["story_id"] = None

# ================== FUNCTIONS ==================
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def admin_login(user, pw):
    return cursor.execute(
        "SELECT * FROM admin WHERE username=? AND password=?",
        (user, hash_password(pw))
    ).fetchone() is not None

# ================== PREMIUM DARK LUXE CSS ==================
st.markdown("""
<style>
/* Overall page */
body {
    background: linear-gradient(135deg,#0e0e0e,#1a1a1a,#2c2c2c);
    font-family:'Poppins', sans-serif;
    color:#fff;
}

/* Hero section */
.hero {
  width: 100%;
  height: 420px;
  background-image: url('https://source.unsplash.com/1600x900/?business,entrepreneur');
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
}
.hero-text {
  text-align: center;
  color: #ffd700;
  text-shadow: 1px 2px 15px rgba(0,0,0,0.7);
}
.hero-text h1 {
  font-size: 3.5rem;
  font-weight: bold;
}
.hero-text p {
  font-size: 1.6rem;
}

/* Card style */
.premium-card {
    background: rgba(30,30,30,0.9);
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0 10px 30px rgba(255,215,0,0.2);
    margin-bottom: 30px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.premium-card:hover {
    transform: scale(1.03);
    box-shadow: 0 12px 40px rgba(255,215,0,0.4);
}
.premium-card h3 { color: #ffd700; }
.premium-card p { color: #ddd; }

/* Buttons */
.stButton>button {
    background-color: #ffd700;
    color: #0e0e0e;
    font-weight:bold;
    border-radius: 8px;
    padding: 8px 15px;
}
.stButton>button:hover {
    background-color: #ffcc00;
}

/* Logout */
.logout-btn { text-align:right; margin-bottom:20px; }

/* Footer */
.footer {
    padding:20px;
    text-align:center;
    color:#bbb;
    font-size:14px;
}
</style>
""", unsafe_allow_html=True)

# ================== HERO SECTION ==================
st.markdown("""
<div class="hero">
  <div class="hero-text">
    <h1>Discover India’s Next Icons</h1>
    <p>Stories of Vision, Grit & Legacy</p>
  </div>
</div>
""", unsafe_allow_html=True)

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

    for s in stories:
        st.markdown(f"<div class='premium-card'>", unsafe_allow_html=True)
        if s[5] and os.path.exists(s[5]):
            st.image(s[5], use_column_width=True)
        st.subheader(s[2])
        st.write(f"**{s[1]}**")
        st.write(s[4][:200]+"...")
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
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
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
        cols = st.columns(len(feats))
        for idx, s in enumerate(feats):
            with cols[idx]:
                st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
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
                st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
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

# ================== FOOTER ==================
st.markdown("""
<div class="footer">
    © 2026 The Emerging Icons - Ultra Luxury Edition | Powered by Streamlit
</div>
""", unsafe_allow_html=True)
