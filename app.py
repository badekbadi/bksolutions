from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
CORS(app)

# Przykładowe produkty
PRODUCTS = [
    {
        'id': 1,
        'name': 'Laptop Dell XPS 13',
        'price': 4999.99,
        'image': 'https://via.placeholder.com/300x200?text=Laptop+Dell+XPS+13',
        'description': 'Wysokiej jakości ultrabook z procesorem Intel Core i7'
    },
    {
        'id': 2,
        'name': 'Smartphone Samsung Galaxy S24',
        'price': 3499.99,
        'image': 'https://via.placeholder.com/300x200?text=Samsung+Galaxy+S24',
        'description': 'Najnowszy flagowy smartphone z aparatem 200MP'
    },
    {
        'id': 3,
        'name': 'Słuchawki Sony WH-1000XM5',
        'price': 1299.99,
        'image': 'https://via.placeholder.com/300x200?text=Sony+WH-1000XM5',
        'description': 'Bezprzewodowe słuchawki z redukcją szumów'
    },
    {
        'id': 4,
        'name': 'Tablet iPad Pro 12.9"',
        'price': 5999.99,
        'image': 'https://via.placeholder.com/300x200?text=iPad+Pro+12.9',
        'description': 'Profesjonalny tablet z ekranem Liquid Retina XDR'
    },
    {
        'id': 5,
        'name': 'Kamera Canon EOS R5',
        'price': 8999.99,
        'image': 'https://via.placeholder.com/300x200?text=Canon+EOS+R5',
        'description': 'Profesjonalna kamera bezlusterkowa 45MP'
    },
    {
        'id': 6,
        'name': 'Smartwatch Apple Watch Ultra',
        'price': 3499.99,
        'image': 'https://via.placeholder.com/300x200?text=Apple+Watch+Ultra',
        'description': 'Zaawansowany smartwatch dla aktywnych użytkowników'
    }
]

# Inicjalizacja koszyka w sesji
def init_cart():
    if 'cart' not in session:
        session['cart'] = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/products')
def get_products():
    return jsonify(PRODUCTS)

@app.route('/api/product/<int:product_id>')
def get_product(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({'error': 'Produkt nie znaleziony'}), 404

@app.route('/api/cart', methods=['GET'])
def get_cart():
    init_cart()
    cart_items = []
    total = 0
    
    for cart_item in session['cart']:
        product = next((p for p in PRODUCTS if p['id'] == cart_item['product_id']), None)
        if product:
            item_total = product['price'] * cart_item['quantity']
            cart_items.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': cart_item['quantity'],
                'total': item_total,
                'image': product['image']
            })
            total += item_total
    
    return jsonify({
        'items': cart_items,
        'total': total,
        'count': sum(item['quantity'] for item in session['cart'])
    })

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    init_cart()
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    # Sprawdź czy produkt istnieje
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return jsonify({'error': 'Produkt nie znaleziony'}), 404
    
    # Sprawdź czy produkt już jest w koszyku
    existing_item = next((item for item in session['cart'] if item['product_id'] == product_id), None)
    
    if existing_item:
        existing_item['quantity'] += quantity
    else:
        session['cart'].append({
            'product_id': product_id,
            'quantity': quantity
        })
    
    session.modified = True
    return jsonify({'message': 'Produkt dodany do koszyka'})

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    init_cart()
    data = request.json
    product_id = data.get('product_id')
    
    session['cart'] = [item for item in session['cart'] if item['product_id'] != product_id]
    session.modified = True
    
    return jsonify({'message': 'Produkt usunięty z koszyka'})

@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    init_cart()
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    if quantity <= 0:
        return remove_from_cart()
    
    for item in session['cart']:
        if item['product_id'] == product_id:
            item['quantity'] = quantity
            break
    
    session.modified = True
    return jsonify({'message': 'Koszyk zaktualizowany'})

@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    session['cart'] = []
    session.modified = True
    return jsonify({'message': 'Koszyk wyczyszczony'})

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json
    
    # Walidacja danych
    required_fields = ['name', 'email', 'message']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Pole {field} jest wymagane'}), 400
    
    # Tutaj normalnie zapisałbyś do bazy danych lub wysłał email
    contact_data = {
        'name': data['name'],
        'email': data['email'],
        'phone': data.get('phone', ''),
        'message': data['message'],
        'timestamp': datetime.now().isoformat()
    }
    
    # Symulacja zapisu do pliku (w prawdziwej aplikacji użyj bazy danych)
    try:
        with open('contacts.json', 'a') as f:
            f.write(json.dumps(contact_data, ensure_ascii=False) + '\n')
    except:
        pass
    
    return jsonify({'message': 'Dziękujemy za wiadomość! Skontaktujemy się wkrótce.'})

@app.route('/api/checkout', methods=['POST'])
def checkout():
    init_cart()
    data = request.json
    
    if not session['cart']:
        return jsonify({'error': 'Koszyk jest pusty'}), 400
    
    # Walidacja danych zamówienia
    required_fields = ['name', 'email', 'address', 'city', 'postal_code']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Pole {field} jest wymagane'}), 400
    
    # Oblicz całkowitą kwotę
    total = 0
    order_items = []
    for cart_item in session['cart']:
        product = next((p for p in PRODUCTS if p['id'] == cart_item['product_id']), None)
        if product:
            item_total = product['price'] * cart_item['quantity']
            total += item_total
            order_items.append({
                'product_id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': cart_item['quantity'],
                'total': item_total
            })
    
    # Stwórz zamówienie
    order_data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'customer': {
            'name': data['name'],
            'email': data['email'],
            'phone': data.get('phone', ''),
            'address': data['address'],
            'city': data['city'],
            'postal_code': data['postal_code']
        },
        'items': order_items,
        'total': total,
        'timestamp': datetime.now().isoformat()
    }
    
    # Symulacja zapisu zamówienia
    try:
        with open('orders.json', 'a') as f:
            f.write(json.dumps(order_data, ensure_ascii=False) + '\n')
    except:
        pass
    
    # Wyczyść koszyk
    session['cart'] = []
    session.modified = True
    
    return jsonify({
        'message': 'Zamówienie zostało złożone!',
        'order_id': order_data['id'],
        'total': total
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)