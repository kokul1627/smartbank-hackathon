# 🏦 Modular Banking Backend System

A **secure, modular, and scalable banking backend** built with **FastAPI**, **MongoDB**, and **JWT authentication**.  
Designed for **role-based access control (RBAC)** — supporting **Customers**, **Bank Admins**, and **Auditors** with clear separation of responsibilities.

> ⚡ **Built for hackathons** — clean, documented, testable, and production-oriented.

---

## 🚀 Features

### 👥 Actors & Roles

| Role | Responsibilities |
|------|------------------|
| **Customer** | Register, create accounts, transfer money, apply for loans, view statements & loan status |
| **Bank Admin** | Approve/reject loans, manage accounts, review flagged transactions |
| **Auditor** | Read-only access to audit logs and system activity |

---

## ⚙️ Core Use Cases

1. Login (Any User)
text[User] 
   ↓  POST /auth/login
[FastAPI]
   ↓  Check email + password
[MongoDB]
   ↓  User found & password correct?
[FastAPI]
   ↓  Generate JWT Token
   →  { access_token: "eyJ..." }
[User]

Anyone can login → gets JWT token


2. Admin Creates Customer
text[Admin] 
   ↓  Has JWT Token (from login)
   ↓  POST /auth/register
[FastAPI]
   ↓  Check JWT → role == "admin"?
   ↓  Yes → Save new user
[MongoDB]
   ↓  User saved
[FastAPI]
   ↓  Generate JWT for new customer
   →  { access_token, user: { id, name, email, role: "customer" } }
[Admin]

Only Admin can create users
No token in body → only in header


3. Admin Creates Account for Customer
text[Admin] 
   ↓  Has JWT Token
   ↓  POST /accounts/?user_id=123
[FastAPI]
   ↓  Check JWT → admin?
   ↓  Find user by ID
[MongoDB]
   ↓  User exists?
   ↓  Yes → Create account
[MongoDB]
   ↓  Account saved
[FastAPI]
   →  { account_number: "123456789", balance: 5000 }
[Admin]

Only Admin creates accounts
Needs customer’s MongoDB ID


4. Customer Views Own Accounts
text[Customer] 
   ↓  Has JWT Token
   ↓  GET /accounts/
[FastAPI]
   ↓  Check JWT → role == "customer"
   ↓  Get user_id from token
   ↓  Find accounts with same user_id
[MongoDB]
   →  List of accounts
[Customer]

Customer sees only their accounts


5. Customer Transfers Money
text[Customer] 
   ↓  POST /transactions/transfer
[FastAPI]
   ↓  Check JWT → customer?
   ↓  Check sender account = customer’s
   ↓  Check balance & daily limit
   ↓  Start transaction
[MongoDB]
   ↓  Deduct from sender
   ↓  Add to receiver
   ↓  Save transaction
   ↓  Commit
[FastAPI]
   →  { transaction_id, status: "completed" }
[Customer]

Atomic: All or nothing
Daily limit checked
---

## 🔐 Security Features

- **JWT Authentication** (PyJWT)
- **Password Hashing** with `bcrypt`
- **Role-Based Access Control (RBAC)**
- **Rate Limiting for Transactions**
- **Secure MongoDB Integration** (via Motor async driver)

---

## 🧠 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend Framework** | FastAPI (Python) |
| **Database** | MongoDB (via Motor async driver) |
| **Authentication** | JWT + bcrypt |
| **Testing** | Pytest (unit + integration) |
| **Configuration** | python-dotenv (`.env` files) |
| **API Documentation** | Swagger UI + ReDoc (auto-generated) |

---

## 🏗️ Project Structure

```bash
modular-banking-backend/
│
├── app/
│   ├── main.py                      # FastAPI entry (updated imports)
│   ├── config.py                    # MongoDB + JWT setup
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── bank_model.py            
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── bank_router.py          
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── audit_service.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── jwt_handler.py
│   │   ├── password.py
│   │   ├── auth_middleware.py
│   │   └── helpers.py
│   │
│   └── tests/
│       ├── __init__.py
│       └── test_registration.py
│
├── .env
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## ⚡ Quick Start


<img width="827" height="963" alt="image" src="https://github.com/user-attachments/assets/ffeef737-8832-483f-b295-29e8f8469884" />


register a new user {coustmer}
<img width="532" height="964" alt="image" src="https://github.com/user-attachments/assets/a6d8f56c-8fc3-430e-8d7a-0ae0e6e1ee48" />

### 1️⃣ Clone & Enter

```bash
git clone https://github.com/yourusername/modular-banking-backend.git
cd modular-banking-backend
```

### 2️⃣ Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure `.env`

```env
MONGO_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/bankdb?retryWrites=true&w=majority
JWT_SECRET=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
```

### 5️⃣ Run the Server

```bash
uvicorn app.main:app --reload
```

**API Docs Available At:**
- 🌐 **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📄 **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000=redoc)

---

## 🧪 Testing
## Testing with `pytest`

We use `pytest` with `mongomock_motor` to run **fast, isolated unit tests** without a real MongoDB.

### Features
- **No real database needed**
- **Fake in-memory DB** (`test_bankdb`)
- **100% safe** — no data loss
- **Fast & reliable**
<img width="1305" height="307" alt="image" src="https://github.com/user-attachments/assets/b91e17fe-acfe-435c-80d6-b3e915aa3491" />

<img width="627" height="797" alt="image" src="https://github.com/user-attachments/assets/fc55a050-144c-434b-9aa6-3001bb175a0d" />

---

### Setup

```bash
# Install test dependencies
pip install pytest mongomock-motor

# Or from requirements.txt
pip install -r requirements.txt
```

