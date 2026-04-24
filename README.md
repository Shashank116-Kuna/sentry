# 🛡️ SENTRY

### Social Engineering Threat Reporting & Detection System

🚀 **Mini Project – B.Tech (Pre-Final Year)**

---

## 👥 Team Members

* Shashank
* Manikanta
* Amulya
* Sirini

---

## 📌 Project Overview

**SENTRY** is a real-time web-based system designed to detect and analyze social engineering scams such as phishing, OTP fraud, and fake KYC messages.

The system uses **Natural Language Processing (NLP)** techniques to identify suspicious patterns, assign risk scores, and group similar scam messages into campaigns.

---

## 🎯 Objectives

* Detect scam messages in real-time
* Identify social engineering techniques
* Generate risk scores for reports
* Cluster similar reports into campaigns
* Provide a live dashboard for monitoring

---

## 🧠 Key Features

* 🔍 **Scam Detection using NLP**
* 📊 **Risk Scoring System**
* 🧩 **Campaign Clustering**
* ⚡ **Real-Time Dashboard**
* 🔐 **Privacy-focused Data Handling**
* 🚦 **Rate Limiting & Input Validation**

---

## 🏗️ System Architecture

```
User (Frontend)
      ↓
Frontend (HTML, CSS, JS)
      ↓
FastAPI Backend
      ↓
NLP Processing + Security Modules
      ↓
SQLite Database
      ↓
Dashboard & Alerts
```

---

## 🧩 Modules

### 1. API Module

Handles report submission, campaigns, alerts, and events

### 2. NLP Module

* Text preprocessing
* Entity extraction
* Scam technique detection

### 3. Security Module

* Input validation
* Rate limiting

### 4. Database Module

* Stores reports, campaigns, statistics

### 5. Frontend Module

* Dashboard UI
* Report submission form
* Real-time updates

---

## 💻 Tech Stack

**Backend:**

* Python
* FastAPI
* SQLite

**Frontend:**

* HTML
* CSS
* JavaScript

**Other Tools:**

* Uvicorn
* Git & GitHub

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/sentry.git
cd sentry
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
cd backend
python app.py
```

### 5. Open in browser

```
http://localhost:8000/static/index.html
```

---

## 🧪 Testing

* Unit Testing
* API Testing
* Functional Testing
* Performance Testing

---

## 📸 Output

> Add screenshots here:

* Dashboard
* Report submission
* Campaign detection

---

## 🚀 Future Scope

* AI-based advanced scam detection
* Integration with messaging platforms (WhatsApp, Truecaller)
* Mobile application development
* Multi-language support

---

## 📌 Conclusion

SENTRY provides an efficient and scalable solution for detecting social engineering scams in real time. It enhances user awareness and helps in identifying large-scale scam campaigns.

---

## 🙏 Acknowledgement

We thank our faculty and mentors for their guidance and support throughout the project.

---

## ⭐ If you like this project

Give it a star on GitHub!
