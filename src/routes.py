from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from data.models import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from data.models import PostCreate, PostResponse
from typing import Optional
import logging
import uuid

from data.db import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select

from data.users import auth_backend, current_active_user, fastapi_users

import io
from PIL import Image

# config for thumbnails
THUMBNAIL_SIZE = (300, 300)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("creating db and tables")
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])


def generate_thumbnail(file_content: bytes) -> bytes | None:
    try:
        # Use io.BytesIO to treat the byte content as a file
        image = Image.open(io.BytesIO(file_content))
        image.thumbnail(THUMBNAIL_SIZE)

        # Save the thumbnail to a new bytes buffer
        thumb_buffer = io.BytesIO()
        image.save(thumb_buffer, format="JPEG")
        return thumb_buffer.getvalue()

    except Exception as e:
        logging.error(f"Error generating thumbnail: {e}")
        return None

@app.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        caption: str = Form(""),
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)
):
    
    file_content = await file.read()
    print(file.content_type)
    slash_pos = str(file.content_type).find('/')
    file_type = str(file.content_type)[0:slash_pos]

    thumbnail_content = None
    if file_type == "image":
        # 2. Generate thumbnail for images
        # The image manipulation is done "on the fly" right here during upload.
        thumbnail_content = generate_thumbnail(file_content)
        if thumbnail_content is None:
             raise HTTPException(status_code=400, detail="Could not process image file.")

    try:
        post = Post(
            user_id=user.id,
            caption=caption,
            file_type=file_type,
            file_content=file_content,
            thumbnail_content=thumbnail_content,
            file_name=file.filename,
            content_type=file.content_type
        )      
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post
    
    except Exception as e:
        # Handle database errors
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        # The file stream is already closed by `await file.read()`
        pass # No need for cleanup of temp files  


@app.get("/feed")
async def get_feed(
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    # Get users for email lookup
    users_result = await session.execute(select(User))
    users = [row[0] for row in users_result.all()]
    user_dict = {u.id: u.email for u in users}

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": user_dict.get(post.user_id, "unknown")
            }
        )

    return {"posts": posts_data}

@app.delete("/post/{post_id}")
async def delete_post(
        post_id: str,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post: Optional[Post] = result.scalars().first()

        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if str(post.user_id) != str(user.id):
            raise HTTPException(status_code=403, detail="You are not authorized to delete this post")

        await session.delete(post)
        await session.commit()
        return {"success": True, "message": "Post deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)