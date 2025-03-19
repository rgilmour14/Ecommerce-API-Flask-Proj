from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey, Table, Column, String, Integer, Delete
from datetime import date
from typing import List
from marshmallow import ValidationError, fields
from sqlalchemy import select, delete

# Initialize Flask app
app = Flask(__name__)

# MySQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:SunflowerShan14!@localhost/ecommerce_api'

# Creating our Base Model
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)

#===========================MODELS===============================

# User Table
class User(Base):
    __tablename__ = "User"
    
    # Columns
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(200), nullable=False)
    address: Mapped[str] = mapped_column(db.String(200))
    email: Mapped[str] = mapped_column(db.String(200))
    
    # one to many relationship => one user to many orders
    orders: Mapped[List["Orders"]] = db.relationship(back_populates='user')

# Association table for many to many relationships
order_products = db.Table(
    "Order_Products",
    Base.metadata,
    db.Column('order_id', db.ForeignKey('orders.id')),
    db.Column('product_id', db.ForeignKey('products.id'))    
)

# Order Table
class Orders(Base):
    __tablename__ = "orders"
    
    # Columns
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('User.id'))
    
    # one to many relationship to the user table
    user: Mapped['User'] = db.relationship(back_populates='orders')
    products: Mapped[List['Products']] = db.relationship(secondary=order_products, back_populates="orders")


# Product Table
class Products(Base):
    __tablename__ = "products"

    # Columns
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(db.String(225), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    orders: Mapped[List['Orders']] = db.relationship(secondary=order_products, back_populates='products')
    
    
# Initialize the database and create tables
with app.app_context():
    # db.drop_all()
    db.create_all()    
        

#===========================SCHEMAS===============================

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Products
    
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        include_fk = True
        
user_schema = UserSchema()
users_schema = UserSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

@app.route('/')
def home():
    return "Home"

#===========================API ROUTES: User CRUD===============================

# Get all users using a GET method
@app.route("/users", methods=['GET'])
def get_users():
    query = select(User)
    result = db.session.execute(query).scalars()
    users = result.all()
    return users_schema.jsonify(users)

# Get specific user using GET method
@app.route("/users/<int:id>", methods=['GET'])
def get_user(id):
    query = select(User).where(User.id == id)
    result = db.session.execute(query).scalars().first()
    
    if result is None:
        return jsonify({"Error": "User not found"}), 404
    return user_schema.jsonify(result)

# Create users with POST request
@app.route("/users", methods=['POST'])
def add_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_user = User(name=user_data['name'], email=user_data['email'], address=user_data['address'])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"Message": "New User added successfully",
                    "user": user_schema.dump(new_user)}), 201
    
# Update a specific user with PUT request
@app.route("/users/<int:id>", methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)
    
    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    user.name = user_data['name']
    user.email = user_data['email']
    user.address = user_data['address']
    
    db.session.commit()
    return user_schema.jsonify(user), 200
    
# Remove a specific user with DELETE request 
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"successfully deleted user {id}"}), 200
    
#===========================API ROUTES: Products CRUD===============================
    
# Get all products using GET method        
@app.route("/products", methods=['GET'])
def get_products():
    query = select(Products)
    result = db.session.execute(query).scalars()
    products = result.all()
    return products_schema.jsonify(products)

# Get specific product using GET method
@app.route("/products/<int:id>", methods=['GET'])
def get_product(id):
    query = select(Products).where(Products.id == id)
    result = db.session.execute(query).scalars().first()
    
    if result is None:
        return jsonify({"Error": "Product not found"}), 404
    return product_schema.jsonify(result)
   
# Create products with POST request
@app.route("/products", methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_product = Products(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"Messages": "New product added!",
                    "product": product_schema.dump(new_product)}), 201

# Update a specific product with PUT request
@app.route("/products/<int:id>", methods=['PUT'])
def update_product(id):
    product = db.session.get(Products, id)
    
    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.product_name = product_data['product_name']
    product.price = product_data['price']
    
    db.session.commit()
    return user_schema.jsonify(product), 200

# Remove a specific product with DELETE request 
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Products, id)

    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"successfully deleted product {id}"}), 200

#=====================API ROUTES: Order Operations=================================
# CREATE an ORDER
@app.route('/orders', methods=['POST'])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Retrieve the user by its id.
    user = db.session.get(User, order_data['user_id'])
    
    # Check if the user exists.
    if user:
        new_order = Orders(order_date = order_data['order_date'], user_id = order_data['user_id'])

        db.session.add(new_order)
        db.session.commit()

        return jsonify({"Message": "New Order Placed!",
                        "order": order_schema.dump(new_order)}), 201
    else:
        return jsonify({"message": "Invalid user id"}), 400

# ADD ITEM TO ORDER
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product(order_id, product_id):
    order = db.session.get(Orders, order_id) 
    product = db.session.get(Products, product_id)

    if order and product: # check to see if both exist
        if product not in order.products: # Ensure the product is not already on the order
            order.products.append(product) # create relationship from order to product
            db.session.commit() 
            return jsonify({"Message": "Successfully added item to order."}), 200
        else: # Product is in order.products
            return jsonify({"Message": "Item is already included in this order."}), 400
    else: # order or product does not exist
        return jsonify({"Message": "Invalid order id or product id."}), 400
    
# # Deleting a product from an Order 
# @app.route("/orders/<int:order_id>/remove_product", methods=['DELETE'])
# def delete_product(id):
#     product = db.session.get(Products, id)

#     if not product:
#         return jsonify({"message": "Invalid product id"}), 400
    
#     db.session.delete(product)
#     db.session.commit()
#     return jsonify({"message": f"successfully deleted product {id}"}), 200

# Get all Orders for a User
# @app.route('/orders/user/<int:user_id>', methods=['GET'])
# def get_user_order(user_id, order_id):
#     user = db.session.get(User, user_id)
#     order = db.session.get(Orders, order_id) 


#     if order and product: # check to see if both exist
#         if product not in order.products: # Ensure the product is not already on the order
#             order.products.append(product) # create relationship from order to product
#             db.session.commit() 
#             return jsonify({"Message": "Successfully added item to order."}), 200
#         else: # Product is in order.products
#             return jsonify({"Message": "Item is already included in this order."}), 400
#     else: # order or product does not exist
#         return jsonify({"Message": "Invalid order id or product id."}), 400
    
if __name__ == '__main__':
    app.run(debug=True)        
    


orders.user_id
        
                

