import pytest
import uuid
import io
from PIL import Image

# Import your module functions and models
from src.posts import (
    generate_thumbnail, 
    create_post_service, 
    update_post_caption_service,
    delete_post_service
)
from data.db import Post

# --- 1. Testing Pure Functions ---

def test_generate_thumbnail_success():
    # Create a dummy red image
    img = Image.new('RGB', (600, 600), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    content = img_bytes.getvalue()

    thumb = generate_thumbnail(content)
    
    assert thumb is not None
    # Verify it is actually an image and resized
    thumb_img = Image.open(io.BytesIO(thumb))
    assert thumb_img.size[0] <= 300
    assert thumb_img.size[1] <= 300

def test_generate_thumbnail_invalid_data():
    # Passing random non-image bytes
    assert generate_thumbnail(b"not an image") is None


# --- 2. Service Logic Tests (Using Mocking) ---
@pytest.mark.asyncio
async def test_create_post_database_integration(db_session, test_user):
    # 1. Prepare dummy image
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    
    # 2. Call service with REAL (in-memory) database session
    post = await create_post_service(
        user_id=test_user.id,
        file_content=img_bytes.getvalue(),
        file_name="ocean.jpg",
        content_type="image/jpeg",
        caption="Beautiful blue",
        session=db_session
    )

    # 3. Assertions (The data is actually in the DB now!)
    assert post.id is not None
    assert post.user_id == test_user.id
    assert getattr(post, "caption") == "Beautiful blue"
    assert getattr(post, "file_type") == "image"
    assert post.thumbnail_content is not None


@pytest.mark.asyncio
async def test_update_post_caption_unauthorized(db_session, test_user):
    
    # 1. Create a "attacker" user
    attacker_id = uuid.uuid4() # Different ID
    
    # 2. Create a post belonging to the 'test_user' from our fixture
    # We manually add it to the DB so we have a target for the attack
    owned_post = Post(
        id=uuid.uuid4(),
        user_id=test_user.id,
        caption="Original Caption",
        file_type="image"
    )
    db_session.add(owned_post)
    await db_session.commit()

    # 3. Attempt to update this post using the 'attacker_id'
    with pytest.raises(PermissionError, match="not authorized"):
        await update_post_caption_service(
            post_id=str(owned_post.id),
            new_caption="New",
            user_id=attacker_id,
            session=db_session
        )

@pytest.mark.asyncio
async def test_delete_post_not_found(db_session, test_user):
    # Generate a random UUID that definitely isn't in our empty test DB
    random_id = str(uuid.uuid4())

    with pytest.raises(ValueError, match="Post not found"):
        await delete_post_service(
            post_id=random_id,
            user_id=test_user.id,
            session=db_session
        )