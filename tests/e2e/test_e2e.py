import pytest
import re
import os
from playwright.sync_api import Page, expect

BASE_URL = os.getenv("BASE_URL", "http://localhost:8501")


# --- 1. Define the Page Object ---
class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.sidebar = Sidebar(page)

        # Define the locators here, attached to self
        self.header = page.get_by_role("heading", name="🚀 Welcome to Simple Social")
        self.login_username = page.get_by_role("textbox", name="Email:")
        self.login_password = page.get_by_role("textbox", name="Password:")
        self.login_button = page.get_by_test_id("stBaseButton-primary")
        self.login_failed_msg = page.get_by_text("Invalid email or password!")
        self.signup_button = page.get_by_test_id("stBaseButton-secondary")
        self.signup_failed_msg = page.get_by_text("Registration failed:")
        self.signup_success_msg = page.get_by_text("Account created! Click Login")

    def navigate(self):
        self.page.goto(BASE_URL)

    def login(self, username, password):
        """Performs the full login workflow"""
        self.login_username.click
        self.login_username.fill(username)
        self.login_password.click
        self.login_password.fill(password)
        self.login_password.press("Tab")
        self.login_button.click()

    def signup(self, username, password):
        """Performs the full login workflow"""
        self.login_username.click
        self.login_username.fill(username)
        self.login_username.press("Tab")
        self.login_password.fill(password)
        self.login_password.press("Tab")
        self.signup_button.click()

class FeedPage:
    def __init__(self, page: Page):
        self.page = page
        self.sidebar = Sidebar(page)

        # Define the locators here, attached to self
        self.feed_title = page.get_by_role("heading", name="🏠 Feed")
        self.first_post_email = page.get_by_test_id("stMainBlockContainer").get_by_role("link", name="teste2e_user2@example.com")
        self.first_delete_button = page.get_by_test_id("stTooltipIcon").get_by_test_id("stBaseButton-secondary").first
        self.edit_button = page.get_by_role("button", name="Edit").first
        self.first_caption = page.get_by_role("paragraph").first
        self.logout_button = page.get_by_role("button", name="Logout")
        self.caption_edit_input = page.get_by_role("textbox", name="New Caption:")
        self.caption_edit_save_button = page.get_by_test_id("stBaseButton-primary")

    def navigate(self):
        self.page.goto(BASE_URL)

class UploadPage:
    def __init__(self, page: Page):
        self.page = page
        self.sidebar = Sidebar(page)

        # Define the locators here, attached to self
        self.upload_title = page.get_by_role("heading", name="📸 Share Something")
        self.dropzone = page.get_by_test_id("stFileUploaderDropzone")
        self.browse_button = self.dropzone.get_by_test_id("stBaseButton-secondary")
        #self.file_uploader_input = page.get_by_test_id("stFileUploaderDropzone").locator("input[type='file']")
        self.caption_input = page.get_by_role("textbox", name="Caption:")
        self.share_button = page.get_by_test_id("stBaseButton-primary")
        self.upload_success_msg = page.get_by_text("Posted!")
        self.upload_failed_msg = page.get_by_test_id("stFileUploaderFileErrorMessage")

    def navigate(self):
        self.page.goto(BASE_URL)        

    def upload_file(self, file_path, caption):
        """Uploads a file with the given caption"""
        # 1. Start listening for the popup event
        with self.page.expect_file_chooser() as fc_info:
            # 2. Click the visible "Browse files" button
            self.browse_button.click()

        # 3. The popup is caught in 'fc_info'. Now set the files.
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)

        # Fill caption and submit
        self.caption_input.fill(caption)
        self.share_button.click()


class Sidebar:
    def __init__(self, page: Page):
        self.page = page

        # Define sidebar-specific locators here
        self.logout_button = page.get_by_test_id("stSidebarUserContent").get_by_test_id("stBaseButton-secondary")
        self.feed_nav = page.get_by_test_id("stRadio").get_by_text("🏠 Feed")
        self.upload_nav = page.get_by_test_id("stRadio").get_by_text("📸 Upload")
        self.sidebar_area = page.get_by_test_id("stSidebarContent")

    def go_to_feed(self):
        self.feed_nav.click()

    def go_to_upload(self):
        self.upload_nav.click()

    def logout(self):
        self.logout_button.click()

    def navigate(self):
        self.page.goto(BASE_URL)            

# Test Data
TEST_USER = "test_e2e_user@example.com"
TEST_PASS = "1234"
BAD_USER = "-99"
BAD_PASS = "wrongpassword"
VALID_IMAGE_FILE_1 = "./tests/e2e/howl.jpeg"
CAPTION_IMAGE_FILE_1 = "Howling wolf!"
VALID_IMAGE_FILE_2 = "./tests/e2e/forest-bathing.webp"
CAPTION_IMAGE_FILE_2 = "Forest Bathing"
CAPTION_IMAGE_FILE_2_1 = "Forest Bathing: woman leaning back against a tree with eyes half-closed"
INVALID_UPLOAD_FILE = "./tests/e2e/invalidfile.txt"
IMAGE_TO_DELETE = "./tests/e2e/arty-stairs.webp"
CAPTION_TO_DELETE = "Artistic staircase with man looking up"

