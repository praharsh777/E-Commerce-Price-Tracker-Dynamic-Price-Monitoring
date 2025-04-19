from flask import Flask, request, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import random
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler
import mysql.connector

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your MySQL username
    password="",  # Replace with your MySQL password
    database="trackmydealdb"
)
cursor = db.cursor()

# Directory paths for data storage (currently unused)
product_details_dir = os.path.join(os.getcwd(), 'data', 'product_details')
tracking_details_dir = os.path.join(os.getcwd(), 'data', 'tracking_details')
os.makedirs(product_details_dir, exist_ok=True)
os.makedirs(tracking_details_dir, exist_ok=True)

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        # Add more user agents if needed
    ]
    return random.choice(user_agents)

def convert_price(price_str):
    try:
        return float(price_str.replace(',', '').replace('₹', '').replace('$', '').strip())
    except ValueError:
        return None

def get_amazon_product_details(url):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title_elem = soup.find('span', {'id': 'productTitle'}) or \
                     soup.find('h1', {'id': 'title'})
        title = title_elem.get_text(strip=True) if title_elem else 'Title not found'

        # Extract price
        price_elem = soup.find('span', {'id': 'priceblock_ourprice'}) or \
                     soup.find('span', {'id': 'priceblock_dealprice'}) or \
                     soup.find('span', {'id': 'priceblock_saleprice'}) or \
                     soup.find('span', {'class': 'a-price-whole'}) or \
                     soup.find('span', {'class': 'a-price-symbol'}) or \
                     soup.find('span', {'class': 'a-offscreen'})
        price = price_elem.get_text(strip=True) if price_elem else 'Price not found'

        # Extract ratings
        ratings_elem = soup.find('span', {'class': 'a-icon-alt'})
        ratings = ratings_elem.get_text(strip=True) if ratings_elem else 'Ratings not found'

        # Extract reviews
        reviews_elem = soup.find('span', {'id': 'acrCustomerReviewText'})
        reviews = reviews_elem.get_text(strip=True) if reviews_elem else 'Reviews not found'

        # Extract description
        description_elem = soup.find('div', {'id': 'feature-bullets'}) or \
                           soup.find('div', {'id': 'productDescription'}) or \
                           soup.find('div', {'id': 'productOverview'})
        description = description_elem.get_text(strip=True) if description_elem else 'Description not found'

        # Extract images
        image_container = soup.find('div', {'id': 'imgTagWrapperId'})
        images = [img['src'] for img in image_container.find_all('img')] if image_container else []

        product_details = {
            'url': url,
            'title': title,
            'price': convert_price(price),
            'ratings': ratings,
            'reviews': reviews,
            'description': description,
            'images': ','.join(images)  # Convert list to comma-separated string for CSV
        }

        return product_details

    except requests.exceptions.RequestException as e:
        return {'error': f'An error occurred: {str(e)}'}

def get_flipkart_product_details(url):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title_elem = soup.find('span', {'class': 'VU-ZEz'})
        title = title_elem.get_text(strip=True) if title_elem else 'Title not found'

        # Extract price
        price_elem = soup.find('div', {'class': 'Nx9bqj CxhGGd'})
        price = price_elem.get_text(strip=True) if price_elem else 'Price not found'

        # Extract ratings
        ratings_elem = soup.find('div', {'class': 'XQDdHH'})
        ratings = ratings_elem.get_text(strip=True) if ratings_elem else 'Ratings not found'

        # Extract reviews
        reviews_elem = soup.find('span', {'class': 'Wphh3N'})
        reviews = reviews_elem.get_text(strip=True) if reviews_elem else 'Reviews not found'

        # Extract description
        description_elem = soup.find('div', {'class': '_4gvKMe'})
        description = description_elem.get_text(strip=True) if description_elem else 'Description not found'

        # Extract images
        images = [img.get('src', 'No source') for img in soup.select('#container > div > div._39kFie.N3De93.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div.DOjaWF.gdgoEp.col-5-12.MfqIAz img')]

        product_details = {
            'url': url,
            'title': title,
            'price': convert_price(price),
            'ratings': ratings + " ★ out of 5★ ",
            'reviews': reviews,
            'description': description,
            'images': ','.join(images)  # Convert list to comma-separated string for CSV
        }

        return product_details

    except requests.exceptions.RequestException as e:
        return {'error': f'An error occurred: {str(e)}'}

