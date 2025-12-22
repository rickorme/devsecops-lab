from src.users import current_active_user, get_users_dict
from data.db import Post, User
from data.models import PostUpdate
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends


import logging
import io
from PIL import Image
import uuid


# config for thumbnails
THUMBNAIL_SIZE = (300, 300)

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
    
async def create_post_service(
    user_id: uuid.UUID, 
    file_content: bytes,
    file_name: str,
    content_type: str,
    caption: str,
    session: AsyncSession
) -> Post:
    """
    Handles the logic for processing an upload and saving it to the database.
    """
    # 1. Determine file type
    slash_pos = content_type.find('/')
    file_type = content_type[0:slash_pos] if slash_pos != -1 else "unknown"

    # 2. Process image logic
    thumbnail_content = None
    if file_type == "image":
        thumbnail_content = generate_thumbnail(file_content)
        if thumbnail_content is None:
            # We raise a ValueError so the API layer can catch it and return a 400
            raise ValueError("Could not process image file.")

    # 3. Database operations
    try:
        post = Post(
            user_id=user_id,
            caption=caption,
            file_type=file_type,
            file_content=file_content,
            thumbnail_content=thumbnail_content,
            file_name=file_name,
            content_type=content_type
        )      
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post
    except Exception as e:
        logging.error(f"Database error during post creation: {e}")
        await session.rollback()
        raise e

async def get_posts_service(
    session: AsyncSession,
    user: User = Depends(current_active_user),
    post_id: Optional[str] = None
):
    # 1. Build the base query
    query = select(Post).order_by(Post.created_at.desc())

    # 2. If post_id is provided, filter the query
    if post_id:
        try:
            post_uuid = uuid.UUID(post_id)
            query = query.where(Post.id == post_uuid)
        except ValueError:
            return [] # Or raise an error if the UUID format is invalid

    result = await session.execute(query)
    posts = result.scalars().all()
    
    # result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    # posts = [row[0] for row in result.all()]
    
    users_dict = await get_users_dict(session)

    posts_data = []
    for post in posts:
        posts_data.append({
            "id": str(post.id),
            "user_id": str(post.user_id),
            "caption": post.caption,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "content_type": post.content_type,
            "created_at": post.created_at.isoformat(),
            "is_owner": post.user_id == user.id,
            "email": users_dict.get(post.user_id, "unknown")
        })
    return posts_data  


async def update_post_caption_service(
    post_id: str, 
    new_caption: str, 
    user_id: uuid.UUID, 
    session: AsyncSession
):
    """
    Handles the business logic for updating a post caption.
    Returns the updated post or raises a ValueError for specific business logic failures.
    """
    post_uuid = uuid.UUID(post_id)
    
    result = await session.execute(select(Post).where(Post.id == post_uuid))
    post: Optional[Post] = result.scalars().first()

    if post is None:
        raise ValueError("Post not found")
    
    if str(post.user_id) != user_id:
        raise PermissionError("You are not authorized to edit this post")

    post.caption = new_caption # type: ignore
    session.add(post)
    await session.commit()
    await session.refresh(post)
    
    return post   


async def delete_post_service(
    post_id: str, 
    user_id: uuid.UUID, 
    session: AsyncSession
):    
    """
    Handles the business logic for deleting a post.
    """
    post_uuid = uuid.UUID(post_id) 

    result = await session.execute(select(Post).where(Post.id == post_uuid))
    post: Optional[Post] = result.scalars().first()

    if post is None:
        raise ValueError("Post not found")
    
    if str(post.user_id) != str(user_id):
        logging.warning(f"User {user_id} attempted to delete post {post_id} belonging to user {post.user_id} without permission")
        raise PermissionError("You are not authorized to delete this post")

    await session.delete(post)
    await session.commit()