from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.responses import Response
from data.models import UserRead, UserCreate, UserUpdate, PostResponse, PostUpdate
from typing import cast
import logging
import uuid

# from data.db import Post, create_db_and_tables, get_async_session, User, generate_thumbnail
# from data import db
from data.db import Post, User, create_db_and_tables, get_async_session #, generate_thumbnail, get_posts_service
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from src.users import auth_backend, current_active_user, fastapi_users
from src.posts import get_posts_service, update_post_caption_service, delete_post_service, create_post_service


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


@app.post("/posts/create", response_model=PostResponse)
async def create_post(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    # Read file content once at the edge
    file_content = await file.read()
    
    try:
        post = await create_post_service(
            user_id=user.id,
            file_content=file_content,
            file_name=str(file.filename),
            content_type=str(file.content_type),
            caption=caption,
            session=session
        )
        return post

    except ValueError as e:
        # Catch business logic errors (like thumbnail generation failure)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch unexpected or database errors
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")
    

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

@app.get("/post/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    posts_data = await get_posts_service(session, user, post_id=post_id)

    if not posts_data:
        raise HTTPException(status_code=404, detail="Post not found")

    return posts_data[0]  # There should be only one post with the given ID


@app.get("/feed")
async def get_feed(
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)
):
    posts_data = await get_posts_service(session, user)

    return {"posts": posts_data}

@app.put("/post/{post_id}")
async def update_post_caption(
    post_id: str,
    update_data: PostUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info(f"User {user.email} attempting to update caption for post {post_id}")
    
    try:
        post = await update_post_caption_service(
            post_id=post_id,
            new_caption=update_data.caption,
            user_id=user.id,
            session=session
        )
        return {
            "success": True,
            "caption": post.caption
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@app.delete("/post/{post_id}")
async def delete_post(
    post_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info(f"User {user.email} attempting to delete post {post_id}")
    
    try:
        # post_uuid = uuid.UUID(post_id)

        # result = await session.execute(select(Post).where(Post.id == post_uuid))
        # post: Optional[Post] = result.scalars().first()

        await delete_post_service(
            post_id=post_id,
            user_id=user.id,
            session=session
        )
        return {"success": True, "message": "Post deleted successfully"}
    

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)