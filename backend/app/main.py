from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
import traceback

from app.database import Base, SessionLocal, engine
from app.api.endpoints import users, admin
from app.models import user, ticket
from app.models.user import User

app = FastAPI()


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
    """Initialize database and create default admin on startup"""
    # DROP AND RECREATE TABLES (for development - removes existing data)
    # In production, use Alembic migrations instead
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise
    
    create_default_admin()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to catch all errors and return detailed error messages"""
    error_detail = {
        "error": str(exc),
        "type": type(exc).__name__,
        "path": str(request.url),
    }
    # Include traceback in development
    error_detail["traceback"] = traceback.format_exc()
    print(f"❌ Error: {error_detail}")  # Print to console for debugging
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(error_detail),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.get("/")
def root_from_tc():
    return {"message": "Backend is running 🚀"}


app.include_router(users.router)
app.include_router(admin.router)
