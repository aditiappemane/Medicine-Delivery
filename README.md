# Medicine Delivery API

A complete Quick Commerce Medicine Delivery Platform built with FastAPI, featuring user authentication, medicine catalog management, prescription handling, and rapid delivery functionality.

## Features

### Authentication & Users
- ✅ User registration with medical profile
- ✅ User login with JWT authentication
- ✅ Profile management with medical information
- ✅ Phone number verification via SMS
- ✅ Delivery address management

### Coming Soon
- Medicine catalog management
- Prescription handling
- Order management
- Delivery tracking
- Payment integration

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: SQLAlchemy with SQLite (can be configured for PostgreSQL)
- **Authentication**: JWT with bcrypt password hashing
- **SMS Verification**: Twilio integration
- **Caching**: Redis
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## Quick Start

### 1. Clone and Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env with your configuration
```

### 2. Environment Configuration

Edit the `.env` file with your settings:

```env
# Database (SQLite for development)
DATABASE_URL=sqlite:///./medicine_delivery.db

# JWT Secret (change in production)
SECRET_KEY=your-super-secret-key-change-this-in-production

# Twilio (optional for SMS verification)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Redis (optional for development)
REDIS_URL=redis://localhost:6379
```

### 3. Run the Application

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user with medical profile |
| POST | `/auth/login` | User login |
| GET | `/auth/me` | Get current user profile |
| PUT | `/auth/profile` | Update user profile and delivery address |
| POST | `/auth/verify-phone` | Verify phone number for delivery |
| POST | `/auth/send-verification-code` | Send SMS verification code |

### Example Usage

#### 1. Register a New User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

#### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "securepassword123"
  }'
```

#### 3. Get User Profile (with token)

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 4. Update Profile

```bash
curl -X PUT "http://localhost:8000/auth/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "blood_group": "O+",
    "allergies": ["Penicillin", "Sulfa drugs"],
    "address_line1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001"
  }'
```

#### 5. Send Verification Code

```bash
curl -X POST "http://localhost:8000/auth/send-verification-code?phone=+1234567890" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 6. Verify Phone Number

```bash
curl -X POST "http://localhost:8000/auth/verify-phone" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "verification_code": "123456"
  }'
```

## Database Schema

### Users Table
- Basic info: id, email, phone, password, first_name, last_name
- Medical profile: date_of_birth, blood_group, allergies, medical_conditions
- Emergency contacts: emergency_contact_name, emergency_contact_phone
- Delivery address: address_line1, address_line2, city, state, postal_code, coordinates
- Verification status: is_phone_verified, is_email_verified, is_active
- Timestamps: created_at, updated_at

## Development

### Project Structure
```
app/
├── __init__.py
├── main.py              # FastAPI application
├── config.py            # Configuration settings
├── database.py          # Database connection
├── dependencies.py      # FastAPI dependencies
├── models/              # SQLAlchemy models
│   ├── __init__.py
│   └── user.py
├── schemas/             # Pydantic schemas
│   ├── __init__.py
│   └── user.py
├── routers/             # API routes
│   ├── __init__.py
│   └── auth.py
└── utils/               # Utility functions
    ├── __init__.py
    ├── auth.py
    └── sms.py
```

### Adding New Features

1. Create models in `app/models/`
2. Create schemas in `app/schemas/`
3. Create routers in `app/routers/`
4. Add utilities in `app/utils/`
5. Register routers in `app/main.py`

## Production Deployment

### Environment Variables
- Set `SECRET_KEY` to a strong random string
- Configure `DATABASE_URL` for your production database
- Set up Twilio credentials for SMS verification
- Configure Redis for caching and session management

### Security Considerations
- Use HTTPS in production
- Configure CORS properly
- Set up rate limiting
- Use environment variables for sensitive data
- Regular security updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 