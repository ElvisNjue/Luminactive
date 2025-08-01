from app import app
from models import db, Product, Order,User, CartItem,Admin

def seed_data():
 with app.app_context():
    db.drop_all()
    db.create_all()

# Create admin user
    if not Admin.query.filter_by(name="admin").first():
        admin = Admin(name="admin")
        admin.set_password("admin123")  # You can change this
        db.session.add(admin)
        db.session.commit()
        print("Admin seeded.")
    else:
        print("Admin already exists.")


    # Users
    users = [
        User(username="Alice Muthoni", email="alice@example.com", password="Alice"),
        User(username="Brian Odhiambo", email="brian@example.com", password="Odhiambo"),
        User(username="Clara Wanjiku", email="clara@example.com", password="Wanjiku"),
    ]
    db.session.add_all(users)
    db.session.commit()


    #products
    products = [
    Product(
        name="Men's Running Shoes",
        category="men",
        description="Lightweight shoes designed for speed and comfort.",
        size="42",
        price=4500,
        image_url="/assets/istockphoto-1147262946-1024x1024.jpg"  
    ),
    Product(
        name="Women's Sports Bra",
        category="women",
        description="Comfortable and supportive for all activities.",
        size="M",
        price=2500,
        image_url="/assets/istockphoto-1401527512-1024x1024.jpg"  
    ),
    Product(
        name="Kids' Training Shoes",
        category="kids",
        description="Durable and flexible for everyday training.",
        size="10",
        price=1200,
        image_url="/assets/istockphoto-859996178-1024x1024.jpg"  
    ),
    Product(
            name="Real Madrid Jersey",
            category="unisex",
            description="Official Modrić #10 Real Madrid home jersey.",
            size="L",
            price=3500,
            image_url="/assets/real madrid jersey.jpg"
    ),
    Product(
            name="Black Football Boots",
            category="unisex",
            description="Classic black leather football boots with studs.",
            size="42",
            price=5000,
            image_url="/assets/black football boots.jpg"
    ),
    Product(
        name="Barcelona jersey",
        category="unisex",
        description="Official Messi #10 Barcelona home jersey.",
        size="L",
        price=3500,
        image_url="/assets/barcelona jersey.jpg",
    ),
    Product(
        name="Black shoes",
        category="unisex",
        description="Light weight shoes designed to run ",
        size="42",
        price=3500,
        image_url="/assets/black shoes.jpg"
    ),
    Product(
        name="White Leggings",
        category="women",
        description="comfortable for workout and running",
        size="M",
        price=2500,
        image_url="/assets/white leggings.jpg"
    ),
    Product(
        name="Black Leggings",
        category="women",
        description="comfortable for workingout and for waling",
        size="M",
        price="2300",
        image_url="/assets/balck leggings.jpg"
    ),
    Product(
        name="Blue football boots",
        category="unisex",
        description="designed for maximum comfort",
        size="44",
        price=2800,
        image_url="/assets/blue football boots.jpg"
    ),
    Product(
        name="white shoes",
        category="unisex",
        description="Made for maximum comfort",
        size="43",
        price=2500,
        image_url="/assets/white shoes.jpg"
    ),
    Product(
        name="white shoes",
        category="unisex",
        description="Made for durability",
        size="45",
        price=3000,
        image_url="/assets/istockphoto-1688015574-612x612.jpg"
    )

]

    db.session.add_all(products)
    db.session.commit()

    # Cart Items
    cart_items = [
        CartItem(user_id=users[0].id, product_id=products[0].id, quantity=1),
        CartItem(user_id=users[1].id, product_id=products[1].id, quantity=2),
        CartItem(user_id=users[2].id, product_id=products[2].id, quantity=3)
    ]
    db.session.add_all(cart_items)
    db.session.commit()
    
    # Create orders
    orders = [
        Order(customer_name="Alice Muthoni", user_id=users[0].id, product_id=products[0].id,
              quantity=2, total_price=5600),
        Order(customer_name="Brian Odhiambo", user_id=users[1].id, product_id=products[1].id,
              quantity=1, total_price=2500),
        Order(customer_name="Clara Wanjiku", user_id=users[2].id, product_id=products[2].id,
              quantity=3, total_price=2400),
    ]
    db.session.add_all(orders)
    db.session.commit()

    print(" Admin,Users, products, Cart Item and orders seeded successfully!")
    
    

