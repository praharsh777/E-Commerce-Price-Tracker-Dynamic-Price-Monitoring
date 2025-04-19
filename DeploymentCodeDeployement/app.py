from flask import Flask, request, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import random
import csv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Directory paths for data storage
product_details_dir = os.path.join(os.getcwd(), 'data', 'product_details')
tracking_details_dir = os.path.join(os.getcwd(), 'data', 'tracking_details')

# Ensure directories exist; create if they don't        
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

        # Extract price: checking different possible price elements
        price_elem = soup.find('span', {'id': 'priceblock_ourprice'}) or \
                     soup.find('span', {'id': 'priceblock_dealprice'}) or \
                     soup.find('span', {'id': 'priceblock_saleprice'}) or \
                     soup.find('span', {'class': 'a-price-whole'}) or \
                     soup.find('span', {'class': 'a-price-symbol'}) or \
                     soup.find('span', {'class': 'a-offscreen'})  # Sometimes price is hidden here

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

        # Extract ASIN (Amazon Standard Identification Number)
        asin_elem = soup.find('input', {'id': 'ASIN'})
        asin = asin_elem['value'] if asin_elem else url.split('/')[-1] if 'dp' in url else 'ASIN not found'

        # Extract image URLs (use correct class for image tags)
        image_container = soup.find('div', {'id': 'imgTagWrapperId'})
        images = [img['src'] for img in image_container.find_all('img')] if image_container else []

        product_details = {
            'url': url,
            'title': title,
            'price': price,
            'ratings': ratings,
            'reviews': reviews,
            'description': description,
            'asin': asin,
            'images': images
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

        # Title
        title_elem = soup.find('span', {'class': 'VU-ZEz'})
        title = title_elem.get_text(strip=True) if title_elem else 'Title not found'

        # Price
        price_elem = soup.find('div', {'class': 'Nx9bqj CxhGGd'})
        price = price_elem.get_text(strip=True) if price_elem else 'Price not found'

        # Ratings
        ratings_elem = soup.find('div', {'class': 'XQDdHH'})
        ratings = ratings_elem.get_text(strip=True) if ratings_elem else 'Ratings not found'

        # Reviews
        reviews_elem = soup.find('span', {'class': 'Wphh3N'})
        reviews = reviews_elem.get_text(strip=True) if reviews_elem else 'Reviews not found'

        # Description
        description_elem = soup.find('div', {'class': '_4gvKMe'})
        description = description_elem.get_text(strip=True) if description_elem else 'Description not found'

        # Images
        images = [img.get('src', 'No source') for img in soup.select('#container > div > div._39kFie.N3De93.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div.DOjaWF.gdgoEp.col-5-12.MfqIAz img')]


        product_details = {
            'url': url,
            'title': title,
            'price': price,
            'ratings': ratings + " ★ out of 5★ ",
            'reviews': reviews,
            'description': description,
            'images': images
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
    csv_file = os.path.join(product_details_dir, 'product_details.csv')
    fieldnames = ['url', 'title', 'price', 'ratings', 'reviews', 'description', 'asin', 'images']

    try:
        with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if os.stat(csv_file).st_size == 0:
                writer.writeheader()
            writer.writerow(product_details)
    except IOError:
        pass  # No terminal output for errors

def send_email_notification(email, subject, message):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465
    smtp_username = 'trackmydeal24@gmail.com'
    smtp_password = 'ldbl cohg ddjr aizr'

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
        pass  # No terminal output for errors

def check_prices():
    tracking_csv_file = os.path.join(tracking_details_dir, 'tracking_details.csv')
    if not os.path.exists(tracking_csv_file):
        return

    with open(tracking_csv_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            email = row['email']
            product_url = row['product_url']
            initial_price = row.get('initial_price')

            if not initial_price:
                continue

            product_details = get_product_details(product_url)
            if 'error' in product_details:
                continue

            current_price = product_details['price'].replace(',', '').replace('₹', '').strip()
            try:
                current_price = float(current_price)
                initial_price = float(initial_price)
            except ValueError:
                continue

            if current_price < initial_price:
                subject = 'Price Drop Alert!'
                message = f"The price of the product you are tracking has dropped.\n\n" \
                          f"Product: {product_details['title']}\n" \
                          f"New Price: {product_details['price']}\n" \
                          f"Link: {product_url}\n"
                send_email_notification(email, subject, message)

scheduler = BackgroundScheduler()
scheduler.add_job(check_prices, 'interval', minutes=10)
scheduler.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    url = request.form.get('url')
    if not url:
        return render_template('error.html', message='URL is required')

    product_details = get_product_details(url)

    if 'error' in product_details:
        return render_template('error.html', message=product_details['error'])

    save_product_details(product_details)

    return render_template('result.html', product_details=product_details)

@app.route('/track', methods=['POST'])
def track():
    email = request.form.get('email')
    url = request.form.get('url')

    if not email or not url:
        return jsonify({'status': 'error', 'message': 'All fields are required'})

    product_details = get_product_details(url)
    if 'error' in product_details:
        return jsonify({'status': 'error', 'message': product_details['error']})

    tracking_csv_file = os.path.join(tracking_details_dir, 'tracking_details.csv')
    fieldnames = ['email', 'product_url', 'initial_price']

    try:
        with open(tracking_csv_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if os.stat(tracking_csv_file).st_size == 0:
                writer.writeheader()
            writer.writerow({'email': email, 'product_url': url, 'initial_price': product_details['price']})
    except IOError:
        return jsonify({'status': 'error', 'message': 'Failed to save tracking details'})

    subject = 'Product Tracking Confirmation'
    message = f"Thank you for tracking your product with us. We'll keep an eye on the price and notify you if the prize drops.\n\n" \
              f"Product: {product_details['title']}\n" \
              f"Price: {product_details['price']}\n" \
              f"Link: {url}\n"

    send_email_notification(email, subject, message)

    return jsonify({'status': 'success', 'message': 'Tracking details saved successfully and email sent!'})

if __name__ == '__main__':
    app.run(debug=True)
