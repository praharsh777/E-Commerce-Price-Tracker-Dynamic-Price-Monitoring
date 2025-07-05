from flask import Flask, request, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import random
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Setup data directories
product_details_dir = os.path.join(os.getcwd(), 'data', 'product_details')
tracking_details_dir = os.path.join(os.getcwd(), 'data', 'tracking_details')

os.makedirs(product_details_dir, exist_ok=True)
os.makedirs(tracking_details_dir, exist_ok=True)

# Define CSV file paths
product_details_path = os.path.join(product_details_dir, 'product_details.csv')
tracking_details_path = os.path.join(tracking_details_dir, 'tracking_details.csv')
def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
    ]
    return random.choice(user_agents)


def convert_price(price_str):
    try:
        return float(price_str.replace(',', '').replace('₹', '').replace('$', '').strip())
    except:
        return None


def get_amazon_product_details(url):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept-Language': 'en-US,en;q=0.9'
    }
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')

        title = soup.find('span', {'id': 'productTitle'})
        title = title.get_text(strip=True) if title else 'Title not found'

        price_elem = soup.find('span', {'class': 'a-offscreen'})
        price = price_elem.get_text(strip=True) if price_elem else 'Price not found'

        rating = soup.find('span', {'class': 'a-icon-alt'})
        rating = rating.get_text(strip=True) if rating else 'Ratings not found'

        reviews = soup.find('span', {'id': 'acrCustomerReviewText'})
        reviews = reviews.get_text(strip=True) if reviews else 'Reviews not found'

        description = soup.find('div', {'id': 'feature-bullets'})
        description = description.get_text(strip=True) if description else 'Description not found'

        images = []
        img_container = soup.find('div', {'id': 'imgTagWrapperId'})
        if img_container:
            for img in img_container.find_all('img'):
                src = img.get('src')
                if src:
                    images.append(src)

        return {
            'url': url,
            'title': title,
            'price': convert_price(price),
            'ratings': rating,
            'reviews': reviews,
            'description': description,
            'images': ','.join(images)
        }
    except Exception as e:
        return {'error': str(e)}


def get_flipkart_product_details(url):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept-Language': 'en-US,en;q=0.9'
    }
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')

        title = soup.find('span', {'class': 'VU-ZEz'})
        title = title.get_text(strip=True) if title else 'Title not found'

        price = soup.find('div', {'class': 'Nx9bqj CxhGGd'})
        price = price.get_text(strip=True) if price else 'Price not found'

        ratings = soup.find('div', {'class': '_5OesEi HDvrBb'})
        ratings = ratings.get_text(strip=True) if ratings else 'Ratings not found'

        reviews = soup.find('span', {'class': '_2_R_DZ'})
        reviews = reviews.get_text(strip=True) if reviews else 'Reviews not found'

        description = soup.find('div', {'class': 'yN+eNk'})
        description = description.get_text(strip=True) if description else 'Description not found'

        images = []
        image_wrappers = soup.select('div._4WELSP._6lpKCl img')
        for img in image_wrappers:
            src = img.get('src') or img.get('data-src')
            if src:
                images.append(src)

        return {
            'url': url,
            'title': title,
            'price': convert_price(price),
            'ratings': ratings,
            'reviews': reviews,
            'description': description,
            'images': ','.join(images)
        }
    except Exception as e:
        return {'error': str(e)}


def get_product_details(url):
    if 'amazon.in' in url or 'amzn.in' in url:
        return get_amazon_product_details(url)
    elif 'flipkart.com' in url:
        return get_flipkart_product_details(url)
    else:
        return {'error': 'Unsupported URL'}


def save_product_details(details):
    product_details_path = os.path.join(product_details_dir, 'product_details.csv')

    # Handle empty file safely
    if os.path.exists(product_details_path):
        try:
            df = pd.read_csv(product_details_path)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=details.keys())
    else:
        df = pd.DataFrame(columns=details.keys())

    # Check if the product already exists (optional)
    if 'url' in df.columns and details['url'] in df['url'].values:
        df.loc[df['url'] == details['url']] = details
    else:
        df = pd.concat([df, pd.DataFrame([details])], ignore_index=True)

    df.to_csv(product_details_path, index=False)

def save_tracking(email, url, price):
    df = pd.read_csv(tracking_details_path) if os.path.exists(tracking_details_path) else pd.DataFrame(columns=['email', 'producturl', 'initial_price', 'timestamp'])
    if not df[(df['email'] == email) & (df['producturl'] == url)].empty:
        return False
    new_entry = {'email': email, 'producturl': url, 'initial_price': price, 'timestamp': datetime.now()}
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(tracking_details_path, index=False)
    return True


def send_email_notification(email, subject, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = 'trackmydeal24@gmail.com'
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login('trackmydeal24@gmail.com', 'ldbl cohg ddjr aizr')
            server.sendmail(msg['From'], email, msg.as_string())
    except Exception as e:
        print(f"Email Error: {e}")


def check_prices():
    if not os.path.exists(tracking_details_path):
        return

    df = pd.read_csv(tracking_details_path)
    for _, row in df.iterrows():
        email, url, initial_price = row['email'], row['producturl'], row['initial_price']
        details = get_product_details(url)
        if 'error' not in details and details['price'] and details['price'] < float(initial_price):
            message = f"Price dropped!\nProduct: {details['title']}\nNew Price: ₹{details['price']}\nLink: {url}"
            send_email_notification(email, 'Price Drop Alert!', message)


scheduler = BackgroundScheduler()
scheduler.add_job(check_prices, 'interval', minutes=5)
scheduler.start()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        details = get_product_details(url)
        if 'error' in details:
            return render_template('result.html', error=details['error'])
        save_product_details(details)
        return render_template('result.html', product_details=details)
    return render_template('index.html')


@app.route('/track', methods=['POST'])
def track():
    url = request.form.get('producturl')
    email = request.form.get('email')
    details = get_product_details(url)
    if 'error' in details:
        return jsonify({'error': details['error']})

    if not save_tracking(email, url, details['price']):
        return jsonify({'error': 'Already tracking this product.'})

    msg = f"Hi, you're now tracking: {details['title']}\nCurrent Price: ₹{details['price']}\nLink: {url}"
    send_email_notification(email, 'Product Tracking Confirmation', msg)
    return jsonify({'message': 'Tracking started successfully!'})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