def get_product_details(url):
    if 'amazon.in' in url:
        return get_amazon_product_details(url)
    elif 'flipkart.com' in url:
        return get_flipkart_product_details(url)
    else:
        return {'error': 'Unsupported URL'}

def save_product_details(product_details):
    try:
        query = """
        INSERT INTO product_details (url, title, price, ratings, reviews, description, images)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        price = VALUES(price), ratings = VALUES(ratings), reviews = VALUES(reviews)
        """
        values = (
            product_details['url'],
            product_details['title'],
            product_details['price'],
            product_details['ratings'],
            product_details['reviews'],
            product_details['description'],
            product_details['images']
        )
        cursor.execute(query, values)
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def send_email_notification(email, subject, message):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465
    smtp_username = 'trackmydeal24@gmail.com'
    smtp_password = 'ldbl cohg ddjr aizr'  # Use environment variables in practice

    sender_email = smtp_username
    receiver_email = email

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")

def check_prices():
    try:
        # Query to get all tracking details from the database
        query = """
        SELECT email, producturl, initial_price
        FROM tracking_details
        """
        cursor.execute(query)
        tracked_products = cursor.fetchall()

        # Loop through each tracked product
        for tracking in tracked_products:
            email = tracking[0]
            product_url = tracking[1]
            initial_price = tracking[2]

            # Scrape the current product details
            product_details = get_product_details(product_url)
            if 'error' in product_details:
                continue

            current_price = product_details['price']
            try:
                current_price = float(current_price)
                initial_price = float(initial_price)
            except ValueError:
                continue  # Skip the product if price conversion fails

            # If the current price is lower than the initial price, send an email notification
            if current_price and initial_price and current_price < initial_price:
                subject = 'Price Drop Alert!'
                message = f"The price of the product you are tracking has dropped.\n\n" \
                          f"Product: {product_details['title']}\n" \
                          f"New Price: {product_details['price']}\n" \
                          f"Link: {product_url}\n"
                send_email_notification(email, subject, message)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Scheduler to run price check every hour
scheduler = BackgroundScheduler()
scheduler.add_job(check_prices, 'interval', hours=1)
scheduler.start()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        product_details = get_product_details(url)
        if 'error' in product_details:
            return render_template('result.html', error=product_details['error'])

        save_product_details(product_details)

        return render_template('result.html', product_details=product_details)

    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track():
    # Retrieve form data
    url = request.form.get('producturl')
    email = request.form.get('email')

    # Validate input
    if not url or not email:
        return jsonify({'error': 'Please provide both email and product URL.'})

    # Get product details
    product_details = get_product_details(url)
    if 'error' in product_details:
        return jsonify({'error': product_details['error']})

    # Save tracking details
    try:
        query = """
        INSERT INTO tracking_details (email, producturl, timestamp)
        VALUES (%s, %s, NOW())
        """
        values = (email, url)
        cursor.execute(query, values)
        db.commit()

        # Send confirmation email
        subject = 'Product Tracking Confirmation'
        message = f"Thank you for tracking your product with us. We'll keep an eye on the price and notify you if the prize drops. {url}.\n\n" \
                  f"Product: {product_details['title']}\n" \
                  f"urrent Price: {product_details['price']}\n"
        send_email_notification(email, subject, message)

        return jsonify({'message': 'Product tracking started successfully!'})

    except mysql.connector.Error as err:
        return jsonify({'error': f"Database error: {err}"})

if __name__ == '__main__':
    app.run(debug=True)
