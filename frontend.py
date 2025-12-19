import streamlit as st
import requests
from streamlit_js_eval import streamlit_js_eval
# import base64
# import urllib.parse

st.set_page_config(page_title="Simple Social", layout="wide")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None


def get_headers():
    """Get authorization headers with token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login_page():
    st.title("🚀 Welcome to Simple Social")

    # Simple form with two buttons
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")

    if email and password:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login", type="primary", use_container_width=True):
                # Login using FastAPI Users JWT endpoint
                login_data = {"username": email, "password": password}
                response = requests.post("http://localhost:8000/auth/jwt/login", data=login_data)

                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.token = token_data["access_token"]

                    # Get user info
                    user_response = requests.get("http://localhost:8000/users/me", headers=get_headers())
                    if user_response.status_code == 200:
                        st.session_state.user = user_response.json()
                        st.rerun()
                    else:
                        st.error("Failed to get user info")
                else:
                    st.error("Invalid email or password!")

        with col2:
            if st.button("Sign Up", type="secondary", use_container_width=True):
                # Register using FastAPI Users
                signup_data = {"email": email, "password": password}
                response = requests.post("http://localhost:8000/auth/register", json=signup_data)

                if response.status_code == 201:
                    st.success("Account created! Click Login now.")
                else:
                    error_detail = response.json().get("detail", "Registration failed")
                    st.error(f"Registration failed: {error_detail}")
    else:
        st.info("Enter your email and password above")


def upload_page_clear_inputs():
    st.rerun()
    # st.session_state.user_input_file = ""
    

def upload_page():
    st.title("📸 Share Something")

    uploaded_file = st.file_uploader("Choose media", key="user_input_file", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm', 'webp'])
    caption = st.text_area("Caption:", key="user_input_caption", placeholder="What's on your mind?")

    if uploaded_file and st.button("Share", type="primary"):
        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"caption": caption}
            response = requests.post("http://localhost:8000/upload", files=files, data=data, headers=get_headers())

            if response.status_code == 200:
                st.success("Posted!")
                st.session_state.user_input_caption = ""
                st.rerun()
            else:
                st.error("Upload failed!")

@st.cache_data
def fetch_thumbnail(post_id):
    print("attempting to fetch thumbnail for post_id: "+post_id)
    url = f"http://localhost:8000/posts/{post_id}/thumbnail"
    resp = requests.get(url)
    return resp.content if resp.status_code == 200 else None


def feed_page():
    st.title("🏠 Feed")

    if st.button("Refresh Feed"):
        st.rerun(scope="app")

    response = requests.get("http://localhost:8000/feed", headers=get_headers())
    if response.status_code == 200:
        posts = response.json()["posts"]

        if not posts:
            st.info("No posts yet! Be the first to share something.")
            return

        for post in posts:
            st.markdown("---")

            # Header with user, date, and delete button (if owner)
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{post['email']}** • {post['created_at'][:10]}")
            with col2:
                if post.get('is_owner', False):
                    if st.button("🗑️", key=f"delete_{post['id']}", help="Delete post"):
                        # Delete the post
                        response = requests.delete(f"http://localhost:8000/post/{post['id']}", headers=get_headers())
                        if response.status_code == 200:
                            st.success("Post deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete post!")

            # Uniform media display with caption overlay
            caption = post.get('caption', '')
            st.markdown(f"***{caption}***")
            if post['file_type'] == 'image':
                # uniform_url = create_transformed_url(post['url'], "", caption)
                # st.image(uniform_url, width=300)
                print("Image file in feed")
                # st.caption(caption)
                thumb_bytes = fetch_thumbnail(post['id'])
                if thumb_bytes:
                    st.image(thumb_bytes)

                # thumbnail_url = f"http://127.0.0.1:8000/posts/{post['id']}/thumbnail"

                # st.markdown(
                #     f'<img src="{thumbnail_url}" alt="Post Image" style="width:200px; border-radius:10px;">',
                #     unsafe_allow_html=True
                # )

            else:
                # For videos: specify only height to maintain aspect ratio + caption overlay
                print("Video filein feed")
                # uniform_video_url = create_transformed_url(post['url'], "w-400,h-200,cm-pad_resize,bg-blurred")
                # st.video(uniform_video_url, width=300)
                st.caption(caption)

            st.markdown("")  # Space between posts
    else:
        st.error("Failed to load feed")


# Main app logic
if st.session_state.user is None:
    login_page()
else:
    # Sidebar navigation
    st.sidebar.title(f"👋 Hi {st.session_state.user['email']}!")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate:", ["🏠 Feed", "📸 Upload"])

    if page == "🏠 Feed":
        feed_page()
    else:
        upload_page()