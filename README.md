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

### 1️⃣ User Registration
- Customer submits personal details
- System validates and securely stores the profile

### 2️⃣ Account Creation
- Choose account type: `Savings`, `Current`, or `Fixed Deposit`
- System generates a unique account number
- Records initial deposit

### 3️⃣ Money Transfer
- Validate sender’s balance and daily limit
- Perform atomic balance updates across accounts  
- **Edge Cases Handled:**
  - Insufficient funds  
  - Daily transfer limit exceeded

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
│   ├── main.py                 # FastAPI app entry
│   ├── config.py               # DB + JWT setup
│   ├── models/                 # Pydantic schemas
│   ├── routes/                 # Modular API endpoints
│   │   ├── auth.py
│   │   ├── accounts.py
│   │   ├── transactions.py
│   │   ├── loans.py
│   │   └── audit.py
│   ├── services/               # Business logic layer
│   ├── utils/                  # JWT, hashing, rate limiter, etc.
│   ├── tests/                  # Unit + integration tests
│   └── __init__.py
│
├── .env                        # Environment variables
├── requirements.txt
├── run.sh                      # Dev startup script
└── README.md                   # You’re here!

```

---

## ⚡ Quick Start

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

Run full test suite with coverage:

```bash
pytest --cov=app
```

Detailed coverage report:

```bash
pytest --cov=app --cov-report=term-missing
```

