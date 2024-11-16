from flask import Flask, request, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', products= None)

@app.route('/products', methods=['GET'])
def show_products():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    category = request.args.get('category')  # Get category from query string
    cursor.execute('SELECT * FROM products WHERE category = ?', (category,))

    products = cursor.fetchall()
    conn.close()

    return render_template('index.html', products=products)


@app.route('/buy-request', methods=['POST'])
def receive_order():
    product = request.form['product_name']
    client_name = request.form['name']
    client_email = request.form['email']
    client_address = request.form['address']
    total_price = request.form['product_price'].replace("$", "")

    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO orders (name, email, address, product, total) 
        VALUES (?, ?, ?, ?, ?)
    ''', (client_name, client_email, client_address, product, total_price))

    conn.commit()
    conn.close()
    return render_template("buy.html", Order = Order(product, client_name, client_email, client_address))

@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.get_json()  # Parse JSON from the request body
    reviewer_name = data.get('reviewer_name')
    review = data.get('review')
    rating = data.get('rating')
    product = data.get('product_name')

    if not review or not product or rating is None:
        return jsonify({"message": "Invalid data"}), 400

    # Insert the review into the reviews.db
    reviews_conn = sqlite3.connect('reviews.db')
    reviews_cursor = reviews_conn.cursor()
    reviews_cursor.execute(
        'INSERT INTO reviews (reviewer_name, review, rating, product) VALUES (?, ?, ?, ?)',
        (reviewer_name, review, rating, product)
    )
    reviews_conn.commit()

    # Recalculate the average rating for the product in the reviews.db
    reviews_cursor.execute('SELECT AVG(rating) FROM reviews WHERE product = ?', (product,))
    avg_rating = reviews_cursor.fetchone()[0]

    # Connect to products.db to update the product's rating
    products_conn = sqlite3.connect('products.db')
    products_cursor = products_conn.cursor()

    # Update the product's rating in the products table
    if avg_rating is not None:  # Ensure that we got a valid average rating
        products_cursor.execute('UPDATE products SET rating = ? WHERE name = ?', (avg_rating, product))
        products_conn.commit()

    # Close both connections
    reviews_conn.close()
    products_conn.close()

    # Respond with a success message
    return jsonify({"message": "Review submitted successfully!"}), 200


@app.route('/apply_coupon', methods=['POST'])
def apply_coupon():
    data = request.get_json()
    coupon_code = data.get('coupon_code')

    if not coupon_code:
        return jsonify({"message": "No coupon code provided"}), 400

    conn = sqlite3.connect('coupons.db')
    cursor = conn.cursor()
    cursor.execute('SELECT discount FROM coupons WHERE code = ?', (coupon_code,))
    result = cursor.fetchone()
    conn.close()

    if result:
        discount = result[0]
        return jsonify({"message": "Coupon applied", "discount": discount}), 200
    else:
        return jsonify({"message": "Invalid coupon"}), 404

# Database initialization (run once)
def init_db():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            address TEXT,
            product TEXT
        )
    ''')
    conn.commit()
    conn.close()

class Order():
    def __init__(self, product, name, email, address):
        self.Product = product
        self.Name = name
        self.Email = email
        self.Address = address
        pass

if __name__ == '__main__':
    # init_db()  # Initialize the database
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0')
