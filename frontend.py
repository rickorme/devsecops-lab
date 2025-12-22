import streamlit as st
import requests

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


def clear_upload_form():
    # This runs BEFORE the page is redrawn
    # st.session_state.user_input_caption = ""
    # To clear the file uploader, we use a trick: change its key
    st.session_state.file_uploader_key += 1
    st.session_state.upload_success = True
    

def upload_page():
    st.title("📸 Share Something")

    # Initialize a counter to force-reset the file uploader
    if "file_uploader_key" not in st.session_state:
        st.session_state.file_uploader_key = 0
    if "upload_success" not in st.session_state:
        st.session_state.upload_success = False
    
    # 1. We wrap the logic in a function we can call
    uploaded_file = st.file_uploader(
        "Choose media", 
        key=f"file_uploader_{st.session_state.file_uploader_key}",
        type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm', 'webp']
    )
    caption = st.text_area(
        "Caption:", 
        key=f"user_input_caption_{st.session_state.file_uploader_key}", 
        placeholder="What's on your mind?"
    )
    # uploaded_file = st.file_uploader("Choose media", key="user_input_file", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm', 'webp'])
    

    if st.button("Share", type="primary"):
        if not uploaded_file:
            st.error("Please select a file first.")
            return
        
        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"caption": caption}

            try:
                response = requests.post("http://localhost:8000/posts/create", files=files, data=data, headers=get_headers())

                if response.status_code == 200:
                    # 2. INSTEAD of setting state here, we call our clear function 
                    # OR we set the state and then IMMEDIATELY rerun.
                    # The most 'Bulletproof' way in a button block:
                    clear_upload_form()
                    st.rerun()
                else:
                    st.error("Upload failed: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

    # Display success message if we just reran after a successful upload
    if st.session_state.upload_success:
        st.success("Posted!")
        st.session_state.upload_success = False # Reset the flag


@st.cache_data
def fetch_thumbnail(post_id):
    print("Fetching thumbnail for post_id: "+post_id)
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
            post_id = post['id']
    
            # Track edit mode in session state
            if f"editing_{post_id}" not in st.session_state:
                st.session_state[f"editing_{post_id}"] = False

            # Header with user, date, and delete button (if owner)
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{post['email']}** • {post['created_at'][:10]}")

                if post.get('is_owner', False):
                    # Check if we are currently editing this specific post
                    if not st.session_state[f"editing_{post_id}"]:
                        if st.button("Edit", key=f"edit_btn_{post_id}"):
                            st.session_state[f"editing_{post_id}"] = True
                            st.rerun()
                    else:
                        # WE ARE IN EDIT MODE
                        new_caption = st.text_input(
                            "New Caption:", 
                            value=post.get('caption', ''), 
                            key=f"input_{post_id}"
                        )
                        
                        edit_col1, edit_col2 = st.columns(2)
                        with edit_col1:
                            if st.button("Save", key=f"save_{post_id}", type="primary"):
                                data = {"caption": new_caption}
                                response = requests.put(
                                    f"http://localhost:8000/post/{post_id}", 
                                    json=data, 
                                    headers=get_headers()
                                )
                                if response.status_code == 200:
                                    st.session_state[f"editing_{post_id}"] = False
                                    st.success("Updated!")
                                    st.rerun()
                                else:
                                    st.error("Failed to update!")
                        
                        with edit_col2:
                            if st.button("Cancel", key=f"cancel_{post_id}"):
                                st.session_state[f"editing_{post_id}"] = False
                                st.rerun()

                    # if st.button(label="Edit", key=f"edit_{post['id']}", help="Edit post caption"):
                    #     logging.info(f"Edit button clicked for post {post['id']}")
                    #     new_caption = st.text_input("New Caption:", value=post.get('caption', ''), key=f"new_caption_{post['id']}")
                        
                    #     if st.button("Save", key=f"save_{post['id']}"):
                    #         # Update the post caption
                    #         print("Save button clicked")
                    #         data = {"caption": new_caption}
                    #         # data = {"caption": "test"}
                    #         # logging.info(f"Updating caption for post {post['id']} to: {new_caption}")
                    #         response = requests.put(f"http://localhost:8000/post/{post['id']}", json=data, headers=get_headers())
                    #         if response.status_code == 200:
                    #             st.success("Caption updated!")
                    #             st.rerun()
                    #         else:
                    #             st.error("Failed to update caption!")

                    #     elif st.button("Cancel", key=f"cancel_{post['id']}"):
                    #         print("Cancel button clicked")
                    #         st.rerun()
                
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
                
                thumb_bytes = fetch_thumbnail(post['id'])
                if thumb_bytes:
                    st.image(thumb_bytes)

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

    if st.sidebar.button(label="Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate:", ["🏠 Feed", "📸 Upload"])

    if page == "🏠 Feed":
        feed_page()
    else:
        upload_page()