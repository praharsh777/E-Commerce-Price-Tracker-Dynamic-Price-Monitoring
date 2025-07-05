# 🛍️ E-Commerce Price Tracker – Dynamic Price Monitoring

A Flask-based web application to track product prices on **Amazon** and **Flipkart**. Users can enter product URLs and their email addresses to receive notifications when prices drop.

## 🚀 Features

- ✅ Track prices from Amazon & Flipkart
- 📧 Email notifications on price drops
- 🔄 Background scheduler checks prices every 5 minutes
- 💾 Product info and tracking data stored in MySQL
- 🖼️ Displays product title, price, ratings, reviews, and image
- 🔒 Prevents duplicate tracking entries

## 🖥️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript, Jinja2
- **Backend**: Flask (Python)
- **Database**: MySQL
- **Web Scraping**: `requests`, `BeautifulSoup`
- **Email**: `smtplib`, Gmail SMTP
- **Scheduler**: APScheduler

## 📦 Project Structure

project/
│
├── templates/
│ ├── index.html
│ ├── result.html
│
├── app.py
└── README.md

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/praharsh777/E-Commerce-Price-Tracker-Dynamic-Price-Monitoring.git
cd E-Commerce-Price-Tracker-Dynamic-Price-Monitoring
```
2. Create Virtual Environment (Optional but Recommended)
bash
Copy code
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On Mac/Linux
3. Install Dependencies
bash
Copy code
pip install -r requirements.txt
If requirements.txt is not created yet, use:
pip freeze > requirements.txt

4. Setup MySQL Database
Create a database named: trackmydealdb

Create tables:

sql
Copy code
CREATE TABLE product_details (
    url TEXT PRIMARY KEY,
    title TEXT,
    price FLOAT,
    ratings TEXT,
    reviews TEXT,
    description TEXT,
    images TEXT
);

CREATE TABLE tracking_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255),
    producturl TEXT,
    initial_price FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
5. Start the Server
bash
Copy code
python app.py
Then go to: http://127.0.0.1:5000

📩 SMTP Setup for Email
The app uses Gmail SMTP.

Go to your Google Account → Security → Enable 2-Step Verification and App Passwords

Replace credentials in app.py:

python
Copy code
smtp_username = 'your-email@gmail.com'
smtp_password = 'your-app-password'
🧪 Sample Product URLs
Amazon: https://www.amazon.in/dp/B09HPQFWS8

Flipkart: https://www.flipkart.com/honor-200-lite-5g/p/itmxxxxxxx

💡 To-Do / Future Improvements
Add user login system

Store price history graph

Support more e-commerce platforms

Add mobile view / responsive design

🧑‍💻 Author
Praharsh
GitHub: @praharsh777

📜 License
This project is for educational use only. Commercial scraping may violate terms of service.

yaml
Copy code

---

Let me know if you want a shorter version or if you'd like badges, demo images, or d
