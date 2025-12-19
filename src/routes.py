from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.responses import Response
from data.models import UserRead, UserCreate, UserUpdate, PostResponse
from typing import Optional, cast
import logging
import uuid

# from data.db import Post, create_db_and_tables, get_async_session, User, generate_thumbnail
# from data import db
from data.db import Post, User, create_db_and_tables, get_async_session #, generate_thumbnail, get_posts
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select

from data.users import auth_backend, current_active_user, fastapi_users
from data.posts import get_posts, generate_thumbnail


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


@app.post("/upload", response_model=PostResponse)
async def upload_file(
        file: UploadFile = File(...),
        caption: str = Form(""),
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)
):
    
    file_content = await file.read()
    logging.info(f"Received file upload: {file.filename} of type {file.content_type} from user {user.email}")
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
        logging.info(f"User {user.email} uploaded a new post with id {post.id}")
        await session.commit()
        logging.info(f"Post {post.id} committed to database")
        await session.refresh(post)
        logging.info(f"Post {post.id} refreshed from database")
        return post
    
    except Exception as e:
        # Handle database errors
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        # The file stream is already closed by `await file.read()`
        pass # No need for cleanup of temp files  

@app.get("/posts/{post_id}/file")
async def get_post_file(post_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    # Assuming you have a way to fetch the Post by ID
    post_uuid = cast(uuid, post_id)
    post = await session.get(Post, post_uuid)
    
    if not post or post.file_content is None:
        raise HTTPException(status_code=404, detail="File not found")

    media_type = cast(str, post.content_type)

    return Response(content=post.file_content, media_type=media_type)

@app.get("/posts/{post_id}/thumbnail")
async def get_post_thumbnail(post_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        # 1. Physically convert the string to a UUID object
        post_uuid = uuid.UUID(post_id) 
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    post = await session.get(Post, post_uuid)
    
    if not post or post.thumbnail_content is None:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
        
    # Thumbnails were saved as JPEG
    return Response(content=post.thumbnail_content, media_type="image/jpeg")


@app.get("/feed")
async def get_feed(
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)
):
    posts_data = await get_posts(session, user)

    return {"posts": posts_data}


@app.delete("/post/{post_id}")
async def delete_post(
        post_id: str,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info(f"User {user.email} attempting to delete post {post_id}")
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