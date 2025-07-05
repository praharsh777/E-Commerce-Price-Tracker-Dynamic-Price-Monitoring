# 🛒 E-Commerce Price Tracker — Dynamic Price Monitoring

Track product prices on Amazon and Flipkart, get instant insights, and receive **email alerts** when prices drop!

![Flask](https://img.shields.io/badge/Flask-Framework-blue)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)
![WebScraping](https://img.shields.io/badge/Web%20Scraping-BeautifulSoup-green)
![Status](https://img.shields.io/badge/Status-Working-brightgreen)

---

## 📌 Features

- 🔍 Scrape live product details from **Amazon** & **Flipkart**
- 📊 Display Title, Price, Rating, Reviews, Description, and Images
- 📧 Track product by email — get notified on **price drops**
- 🗃️ Stores product & tracking data using **CSV files**
- 🌙 Clean UI with Dark Mode Toggle
- 🔁 Auto price check every 5 minutes using APScheduler

---

## 📁 Project Structure

E-Commerce-Price-Tracker-Dynamic-Price-Monitoring/
├── app.py
├── templates/
│ ├── index.html
│ ├── result.html
│ ├── error.html
├── data/
│ ├── product_details/
│ │ └── product_details.csv
│ ├── tracking_details/
│ └── tracking_details.csv
├── requirements.txt
└── README.md

---

## ⚙️ How it Works

1. Paste any **Amazon** or **Flipkart** product URL.
2. App fetches product details like title, price, ratings, reviews, images, etc.
3. User can enter their **email** and start **tracking** the product.
4. App checks prices every 5 mins; on drop, a notification email is sent!
5. All data is stored in local **CSV files** instead of a database.

---

## 📸 Screenshots

> 📌 *Insert screenshots of the homepage and result page if possible*

---

## 🧪 Technologies Used

- `Python 3.10+`
- `Flask`
- `BeautifulSoup` + `Requests`
- `APScheduler`
- `smtplib` for email notifications
- `pandas` for data storage (CSV)
- `HTML + CSS + JavaScript` (Frontend)

---

## 📦 Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/praharsh777/E-Commerce-Price-Tracker-Dynamic-Price-Monitoring.git
   cd E-Commerce-Price-Tracker-Dynamic-Price-Monitoring
Install dependencies

pip install -r requirements.txt
Run the Flask App

python app.py
Visit:
http://127.0.0.1:5000/
📬 Email Notification Setup
The app uses a Gmail account to send alerts.

Email ID: trackmydeal24@gmail.com

Make sure you enable "App Passwords" in Gmail settings if you deploy your own version.

🚀 Hosting Recommendations
Can be hosted easily on:

Railway (with free plan)

Render

Fly.io

Replit (for small-scale demo)

No DB setup needed (CSV files are used)!

🙋‍♂️ Author
Praharsh Sai
📧 praharshsai867@gmail.com
🔗 GitHub

