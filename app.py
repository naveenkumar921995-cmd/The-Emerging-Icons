import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime, date

# ================== BASIC CONFIG ==================
st.set_page_config(
    page_title="The Emerging Icons",
    page_icon="⭐",
    layout="wide"
)

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

# Create tables if they don't exist
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
    created_at TEXT,
    expiry_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
    username TEXT,
    password TEXT
)
""")

# create default admin if not exists
cursor.execute("SELECT * FROM admin")
if not cursor.fetchone():
    default_pw = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute("INSERT INTO admin VALUES (?,?)", ("admin", default_pw))
    conn.commit()

# ================== FUNCTIONS ==================
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def admin_login(user, pw):
    result = cursor.execute(
        "SELECT * FROM admin WHERE username=? AND password=?",
        (user, hash_password(pw))
    ).fetchone()
    return result is not None

def luxury_css():
    st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
        color:#ffffff;
        font-family:'Poppins', sans-serif;
    }
    .card {
        background:#1c1c1c;
        padding:25px;
        border-radius:16px;
        box-shadow:0 0 50px rgba(255,215,0,0.15);
        margin-bottom:30px;
        transition: transform 0.2s;
    }
    .card:hover {transform: scale(1.02);}
    h1,h2,h3 {
        color:#ffd700;
    }
    .metric {
        color:#ccc;
        font-size:14px;
    }
    .logout-btn {text-align:right; margin-bottom:20px;}
    </style>
    """, unsafe_allow_html=True)

luxury_css()

# ================== HEADER ==================
st.markdown("<h1 style='text-align:center'>THE EMERGING ICONS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#ddd'>India’s Next Generation of Entrepreneurs</p>", unsafe_allow_html=True)
st.divider()

# ================== SIDEBAR ==================
menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Featured Stories", "Submit Story", "Admin Login"]
)

# ================== TODAY FOR EXPIRY CHECK ==================
today = date.today().isoformat()

# ================== HOME ==================
if menu == "Home" and st.session_state["story_id"] is None:
    cursor.execute("""
        SELECT * FROM stories 
        WHERE approved=1 
        AND (expiry_date IS NULL OR expiry_date >= ?) 
        ORDER BY created_at DESC
    """, (today,))
    stories = cursor.fetchall()
    story_to_open = None

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
            story_to_open = s[0]

        st.markdown("</div>", unsafe_allow_html=True)

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
            st.image(story[5], width=500)

        st.write(story[4])
        st.caption(f"❤️ {story[7]}  | 👁 {story[8]}")

        if st.button("❤️ Like Story"):
            cursor.execute("UPDATE stories SET likes = likes + 1 WHERE id=?", (sid,))
            conn.commit()
            st.experimental_rerun()

        if st.button("⬅ Back"):
            st.session_state["story_id"] = None
            st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ================== FEATURED ==================
if menu == "Featured Stories":
    cursor.execute("""
        SELECT * FROM stories 
        WHERE approved=1 AND featured=1 
        AND (expiry_date IS NULL OR expiry_date >= ?) 
        ORDER BY created_at DESC
    """, (today,))
    feats = cursor.fetchall()

    if not feats:
        st.info("No featured stories available yet.")
    else:
        for s in feats:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader(s[2])
            st.write(f"**{s[1]}**")
            st.write(s[4][:300] + "...")
            st.markdown("</div>", unsafe_allow_html=True)

# ================== SUBMIT ==================
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

# ================== ADMIN ==================
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
        # Logout button always visible at top
        st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state["admin_logged_in"] = False
            st.session_state["admin_user"] = None
            st.success("Logged out successfully")
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.info(f"You are logged in as Admin: {st.session_state['admin_user']} ✅")

        # Pending stories with expiry control
        cursor.execute("SELECT * FROM stories WHERE approved=0 ORDER BY created_at DESC")
        pending = cursor.fetchall()

        approve_id = None
        feature_id = None
        expiry_for_story = None

        for s in pending:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader(s[2])
            st.write(f"**{s[1]}**")
            st.text("Set expiry date (optional):")
            expiry_for_story = st.date_input("Expiry Date", min_value=date.today(), key=f"expiry{s[0]}")
            
            col1, col2 = st.columns(2)
            if col1.button("Approve", key=f"a{s[0]}"):
                approve_id = s[0]
            if col2.button("Feature", key=f"f{s[0]}"):
                feature_id = s[0]

            st.markdown("</div>", unsafe_allow_html=True)

        # Apply DB updates
        if approve_id:
            cursor.execute("UPDATE stories SET approved=1, expiry_date=? WHERE id=?", (expiry_for_story.isoformat() if expiry_for_story else None, approve_id))
            conn.commit()
            st.success("Story approved ✅")
            st.experimental_rerun()

        if feature_id:
            cursor.execute("UPDATE stories SET featured=1, expiry_date=? WHERE id=?", (expiry_for_story.isoformat() if expiry_for_story else None, feature_id))
            conn.commit()
            st.success("Story featured ⭐")
            st.experimental_rerun()
