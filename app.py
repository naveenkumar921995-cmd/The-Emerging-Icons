import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime, date
from PIL import Image

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

# ================= ULTRA LUXURY CSS =================
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
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover { transform: translateY(-10px); box-shadow:0 0 100px rgba(255,215,0,0.4); }

.logout-btn {
    background-color:#ffd700; color:#0b0b0b; font-weight:bold; border-radius:12px; padding:5px 15px;
    float:right; margin-top:-50px; cursor:pointer;
}

.featured-carousel {
    display:flex; overflow-x:auto; gap:25px; padding:20px 0; scroll-behavior: smooth;
}
.featured-card {
    min-width:320px; flex:0 0 auto; background:#222; border-radius:16px; padding:20px; 
    box-shadow:0 0 40px rgba(255,215,0,0.2); transition: transform 0.3s ease;
}
.featured-card:hover { transform: translateY(-8px); box-shadow:0 0 70px rgba(255,215,0,0.5);}
.counter { font-size:1.2rem; font-weight:bold; color:#ffd700; }
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

# ================= SAMPLE STORIES =================
# Add sample entrepreneurs if table is empty
cursor.execute("SELECT COUNT(*) FROM stories")
if cursor.fetchone()[0] == 0:
    placeholder_img = "images/placeholder.png"
    sample_stories = [
        {
            "name":"Rohit Sharma",
            "title":"Revolutionizing E-commerce in India",
            "profile":"Serial entrepreneur in e-commerce and retail",
            "story":"Rohit started his journey by launching small online stores and quickly scaled to a nationwide platform. His innovative marketing techniques and focus on customer satisfaction have set new benchmarks in the industry.",
            "image": placeholder_img,
            "featured":1
        },
        {
            "name":"Anita Desai",
            "title":"Sustainable Fashion Pioneer",
            "profile":"Founder of eco-friendly clothing line",
            "story":"Anita combines sustainability with style, creating a fashion brand loved by young professionals. Her dedication to eco-conscious production is inspiring the next generation of designers.",
            "image": placeholder_img,
            "featured":1
        },
        {
            "name":"Sumit Bhardwaj",
            "title":"Leader in Project & Facility Management",
            "profile":"Senior Manager at DLF Limited",
            "story":"With 15+ years in project execution and facility management, Sumit ensures operations run efficiently, from HVAC to electrical systems, mentoring teams to exceed performance standards.",
            "image": placeholder_img,
            "featured":0
        },
        {
            "name":"Priya Verma",
            "title":"AI Startup Founder",
            "profile":"Innovator in AI-driven analytics",
            "story":"Priya's startup provides AI solutions for medium businesses. Her work is transforming how companies leverage data for strategic decisions.",
            "image": placeholder_img,
            "featured":0
        },
        {
            "name":"Arjun Mehta",
            "title":"Green Energy Entrepreneur",
            "profile":"CEO of SolarTech Solutions",
            "story":"Arjun leads initiatives in solar energy deployment, creating affordable and scalable renewable energy solutions for communities across India.",
            "image": placeholder_img,
            "featured":0
        }
    ]
    for s in sample_stories:
        cursor.execute("""
            INSERT INTO stories (name,title,profile,story,image,featured,approved,created_at)
            VALUES (?,?,?,?,?,?,1,?)
        """, (s["name"], s["title"], s["profile"], s["story"], s["image"], s["featured"], datetime.now().isoformat()))
    conn.commit()

# ================= HOME =================
if menu == "Home":
    # Featured Carousel
    cursor.execute("SELECT * FROM stories WHERE approved=1 AND featured=1 AND (expiry_date IS NULL OR expiry_date>=?) ORDER BY created_at DESC", (today_str,))
    featured = cursor.fetchall()
    if featured:
        st.markdown("<h2 style='color:#ffd700;'>⭐ Featured Entrepreneurs</h2>", unsafe_allow_html=True)
        st.markdown("<div class='featured-carousel'>", unsafe_allow_html=True)
        for f in featured:
            img_path = f[5] if f[5] and os.path.exists(f[5]) else "images/placeholder.png"
            img_html = f"<img src='{img_path}' width='100%' style='border-radius:12px; margin-bottom:10px;'/>"
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
        img_path = s[5] if s[5] and os.path.exists(s[5]) else "images/placeholder.png"
        col1.image(img_path, width=220)
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
    img_path = story[5] if story[5] and os.path.exists(story[5]) else "images/placeholder.png"
    st.image(img_path, width=500)
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

# ================= ADMIN =================
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
