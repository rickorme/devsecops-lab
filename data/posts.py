from data.users import current_active_user, get_users_dict
from data.db import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends


import logging
import io
from PIL import Image


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
    


async def get_posts(
        session: AsyncSession,
        user: User = Depends(current_active_user)
        
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]
    
    users_dict = await get_users_dict(session)

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "file_type": post.file_type,
                # "file_content": post.file_content,
                # "thumbnail_content": post.thumbnail_content,
                "file_name": post.file_name,
                "content_type": post.content_type,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": users_dict.get(post.user_id, "unknown")
            }
        )
    return posts_data    