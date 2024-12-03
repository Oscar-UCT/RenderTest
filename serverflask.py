from flask import Flask, request, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', products= None)

# Metodo para entregar los productos segun categoria
@app.route('/products', methods=['GET'])
def show_products():
    conn = sqlite3.connect('turismodatos.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    category = request.args.get('category')
    cursor.execute('SELECT * FROM Productos WHERE categoria = ?', (category,))

    products = cursor.fetchall()
    conn.close()

    return render_template('index.html', products=products)

@app.route('/order')
def buy_product():
    product_name = request.args.get('product')
    return render_template('order.html', product=product_name)

@app.route('/personal-data', methods=['POST'])
def final_confirmation():
    try:
        # Check if all required fields are present
        if not all(key in request.form for key in ['rut', 'name', 'email', 'address', 'product']):
            return "Missing required fields", 400

        # Create Client
        client = Cliente(request.form['rut'], request.form['name'], request.form['email'], request.form['address'])
   
        # Fetch Product Price
        product_conn = sqlite3.connect('turismodatos.db')
        cursor = product_conn.cursor()
        
        # Use parameterized query to prevent SQL injection
        cursor.execute('SELECT precio FROM Productos WHERE nombre = ?', (request.form['product'],))
        
        # Check if product exists
        result = cursor.fetchone()
        if result is None:
            product_conn.close()
            return "Product not found", 404
        
        price = result[0]
        product_conn.close()

        # Create Order and render confirmation template
        return render_template('confirm.html', Order=Order(
            request.form['product'], 
            price, 
            client.Rut, 
            client.Name, 
            client.Email, 
            client.Address
        ))
    
    except sqlite3.Error as e:
        # Handle database errors
        return f"Database error: {str(e)}", 500
    except Exception as e:
        # Catch any other unexpected errors
        return f"An error occurred: {str(e)}", 500

@app.route('/order-confirm', methods=['POST'])
def receive_order():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400
   
    order = Order(
        rut=data.get("rut"),
        name=data.get("name"),
        email=data.get("email"),
        address=data.get("address"),
        product=data.get("product"),
        total=data.get("total")
    )
    
    conn = sqlite3.connect('turismodatos.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Pedidos (rut, nombre, email, direccion, producto, total)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (order.Rut, order.Name, order.Email, order.Address, order.Product, order.Total))
    conn.commit()
    conn.close()
    
    return render_template("buy.html", Order=order)

# Método para guardar la reseña
@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.get_json()
    reviewer_name = data.get('reviewer_name')
    review = data.get('review')
    rating = data.get('rating')
    product = data.get('product_name')

    if not review or not product or rating is None:
        return jsonify({"message": "Invalid data"}), 400


    reviews_conn = sqlite3.connect('turismodatos.db')
    reviews_cursor = reviews_conn.cursor()
    reviews_cursor.execute(
        'INSERT INTO Reseñas (cliente_nombre, producto, comentario, clasificacion) VALUES (?, ?, ?, ?)',
        (reviewer_name, review, rating, product)
    )
    reviews_conn.commit()

    reviews_cursor.execute('SELECT AVG(clasificacion) FROM reseñas WHERE producto = ?', (product,))
    avg_rating = reviews_cursor.fetchone()[0]

    products_conn = sqlite3.connect('turismodatos.db')
    products_cursor = products_conn.cursor()

    if avg_rating is not None:
        products_cursor.execute('UPDATE productos SET clasificacion = ? WHERE nombre = ?', (avg_rating, product))
        products_conn.commit()

    reviews_conn.close()
    products_conn.close()


    return jsonify({"message": "Review submitted successfully!"}), 200


# Método para entregar cupón con su descuento
@app.route('/apply_coupon', methods=['POST'])
def apply_coupon():
    data = request.get_json()
    coupon_code = data.get('coupon_code')

    if not coupon_code:
        return jsonify({"message": "No coupon code provided"}), 400

    conn = sqlite3.connect('turismodatos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT descuento FROM Cupones WHERE codigo = ?', (coupon_code,))
    result = cursor.fetchone()
    conn.close()

    if result:
        discount = result[0]
        return jsonify({"message": "Coupon applied", "discount": discount}), 200
    else:
        return jsonify({"message": "Invalid coupon"}), 404

class Cliente():
    def __init__(self, rut, name, email, address):
        self.Rut = rut
        self.Name = name
        self.Email = email
        self.Address = address
        pass

class Order():
    def __init__(self, product, total, rut, name, email, address):
        self.Product = product
        self.Total = total
        self.Rut = rut
        self.Name = name
        self.Email = email
        self.Address = address
        pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
