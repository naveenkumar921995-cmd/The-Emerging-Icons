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
    background: linear-gradient(160deg, #0b0b0b, #1c1c1c);
    color:#fff; font-family:'Merriweather', serif;
}
h1,h2,h3 { color:#ffd700; text-shadow: 0px 0px 10px rgba(255,215,0,0.7); }

.card {
    background:#1a1a1a; 
    padding:25px; 
    border-radius:20px; 
    box-shadow:0 0 60px rgba(255,215,0,0.15); 
    margin-bottom:30px; 
    transition: transform 0.5s ease, box-shadow 0.5s ease;
    position:relative;
    overflow:hidden;
}
.card::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
    transform: rotate(45deg) scale(0);
    opacity:0;
    transition: all 0.6s ease;
}
.card:hover::after {
    transform: rotate(45deg) scale(1);
    opacity:1;
}
.card:hover {
    transform: translateY(-12px) scale(1.03);
    box-shadow:0 0 120px rgba(255,215,0,0.5);
}
.featured-card {
    min-width:320px; flex:0 0 auto; background:#222; border-radius:16px; padding:20px; 
    box-shadow:0 0 40px rgba(255,215,0,0.2); transition: transform 0.3s ease;
}
.featured-card:hover { transform: translateY(-8px) scale(1.05); box-shadow:0 0 90px rgba(255,215,0,0.6);}
.featured-carousel { display:flex; overflow-x:auto; gap:25px; padding:20px 0; scroll-behavior: smooth; }
.counter { font-size:1.2rem; font-weight:bold; color:#ffd700; }
.logout-btn { background-color:#ffd700; color:#0b0b0b; font-weight:bold; border-radius:12px; padding:5px 15px; float:right; margin-top:-50px; cursor:pointer; }
::-webkit-scrollbar { height:8px; }
::-webkit-scrollbar-thumb { background:#ffd700; border-radius:4px; }
</style>
"""
st.markdown(luxury_style, unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("<h1 style='text-align:center; font-size:3rem;'>THE EMERGING ICONS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:1.2rem; color:#aaa;'>India’s Next Generation of Entrepreneurs</p>", unsafe_allow_html=True)
st.divider()

# ================= SIDEBAR =================
menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Featured Stories", "Submit Story", "Admin Login"]
)
today_str = date.today().isoformat()

# ================= HOME =================
if menu == "Home":
    # Featured Carousel
    cursor.execute("SELECT * FROM stories WHERE approved=1 AND featured=1 AND (expiry_date IS NULL OR expiry_date>=?) ORDER BY created_at DESC", (today_str,))
    featured = cursor.fetchall()
    if featured:
        st.markdown("<h2 style='color:#ffd700;'>⭐ Featured Entrepreneurs</h2>", unsafe_allow_html=True)
        st.markdown("<div class='featured-carousel'>", unsafe_allow_html=True)
        for f in featured:
            img_html = f"<img src='{f[5]}' width='100%' style='border-radius:12px; margin-bottom:10px;'/>" if f[5] else ""
            card_html = f"""
            <div class='featured-card'>
                {img_html}
                <h3>{f[2]}</h3>
                <p><b>{f[1]}</b></p>
                <p>{f[4][:120]}...</p>
                <p class='counter'>❤️ {f[7]}  | 👁 {f[8]}</p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Main Stories
    cursor.execute("SELECT * FROM stories WHERE approved=1 AND (expiry_date IS NULL OR expiry_date>=?) AND featured=0 ORDER BY created_at DESC", (today_str,))
    stories = cursor.fetchall()
    for s in stories:
        cursor.execute("UPDATE stories SET views=views+1 WHERE id=?", (s[0],))
        conn.commit()
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col1, col2 = st.columns([1,3])
        if s[5] and os.path.exists(s[5]):
            col1.image(s[5], width=220)
        col2.subheader(s[2])
        col2.write(f"**{s[1]}**")
        col2.write(s[4][:280]+"...")
        col2.markdown(f"<p class='counter'>❤️ {s[7]}  | 👁 {s[8]}</p>", unsafe_allow_html=True)
        if col2.button("Read Full Story", key=f"read{s[0]}"):
            st.session_state["story_id"] = s[0]
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ================= FULL STORY MODAL =================
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
        cursor.execute("UPDATE stories SET likes = likes + 1 WHERE id=?", (sid,))
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

# ================= ADMIN PANEL =================
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
        if st.button("Logout", key="logout"):
            del st.session_state["admin"]
            st.experimental_rerun()

        # Pending stories with expiry date
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
                st.experimental_rerun()
            if st.button("Feature", key=f"feature_{s[0]}"):
                cursor.execute("UPDATE stories SET featured=1 WHERE id=?", (s[0],))
                conn.commit()
                st.success(f"Story '{s[2]}' featured ⭐")
                st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)
