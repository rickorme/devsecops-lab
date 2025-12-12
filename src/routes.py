from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from data.users import users_data
from data.models import PostCreate, PostResponse
from typing import Optional
import logging
import datetime

from data.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("creating db and tables")
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# router = FastAPI().router

@app.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        caption: str = Form(""),
        session: AsyncSession = Depends(get_async_session)
):
    post = Post(
        caption=caption,
        url="dummyurl",
        file_type="photo",
        file_name="dummy naem"
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post

@app.get("/feed")
async def get_feed(
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat()
            }
        )

    return {"posts": posts_data}


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




# text_posts = {
#     1: {"title": "Golden Hour on the Coast 🌅","content": "Managed to catch the most incredible light this morning down at Big Sur! I used my new prime lens ($f/1.8$) and shot at a low ISO to keep the details sharp. The mist rolling in added a beautiful, soft texture. Let me know what you think of the composition! Should I crop tighter on the rocks?"},
#     2: {"title": "Street Portrait in the Rain","content": "This candid shot was taken yesterday in the city. The reflection of the neon signs in the wet pavement was the main draw. I struggled a bit with the autofocus in the low light, but the mood is exactly what I was aiming for. Used a high shutter speed to freeze the raindrops. Critiques welcome!"},
#     3: {"title": "Macro Magic: Dew Drop on a Leaf 🌿","content": "First time trying out focus stacking for macro photography! It took about 15 shots to get this level of detail on the tiny dew drop. I used a ring light to illuminate it evenly. Any tips on minimizing background distractions in macro work? It's a tricky one!"},
#     4: {"title": "Milky Way over the Mountains ✨","content": "Spent all night hiking for this shot! It's a $30$-second exposure at $ISO$ $3200$. I used an intervalometer to take multiple shots for noise reduction in post. The light pollution from the nearby town is still a bit noticeable on the horizon. Does anyone have a good workflow for editing the Galactic Core?"},
#     5: {"title": "Vintage Film Look with Digital","content": "Experimenting with color grading to emulate the look of Kodak Portra film. This is a landscape photo from a recent trip. I adjusted the tone curve and added some grain in Lightroom. It's amazing how much you can change the feel of an image just with color. Does it feel authentic to film?"},
#     6: {"title": "Action Shot: Dog Catching a Frisbee 🐕","content": "Finally nailed a clear action shot! I pre-focused on the spot where I expected the action and used continuous shooting mode. The shutter speed was set to $1/1600$s. Still figuring out the best balance of depth of field for fast-moving subjects. Any recommendations for continuous autofocus settings?"},
#     7: {"title": "Monochrome Cityscape","content": "Converted this cityscape to black and white to emphasize the architectural lines and textures. I used a red filter effect in post to darken the sky dramatically. The contrast is a little high, maybe? I'm trying to achieve a dramatic, high-key look. Should I bring the shadows up a bit more?"},
#     8: {"title": "A Rainbow Through the Window 🌈","content": "A simple, candid moment captured inside. The light hit the prism on the window just right, casting a small rainbow. The challenge was maintaining the exposure on both the bright window and the darker interior. I bracketed the shot to blend them later. What subtle details do you notice?"},
#     9: {"title": "Long Exposure Waterfall Blur 🌊","content": "Used a $6$-stop ND filter to get this silky smooth water effect on a waterfall. The total exposure time was $2$ seconds. I had to wait for the wind to die down completely to keep the surrounding foliage sharp. Next time, I plan to try an even longer exposure. What's your favorite ND filter brand?"},
#     10: {"title": "Wildlife: Bird in Flight", "content": "Extremely happy with this capture of a hawk mid-flight! I was using a telephoto zoom lens and had to track the bird carefully. I find it difficult to keep the subject framed properly at the extreme end of the zoom. The background bokeh is lovely though. Any tips for handheld tracking?"}
# }

# @router.get("/hello-world")
# def hello_world():
#     return {"message": "Hello World"}

# @router.get("/users")
# def get_users(limit: Optional[int] = None):
#     logger.info("/api/users was called successfully: " + str(datetime.datetime.now()))

#     if limit:
#         return users_data[:limit]
#     return users_data

# @router.get("/users/{user_id}")
# def get_user(user_id: int):
#     logger.info(f"/api/users/{user_id} was called successfully: " + str(datetime.datetime.now()))
#     user = next((user for user in users_data if user['id'] == user_id), None)
#     if user:
#         return user
#     raise HTTPException(status_code=404, detail="User not found")

# @router.get("/posts/")
# def get_text_posts(limit: Optional[int] = None):
#     if limit:
#         return dict(list(text_posts.items())[:limit])
    
#     return text_posts

# @router.get("/posts/{post_id}")
# def get_text_post(post_id: int):
#     post = text_posts.get(post_id)
#     if post:
#         return post
#     raise HTTPException(status_code=404, detail="Post not found")

# @router.post("/posts/")
# def create_post(post: PostCreate):
#     new_post = {"title": post.title, "content": post.content}
#     text_posts[max(text_posts.keys()) + 1] = new_post

#     return new_post

# @router.delete("/posts/{post_id}")
# def delete_post(post_id: int):
#     if post_id in text_posts:
#         del text_posts[post_id]
#         return {"detail": "Post with id " + str(post_id) + " deleted"}
#     raise HTTPException(status_code=404, detail="Post not found")