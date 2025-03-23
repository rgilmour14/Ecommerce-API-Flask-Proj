E-commerce API Project

Project Description:
A fully-functional e-commerce API built using Flask, Flask-SQLAlchemy, Flask-Marshmallow and MySQL. The API allows the management of Users, Orders and Products. These models are set up with relationships, One-to-Many and Many-To-Many associations. One-to-Many allows a user to place multiple orders. Many-to-Many can allow a order to have multiple products, in which a product can belong to multiple orders. Serialization is implemented with Marshmallow and CRUD endpoints. 

User endpoints include:
Retrieve all users
Retrieve a user by ID
Create a new user
Update a user by ID
Delete a user by ID

Product endpoints include:
Retrieve all products
Retrieve a product by ID
Create a new product
Update a product by ID
Delete a product by ID

Order endpoints include:
Create a new order with user ID and order date
Add a product to an order (prevent duplicates)
Remove a product from an order
Get all orders for a user



How to Install and Run the Project:
Open Python and run the app.py file
Open SQL Workbench and the database ecommerce_api
Open Postman 

How to Use the Project:
Create a new Workspace in Postman
Provide the URL for the task you want to perform
Select body and make sure raw and JSON is selected.
Input the data in the body and click on send.
The results will appear at the bottom of the Postman screen and in SQL Workbench
View the tables in SQL to see results


