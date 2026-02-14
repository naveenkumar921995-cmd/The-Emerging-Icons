import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime, date

# ================= CONFIG =================
st.set_page_config(
    page_title="The Emerging Icons",
    page_icon="⭐",
    layout="wide"
)

# ================= DB SETUP =================
os.makedirs("images", exist_ok=True)
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables
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

# Default admin
cursor.execute("SELECT * FROM admin")
if not cursor.fetchone():
    password = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute("INSERT INTO admin VALUES (?,?)", ("admin", password))
    conn.commit()

# ================= FUNCTIONS =================
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def admin_login(user, pw):
    cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (user, hash_password(pw)))
    return cursor.fetchone()

# ================= ULTRA PREMIUM CSS =================
luxury_style = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;700&display=swap');

body {
    background: #f5f5f5; /* Light soft premium background */
    color:#333; 
    font-family:'Merriweather', serif;
}

h1,h2,h3 { 
    color:#bfa33f; /* Subtle gold */
    text-shadow: 0px 0px 6px rgba(191,163,63,0.8); 
}

.card {
    background:#ffffff; 
    padding:25px; 
    border-radius:16px; 
    box-shadow:0 10px 30px rgba(191,163,63,0.2); 
    margin-bottom:30px; 
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover { 
    transform: translateY(-8px); 
    box-shadow:0 15px 50px rgba(191,163,63,0.3); 
}

.logout-btn {
    background-color:#bfa33f; 
    color:#fff; 
    font-weight:bold; 
    border-radius:12px; 
    padding:5px 15px;
    float:right; 
    margin-top:-50px; 
    cursor:pointer;
}

.featured-carousel {
    display:flex; 
    overflow-x:auto; 
    gap:25px; 
    padding:20px 0; 
    scroll-behavior: smooth;
}

.featured-card {
    min-width:320px; 
    flex:0 0 auto; 
    background:#fafafa; 
    border-radius:16px; 
    padding:20px; 
    box-shadow:0 5px 25px rgba(191,163,63,0.2); 
    transition: transform 0.3s ease;
}
.featured-card:hover { 
    transform: translateY(-5px); 
    box-shadow:0 10px 40px rgba(191,163,63,0.3);
}

.counter { 
    font-size:1.2rem; 
    font-weight:bold; 
    color:#bfa33f; 
}

p, span, label, td {
    color:#333; /* Ensure all text is readable */
}
</style>
"""
st.markdown(luxury_style, unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("<h1 style='text-align:center; font-size:3rem;'>THE EMERGING ICONS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:1.2rem; color:#ccc;'>India’s Next Generation of Entrepreneurs</p>", unsafe_allow_html=True)
st.divider()

# ================= SIDEBAR =================
menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Featured Stories", "Submit Story", "Admin Login"]
)

today_str = date.today().isoformat()

# ================= SAMPLE STORIES INSERTION =================
cursor.execute("SELECT COUNT(*) FROM stories")
if cursor.fetchone()[0] == 0:
    sample_data = [
        ("Elon Musk", "SpaceX Visionary", "Founder & CEO of SpaceX & Tesla", 
         "Elon Musk is transforming space and transportation...", "images/elon_musk.jpg", 1),
        ("Sundar Pichai", "Tech Leader", "CEO of Alphabet & Google", 
         "Sundar Pichai has led Google through multiple innovations...", "images/sundar_pichai.jpg", 1),
        ("Riya Aziz", "Emerging Entrepreneur", "Co-founder of FinTech Startup", 
         "Riya is making waves in the Indian fintech ecosystem...", "images/riya_aziz.jpg", 0),
        ("Vikram Jain", "Growth Hacker", "Founder of SaaS Startup", 
         "Vikram's SaaS platform is disrupting traditional markets...", "images/vikram_jain.jpg", 0),
        ("Priya Sharma", "Innovator", "Social Entrepreneur", 
         "Priya works to create sustainable impact through tech...", "images/priya_sharma.jpg", 0)
    ]
    for s in sample_data:
        cursor.execute("""
            INSERT INTO stories (name,title,profile,story,image,featured,approved,created_at)
            VALUES (?,?,?,?,?,?,1,?)
        """, (*s, datetime.now().isoformat()))
    conn.commit()

# ================= HOME =================
if menu == "Home":
    cursor.execute("SELECT * FROM stories WHERE approved=1 AND (expiry_date IS NULL OR expiry_date>=?) ORDER BY created_at DESC", (today_str,))
    stories = cursor.fetchall()
    if stories:
        for s in stories:
            try:
                cursor.execute("UPDATE stories SET views=views+1 WHERE id=?", (s[0],))
                conn.commit()
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                col1, col2 = st.columns([1,3])
                if s[5] and os.path.exists(s[5]):
                    col1.image(s[5], width=220)
                col2.subheader(s[2])
                col2.write(f"**{s[1]}**")
                col2.write(f"<span class='text-light'>{s[4][:280]}...</span>", unsafe_allow_html=True)
                col2.markdown(f"<p class='counter'>❤️ {s[7]}  | 👁 {s[8]}</p>", unsafe_allow_html=True)
                if col2.button("Read Full Story", key=f"read{s[0]}"):
                    st.session_state["story_id"] = s[0]
            except Exception as e:
                st.error(f"Error displaying story '{s[1]}': {e}")
            st.markdown("</div>", unsafe_allow_html=True)

# ================= FULL STORY =================
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
    st.markdown(f"<p class='counter'>❤️ {story[7]}  | 👁 {story[8]}</p>", unsafe_allow_html=True)
    if st.button("❤️ Like Story"):
        cursor.execute("UPDATE stories SET likes=likes+1 WHERE id=?", (sid,))
        conn.commit()
        st.experimental_rerun()
    if st.button("⬅ Back"):
        del st.session_state["story_id"]
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ================= SUBMIT STORY =================
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
            """, (name,title,profile,story,img_path,datetime.now().isoformat()))
            conn.commit()
            st.success("Story submitted for admin approval.")

# ================= ADMIN =================
if menu == "Admin Login":
    st.subheader("Admin Panel")
    if "admin" not in st.session_state:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if admin_login(user,pw):
                st.session_state["admin"] = True
            else:
                st.error("Invalid credentials")
    else:
        if st.button("Logout"):
            del st.session_state["admin"]
        # Pending stories
        cursor.execute("SELECT * FROM stories WHERE approved=0")
        pending = cursor.fetchall()
        for s in pending:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader(s[2])
            st.write(s[1])
            expiry = st.date_input("Set expiry date", value=date.today(), key=f"expiry_{s[0]}")
            if st.button("Approve", key=f"approve_{s[0]}"):
                cursor.execute("UPDATE stories SET approved=1, expiry_date=? WHERE id=?", (expiry.isoformat(), s[0]))
                conn.commit()
                st.success(f"Story '{s[2]}' approved ✅")
            if st.button("Feature", key=f"feature_{s[0]}"):
                cursor.execute("UPDATE stories SET featured=1 WHERE id=?", (s[0],))
                conn.commit()
                st.success(f"Story '{s[2]}' featured ⭐")
            st.markdown("</div>", unsafe_allow_html=True)