def test_login_page_structure(page: Page):
    # Initialize the object with the current page
    login = LoginPage(page)
    
    login.navigate()
    
    # Check expected elements are visible
    expect(login.header).to_be_visible()
    expect(login.login_username).to_be_visible()
    expect(login.login_password).to_be_visible()

def test_signup_sucess(page: Page):
    # Initialize the object with the current page
    login = LoginPage(page)
    
    login.navigate()

    login.signup(TEST_USER,TEST_PASS)

    expect(login.signup_success_msg).to_be_visible()

def test_signup_fail(page: Page):
    # Initialize the object with the current page
    login = LoginPage(page)
    
    login.navigate()

    login.signup(BAD_USER,TEST_PASS)

    expect(login.signup_failed_msg).to_be_visible()

def test_login_failed(page: Page):
    # Initialize the object with the current page
    login = LoginPage(page)
    
    login.navigate()

    login.login(TEST_USER, BAD_PASS)

    expect(login.login_failed_msg).to_be_visible()    

def test_login_sucess(page: Page):
    # Initialize the object with the current page
    login = LoginPage(page)
    
    login.navigate()

    login.login(TEST_USER, TEST_PASS)

    expect(login.sidebar.sidebar_area).to_be_visible()

def test_upload_page_structure(page: Page):
    # Initialize the object with the current page
    login = LoginPage(page)
    upload = UploadPage(page)
    
    login.navigate()
    login.login(TEST_USER, TEST_PASS)

    # Navigate to Upload Page
    login.sidebar.go_to_upload()
    expect(upload.upload_title).to_be_visible()
    expect(upload.dropzone).to_be_visible()
    expect(upload.browse_button).to_be_visible()
    expect(upload.caption_input).to_be_visible()
    expect(upload.share_button).to_be_visible()

def test_upload_post_success(page: Page):
    # Initialize the object with the current page
    login = LoginPage(page)
    upload = UploadPage(page)
    
    login.navigate()
    login.login(TEST_USER, TEST_PASS)

    # Navigate to Upload Page
    login.sidebar.go_to_upload()
    expect(upload.upload_title).to_be_visible()

    # Upload a file
    upload.upload_file(VALID_IMAGE_FILE_1, CAPTION_IMAGE_FILE_1)

    # Verify success message
    expect(upload.upload_success_msg).to_be_visible()  


def test_upload_post_fail(page: Page):
    # Initialize the object with the current page
    login = LoginPage(page)
    upload = UploadPage(page)
    
    login.navigate()
    login.login(TEST_USER, TEST_PASS)

    # Navigate to Upload Page
    login.sidebar.go_to_upload()
    expect(upload.upload_title).to_be_visible()

    # Upload a file
    upload.upload_file(INVALID_UPLOAD_FILE, CAPTION_IMAGE_FILE_1)

    # Verify error message
    expect(upload.upload_failed_msg).to_be_visible() 

def test_upload_and_edit_flow(page: Page):
    # Initialize the object with the current page
    login = LoginPage(page)
    upload = UploadPage(page)
    feed = FeedPage(page)
    
    login.navigate()
    login.login(TEST_USER, TEST_PASS)

    # Navigate to Upload Page
    login.sidebar.go_to_upload()
    expect(upload.upload_title).to_be_visible()

    # Upload a file
    upload.upload_file(VALID_IMAGE_FILE_2, CAPTION_IMAGE_FILE_2)

    # Verify success message
    expect(upload.upload_success_msg).to_be_visible()  

    # Navigate to Feed Page
    login.sidebar.go_to_feed()
    expect(feed.feed_title).to_be_visible()

    # Edit the post
    feed.edit_button.click()
    expect(feed.caption_edit_input).to_be_visible()

    feed.caption_edit_input.fill(CAPTION_IMAGE_FILE_2_1)
    feed.caption_edit_save_button.click()

    expect(page.get_by_role("paragraph").filter(has_text=CAPTION_IMAGE_FILE_2_1)).to_be_visible()


def test_delete_post_flow(page: Page):
    # Initialize the object with the current page
    login = LoginPage(page)
    feed = FeedPage(page)
    upload = UploadPage(page)
    
    login.navigate()
    login.login(TEST_USER, TEST_PASS)

    # Upload a file to ensure there is at least one post
    feed.sidebar.go_to_upload()
    upload.upload_file(IMAGE_TO_DELETE, CAPTION_TO_DELETE)

    # Navigate to Feed Page
    login.sidebar.go_to_feed()
    expect(feed.feed_title).to_be_visible()

    new_post_caption = page.get_by_text(CAPTION_TO_DELETE)
    expect(new_post_caption).to_be_visible()

    # Delete the first post
    feed.first_delete_button.click()

    # Verify the first post is no longer visible
    expect(new_post_caption).not_to_be_visible()



