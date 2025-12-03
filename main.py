import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles 
from src.routes import router

app = FastAPI(title="Simple labb projekt app")

# Include the API router
app.include_router(router)

# ⬇️ Configuration to serve static files
app.mount(
    "/",  # 1. The path users will access (root path)
    StaticFiles(directory="public", html=True), # 2. The directory containing the files
    name="public" # 3. An internal name for FastAPI
)

def main():
    print("Starting test app...")
    

if __name__ == "__main__":
    main()