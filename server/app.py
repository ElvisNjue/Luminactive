from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_cors import CORS
from werkzeug.security import check_password_hash
from  models import db, User, Product, Order,CartItem, Payment,Admin,Notification
# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Initialize db
db.init_app(app)

#Initialize Flask Migrate
migrate = Migrate(app, db)

# Home route
@app.route('/')
def home():
    return " API is running"

#signup route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({'error': 'Username or Email already exists'}), 409

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully!'}), 201

#Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and user.password == data['password']:
        return jsonify({
            'message': 'Login successful',
            'username': user.name,  # Return username
            'email': user.email,
            'id': user.id
        }), 200
    return jsonify({'message': 'Invalid credentials'}), 401


@app.route("/users/<int:id>", methods=["GET", "PUT"])
def handle_user(id):
    user = User.query.get_or_404(id)

    if request.method == "GET":
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })

    elif request.method == "PUT":
        data = request.json
        user.email = data.get("email", user.email)
        if "password" in data and data["password"]:
            user.password = data["password"]  
        db.session.commit()
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })

    
# Get all products
@app.route('/products', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products]), 200

# Get product by ID
@app.route('/products/<int:id>', methods=['GET'])
def get_product_by_id(id):
    product = Product.query.get(id)
    if product:
        return jsonify(product.to_dict()), 200
    else:
        return jsonify({"error": "Product not found"}), 404



# Search product by name or category
@app.route('/products/search', methods=['GET'])
def search_products():
    name = request.args.get('name')
    category = request.args.get('category')
    
    query = Product.query
    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))
    if category:
        query = query.filter_by(category=category)
    
    results = query.all()
    return jsonify([product.to_dict() for product in results])

# Get all users
@app.route('/admin/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    admin = Admin.query.filter_by(username=username).first()
    if admin and admin.check_password(password):
        return jsonify({'message': 'Login successful', 'is_admin': True}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/register-admin', methods=['POST'])
def register_admin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if Admin.query.filter_by(username=username).first():
        return jsonify({'message': 'Admin already exists'}), 400

    new_admin = Admin(username=username)
    new_admin.set_password(password)
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({'message': 'Admin registered successfully'}), 201


@app.route('/admin/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "description": p.description,
        "price": p.price,
        "quantity": p.quantity,
        "size": p.size,
        "image_url": p.image_url
    } for p in products])

@app.route('/admin/products', methods=['POST'])
def add_product():
    data = request.json
    new_product = Product(
        name=data.get("name"),
        price=data.get("price"),
        size=data.get("size"),
        quantity=data.get("quantity"),
        description=data.get("description"),
        image_url=data.get("image_url"),
        category=data.get("category")
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added"}), 201

@app.route('/admin/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})



# ----------------- ORDER ROUTES -----------------

@app.route('/admin/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([
        {
            "id": o.id,
            "product_id": o.product_id,
            "customer_name": o.customer_name,
            "quantity": o.quantity,
            "total_price": o.total_price
        }
        for o in orders
    ])


# ----------------- USER ROUTES -----------------

@app.route('/admin/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'phone_number': u.phone_number,
        'city': u.city,
        'address': u.address,
        'payment_method': u.payment_method,
        'password': u.password_hash
    } for u in users])


# ----------------- NOTIFICATION ROUTES ----------------
@app.route('/admin/notify', methods=['POST'])
def send_notification():
    data = request.get_json()
    user_id = data.get('user_id')
    message = data.get('message')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    if user_id == 'all':
        users = User.query.all()
        for user in users:
            notification = Notification(user_id=user.id, message=message)
            db.session.add(notification)
        db.session.commit()
        return jsonify({'message': 'Notification sent to all users'}), 200

    else:
        notification = Notification(user_id=user_id, message=message)
        db.session.add(notification)
        db.session.commit()
        return jsonify({'message': f'Notification sent to user {user_id}'}), 200

#orders
@app.route('/orders/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    order_list = [
        {
            "id": order.id,
            "items": order.items,  # Make sure items are JSON serializable
            "total_price": order.total_price,
            "status": order.status,
            "date": order.date.strftime('%Y-%m-%d')
        }
        for order in orders
    ]
    return jsonify(order_list), 200

@app.route('/place-order', methods=['POST'])
def place_order():
    data = request.get_json()

    try:
        new_order = Order(
            user_id=data['user_id'],
            items=data['items'],  # make sure this is JSON serializable
            total_price=data['total_price'],
            status='Pending',  # you can change this as needed
            date=datetime.utcnow()  # import datetime from datetime
        )

        db.session.add(new_order)
        db.session.commit()

        return jsonify({'message': 'Order placed successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400


#cart
@app.route('/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    # Check if product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Create and save CartItem
    cart_item = CartItem(product_id=product_id, quantity=quantity)
    db.session.add(cart_item)
    db.session.commit()

    return jsonify({
        "message": "Item added to cart",
        "cart_item": {
            "id": cart_item.id,
            "product_id": product_id,
            "quantity": quantity
        }
    }), 201


@app.route('/cart', methods=['GET'])
def view_cart():
    cart_items = CartItem.query.all()
    result = [
        {
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "image_url": item.product.image_url,
            "price": item.product.price,
            "quantity": item.quantity,
            "total_price": item.product.price * item.quantity  # calculated here
        }
        for item in cart_items
    ]
    return jsonify(result), 200



@app.route('/cart/<int:item_id>', methods=['DELETE'])
def delete_cart_item(item_id):
    # Logic to delete from cart
    return jsonify({"message": f"Item {item_id} removed"}), 200

@app.route('/cart/<int:item_id>', methods=['PATCH'])
def update_cart_item(item_id):
    data = request.get_json()
    quantity = data.get('quantity')
    # Update logic here
    return jsonify({"message": "Quantity updated", "item_id": item_id, "quantity": quantity})







@app.route('/payments', methods=['POST'])
def create_payment():
    data = request.json
    payment = Payment(
        order_id=data['order_id'],
        method=data['method'],
        paid=data.get('paid', False),
        date_paid=datetime.utcnow() if data.get('paid') else None
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({"message": "Payment created"}), 201


@app.route('/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.all()
    result = []
    for p in payments:
        result.append({
            "id": p.id,
            "order_id": p.order_id,
            "method": p.method,
            "paid": p.paid,
            "date_paid": p.date_paid
        })
    return jsonify(result)


@app.route('/payments/<int:id>', methods=['GET'])
def get_payment(id):
    payment = Payment.query.get_or_404(id)
    return jsonify({
        "id": payment.id,
        "order_id": payment.order_id,
        "method": payment.method,
        "paid": payment.paid,
        "date_paid": payment.date_paid
    })


@app.route('/payments/<int:id>', methods=['PUT'])
def update_payment(id):
    payment = Payment.query.get_or_404(id)
    data = request.json
    payment.method = data.get('method', payment.method)
    payment.paid = data.get('paid', payment.paid)
    if payment.paid:
        payment.date_paid = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Payment updated"})


@app.route('/payments/<int:id>', methods=['DELETE'])
def delete_payment(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    return jsonify({"message": "Payment deleted"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables if they don't exist
        print("Database created successfully")
    app.run(debug=True)



