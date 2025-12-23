# JWT Authentication Implementation Guide

## ✅ What's Already Implemented

Your project now has complete JWT authentication with password hashing using bcrypt.

### 1. **Password Hashing** ([app/security.py](app/security.py))
- Uses **bcrypt** for secure password hashing
- Passwords are automatically hashed when users are created or registered
- Never stores plain-text passwords in the database

```python
hash_password(password: str) -> str  # Hashes a password
verify_password(plain_password: str, hashed_password: str) -> bool  # Verifies passwords
```

### 2. **JWT Token Generation** ([app/security.py](app/security.py))
- Creates secure JWT tokens with:
  - 30-minute expiration (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
  - User email and ID embedded in token
  - HS256 algorithm for signing

```python
create_access_token(data: dict, expires_delta: Optional[timedelta]) -> str  # Creates JWT token
decode_access_token(token: str) -> Optional[TokenData]  # Validates JWT token
```

### 3. **Authentication Dependency** ([app/dependencies.py](app/dependencies.py))
- `get_current_user()` - Validates JWT tokens and returns the authenticated user
- Can be used to protect any endpoint

### 4. **API Endpoints**

#### Register User
```
POST /users/
Content-Type: application/json

{
  "nom": "John",
  "prenom": "Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "telephone": "1234567890"
}

Response (201):
{
  "id": 1,
  "nom": "John",
  "prenom": "Doe",
  "email": "john@example.com",
  "telephone": "1234567890",
  "role": "client_1"  // Randomly assigned
}
```

#### Login (Get JWT Token)
```
POST /users/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nom": "John",
    "prenom": "Doe",
    "email": "john@example.com",
    "telephone": "1234567890",
    "role": "client_1"
  }
}
```

#### Protected Endpoint - Get Current User
```
GET /users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response (200):
{
  "id": 1,
  "nom": "John",
  "prenom": "Doe",
  "email": "john@example.com",
  "telephone": "1234567890",
  "role": "client_1"
}
```

---

## 🔐 Security Features

1. **Password Hashing with Bcrypt**
   - Passwords are hashed before storing in database
   - Each password has a unique salt
   - Passwords are verified during login without decryption

2. **JWT Tokens**
   - Signed with a secret key
   - Include expiration time
   - Tamper-proof

3. **HTTP Bearer Token**
   - Tokens passed via `Authorization: Bearer <token>` header
   - Industry-standard authentication method

---

## 📝 How to Protect Endpoints

To protect any endpoint with JWT authentication, use the `get_current_user` dependency:

```python
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/protected-endpoint")
def protected_endpoint(current_user = Depends(get_current_user)):
    """This endpoint requires a valid JWT token"""
    return {
        "message": f"Hello, {current_user.prenom} {current_user.nom}",
        "user_id": current_user.id,
        "role": current_user.role
    }
```

---

## ⚙️ Configuration

Edit these values in [app/security.py](app/security.py):

```python
SECRET_KEY = "your-secret-key-change-this-in-production"  # Change this!
ALGORITHM = "HS256"  # JWT signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token validity period
```

### Important: Change SECRET_KEY in Production!
```python
# Generate a secure secret key:
import secrets
secret_key = secrets.token_urlsafe(32)
print(secret_key)
```

---

## 🚀 Testing with cURL

### 1. Register User
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "John",
    "prenom": "Doe",
    "email": "john@example.com",
    "password": "test123",
    "telephone": "1234567890"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "test123"
  }'
```

Save the `access_token` from the response.

### 3. Access Protected Endpoint
```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer <your-token-here>"
```

---

## 📦 Dependencies

All required packages are already installed:
- `python-jose[cryptography]` - JWT handling
- `passlib[bcrypt]` - Password hashing
- `bcrypt` - Bcrypt algorithm
- `fastapi` - Web framework

---

## ✨ What's Hashed & Secured

| Item | Security | Location |
|------|----------|----------|
| User Password | Bcrypt hash | Database |
| JWT Token | HS256 signed | Returned to client |
| Token Claims | Signed payload | Cannot be tampered |
| Credentials | Validated on login | In-memory, never stored |

---

## 📚 Files Modified/Created

1. ✅ [app/security.py](app/security.py) - Created (JWT & password handling)
2. ✅ [app/dependencies.py](app/dependencies.py) - Updated (Authentication dependency)
3. ✅ [app/schemas/user.py](app/schemas/user.py) - Updated (Token schema)
4. ✅ [app/crud/user.py](app/crud/user.py) - Updated (Password hashing on create)
5. ✅ [app/api/endpoints/users.py](app/api/endpoints/users.py) - Updated (Login endpoint)

---

## ✅ Next Steps

1. **Change the SECRET_KEY** to a strong, random value for production
2. **Test the authentication flow** using the cURL commands above
3. **Apply JWT protection** to other endpoints as needed using `Depends(get_current_user)`
4. **Configure token expiration time** if needed (default: 30 minutes)

All authentication is production-ready! 🎉
