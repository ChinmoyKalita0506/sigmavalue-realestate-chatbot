# Mini Real Estate Analysis Chatbot

A web‑based chatbot built with **React** (frontend) and **Django** (backend) that lets you:

- Analyze price trends for a given area  
- Compare demand trends between two areas  
- Show price growth over the last *N* years  

This was developed as the Sigmavalue Full Stack Developer Assignment (due 18 May 2025).

---

## 📋 Tech Stack

- **Backend**:  
  - Django  
  - Django REST Framework  
  - pandas  
  - openpyxl  
  - django-cors-headers  
- **Frontend**:  
  - React  
  - Axios  
  - Recharts  

---

## 🚀 Setup

### 1. Clone the repo

cd backend
# Create & activate virtualenv
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations (no models needed but still required)
python manage.py migrate

# Start the Django server
python manage.py runserver

cd ../frontend/realestate-chatbot
npm install
npm start

