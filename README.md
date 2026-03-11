#  Cab Booking System Backend

This project is a backend system for a ride-booking platform inspired by applications like Uber and Ola.

It was developed as part of the **Labmentix Internship Program** to demonstrate backend development, API design, and cloud deployment.

---

#  Features

• Request a ride  
• Driver accepts ride  
• Complete ride  
• Payment integration using Stripe  
• Receipt generation  
• Driver review system  
• Admin APIs  
• Deployed backend API

---

#  Tech Stack

Backend:
- FastAPI
- Python

Database:
- PostgreSQL
- SQLModel / SQLAlchemy

Other Tools:
- Redis (driver matching)
- Stripe API (payments)

Deployment:
- Render Cloud Platform
- GitHub


#  Project Architecture

Frontend (HTML + JS)  
↓  
FastAPI Backend  
↓  
PostgreSQL Database  
↓  
Stripe Payment API  


#  Deployment

The backend is deployed using **Render Web Services**.

### Step 1 — Push project to GitHub


git init
git add .
git commit -m "cab booking system"
git push

### Step 2 — Connect GitHub repository to Render

Render automatically pulls the repository and deploys the backend service.

### Step 3 — Build Command


pip install -r backend/requirements.txt


This installs all project dependencies such as FastAPI, SQLModel, Redis, and Stripe.

---

### Step 4 — Start Command


uvicorn backend.main:app --host 0.0.0.0 --port $PORT


This command starts the FastAPI application on the Render server.

---

### Step 5 — Environment Variables

Sensitive credentials are stored securely using environment variables.


DATABASE_URL
STRIPE_SECRET_KEY

# 🌐 Live Deployment

Backend API


https://cab-booking-api-sdjk.onrender.com


Swagger API Documentation


https://cab-booking-api-sdjk.onrender.com/docs


# 📂 Project Structure
cab-booking-system
│
├── backend
│ ├── routes
│ ├── services
│ ├── models.py
│ ├── database.py
│ └── main.py
│
├── frontend
│ ├── index.html
│ ├── rider.html
│ ├── driver.html
│ └── script.js

#  Demo Flow

1️⃣ Rider requests a ride  
2️⃣ Driver accepts the ride  
3️⃣ Ride is completed  
4️⃣ Rider makes payment  
5️⃣ Rider leaves a review

---

#  What I Learned

Through this project I learned:

• Designing REST APIs using FastAPI  
• Database modeling with PostgreSQL  
• Payment integration using Stripe  
• Secure environment variable management  
• Deploying applications using Render  
• Version control with Git and GitHub
