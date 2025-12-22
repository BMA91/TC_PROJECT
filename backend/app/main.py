from fastapi import FastAPI

from app.database import Base, SessionLocal, engine
from app.api.endpoints import users, admin
from app.models import user, ticket
from app.models.user import User

app = FastAPI()

# DROP AND RECREATE TABLES (for development - removes existing data)
# In production, use Alembic migrations instead
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def create_default_admin():
    """Create default admin user if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin_email = "admin@gmail.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if not existing_admin:
            # Create default admin
            admin_user = User(
                nom="Admin",
                prenom="System",
                telephone="000000000",
                password="admin",
                email=admin_email,
                role="admin",
            )
            db.add(admin_user)
            db.commit()
            print("✅ Default admin user created: admin@gmail.com / admin")
        else:
            print("ℹ️  Default admin user already exists")
    except Exception as e:
        print(f"❌ Error creating default admin: {e}")
        db.rollback()
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    """Create default admin on startup"""
    create_default_admin()


@app.get("/")
def root_from_tc():
    return {"message": "Backend is running 🚀"}


app.include_router(users.router)
app.include_router(admin.router)
