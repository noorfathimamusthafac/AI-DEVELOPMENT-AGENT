from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import User
from app.auth.security import hash_password
from app.auth.routes import router as auth_router
from app.api.agent_routes import router as agent_router

# Create DB schema
Base.metadata.create_all(bind=engine)

def seed_default_users():
    db = SessionLocal()
    try:
        # Seed Developer
        dev = db.query(User).filter(User.email == "dev@example.com").first()
        if not dev:
            dev = User(
                email="dev@example.com",
                hashed_password=hash_password("password123"),
                full_name="Sarah Developer",
                role="developer"
            )
            db.add(dev)
        
        # Seed Admin
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin = User(
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                full_name="Alex Lead Admin",
                role="admin"
            )
            db.add(admin)

        db.commit()
    finally:
        db.close()

seed_default_users()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Development Assistant integrating with OpenProject Work Board",
    version="1.0.0"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(agent_router)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "mode": "mock" if settings.OPENPROJECT_MOCK_MODE else "live",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
