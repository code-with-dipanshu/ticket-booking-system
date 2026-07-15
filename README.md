# 🎟️ Ticket Booking System

A full-stack Ticket Booking and Event Management System built with **FastAPI, PostgreSQL, SQLAlchemy, Redis, React, and Vite**.

## 🚀 Live Demo

### 🌐 Frontend
**https://ticket-booking-frontend-uktc.onrender.com**

### ⚙️ Backend API
**https://ticket-booking-backend-wg5h.onrender.com**

### 📖 API Documentation (Swagger)
**https://ticket-booking-backend-wg5h.onrender.com/docs**

---

## ✨ Features

- 🔐 JWT Authentication & Role-Based Authorization
- 🎫 Ticket Booking System
- 🏟️ Venue Management
- 🎭 Event Management
- 💺 Seat Booking & Availability
- ⚡ Redis-based Seat Hold Mechanism
- 📦 PostgreSQL Database
- 🐳 Dockerized Deployment
- 📱 Responsive React Frontend
- 📚 Interactive API Documentation (Swagger)

---

## 🛠️ Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Redis
- JWT Authentication

### Frontend
- React
- Vite
- JavaScript
- HTML/CSS

### DevOps
- Docker
- Render
- GitHub

---

## 📂 Project Structure

```
Ticket-Booking/
│
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml
├── render.yaml
└── README.md
```

---

## 🚀 Running Locally

### Clone Repository

```bash
git clone https://github.com/code-with-dipanshu/ticket-booking-system.git
cd Ticket-Booking
```

---

### Backend

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend runs on:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

---

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend runs on:

```
http://localhost:5173
```

---

## 🐳 Docker

Run the complete application using Docker Compose:

```bash
docker compose up --build
```

Services:

| Service | Port |
|----------|------|
| Frontend | 5173 |
| Backend | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |

---

## 🩺 Health Check

```
GET https://ticket-booking-backend-wg5h.onrender.com/health
```

Example Response:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## 🧪 API Testing

Swagger Documentation:

**https://ticket-booking-backend-wg5h.onrender.com/docs**

Use Swagger UI to test:

- User Registration
- Login
- Event APIs
- Venue APIs
- Ticket Booking APIs
- Authentication

---

## 🌍 Deployment

| Service | URL |
|---------|-----|
| Frontend | https://ticket-booking-frontend-uktc.onrender.com |
| Backend | https://ticket-booking-backend-wg5h.onrender.com |
| Swagger API Docs | https://ticket-booking-backend-wg5h.onrender.com/docs |

---

## 👨‍💻 Author

**Dipanshu Ramteke**

B.Tech Computer Science Engineering (Data Science)

Vishwakarma Institute of Information Technology, Pune

GitHub: https://github.com/code-with-dipanshu


---