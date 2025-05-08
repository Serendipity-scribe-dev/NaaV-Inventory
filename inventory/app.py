# 💡Importing all the packages
from flask import Flask, render_template, request, redirect,session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
import os
import csv
import google.generativeai as genai

# 💡Loading the environment varibales
load_dotenv()

# 💡Getting the API Key from environment variable
# GEMINI_API_URL = 'https://api.gemini.com/v1/chat'
API_KEY = os.getenv('GEMINI_API_KEY')

# 💡Configuring the 
genai.configure(api_key = API_KEY)

# 💡Seeting the flask app and configuring the database for the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config["SECRET_KEY"] = "hjhjsdahhds"
db = SQLAlchemy(app)
socketio = SocketIO(app)


# 💡Creating the class instacne for each table in the Database inventory.db
class Product(db.Model):
    __tablename__ = 'products'
    product_id      = db.Column(db.String(200), primary_key=True)
    quantity = db.Column(db.Integer)
    category = db.Column(db.String(50))
    price = db.Column(db.Float)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<Product %r>' % self.product_id
    
class Location(db.Model):
    __tablename__   = 'locations'
    location_id     = db.Column(db.String(200), primary_key=True)
    date_created    = db.Column(db.DateTime, default=datetime.utcnow)
  
    def __repr__(self):
        return '<Location %r>' % self.location_id
    
class ProductMovement(db.Model):
    __tablename__   = 'productmovements'
    movement_id     = db.Column(db.Integer, primary_key=True)
    product_id      = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    qty             = db.Column(db.Integer)
    from_location   = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    to_location     = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    movement_time   = db.Column(db.DateTime, default=datetime.utcnow)
    product         = db.relationship('Product', foreign_keys=product_id)
    fromLoc         = db.relationship('Location', foreign_keys=from_location)
    toLoc           = db.relationship('Location', foreign_keys=to_location)
  
    def __repr__(self):
        return '<ProductMovement %r>' % self.movement_id
  
class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<Supplier %r>' % self.name

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(100), nullable=False, unique=True)  # Add customer_id field
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<Customer %r>' % self.name

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(200), db.ForeignKey('products.product_id'), nullable=False)
    customer_id = db.Column(db.String(100), db.ForeignKey('customers.customer_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    product = db.relationship('Product', backref=db.backref('sales', lazy=True))
    customer = db.relationship('Customer', backref=db.backref('sales', lazy=True))

    def __repr__(self):
        return f'<Sale {self.id}>'


# 💡Route and Function to Add a new product 
@app.route('/', methods=["POST", "GET"])
def index():
      
    if (request.method == "POST") and ('product_name' in request.form):
        product_name    = request.form["product_name"]
        new_product     = Product(product_id=product_name)
        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect("/")
      
        except:
            return "There Was an issue while add a new Product"
  
    if (request.method == "POST") and ('location_name' in request.form):
        location_name    = request.form["location_name"]
        new_location     = Location(location_id=location_name)
        try:
            db.session.add(new_location)
            db.session.commit()
            return redirect("/")
      
        except:
            return "There Was an issue while add a new Location"
    else:
        products    = Product.query.order_by(Product.date_created).all()
        locations   = Location.query.order_by(Location.date_created).all()
        return render_template("index.html", products = products, locations = locations)
    
# 💡Route and Function to View Location
@app.route('/locations/', methods=["POST", "GET"])
def viewLocation():
    if (request.method == "POST") and ('location_name' in request.form):
        location_name = request.form["location_name"]
        new_location = Location(location_id=location_name)
        try:
            db.session.add(new_location)
            db.session.commit()
            return redirect("/locations/")
        except:
            locations = Location.query.order_by(Location.date_created).all()
            return "There Was an issue while add a new Location"
    else:
        locations = Location.query.order_by(Location.date_created).all()
        return render_template("locations.html", locations=locations)
    
# 💡Route and Function to View Product
@app.route('/products/', methods=["POST", "GET"])
def viewProduct():
    if (request.method == "POST") and ('product_name' in request.form):
        product_name = request.form["product_name"]
        quantity = request.form["quantity"]
        category = request.form["category"]
        price = request.form["price"]
        new_product = Product(product_id=product_name,quantity=quantity,category=category,price=price)
        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect("/products/")
        except:
            products = Product.query.order_by(Product.date_created).all()
            return "There Was an issue while add a new Product"
    else:
        products = Product.query.order_by(Product.date_created).all()
        return render_template("products.html", products=products)

# 💡Route and Function to Update Product
@app.route("/update-product/<name>", methods=["POST", "GET"])
def updateProduct(name):
    product = Product.query.get_or_404(name)
    old_porduct = product.product_id
    if request.method == "POST":
        product.product_id    = request.form['product_name']
        try:
            db.session.commit()
            updateProductInMovements(old_porduct, request.form['product_name'])
            return redirect("/products/")
        except:
            return "There was an issue while updating the Product"
    else:
        return render_template("update-product.html", product=product)

# 💡Route and Function to Delete Product
@app.route("/delete-product/<name>")
def deleteProduct(name):
    product_to_delete = Product.query.get_or_404(name)
    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        return redirect("/products/")
    except:
        return "There was an issue while deleteing the Product"
  
# 💡Route and Function to Update Location
@app.route("/update-location/<name>", methods=["POST", "GET"])
def updateLocation(name):
    location = Location.query.get_or_404(name)
    old_location = location.location_id
    if request.method == "POST":
        location.location_id = request.form['location_name']
        try:
            db.session.commit()
            updateLocationInMovements(
                old_location, request.form['location_name'])
            return redirect("/locations/")
        except:
            return "There was an issue while updating the Location"
    else:
        return render_template("update-location.html", location=location)

# 💡Route and Function to Delete Location
@app.route("/delete-location/<name>")
def deleteLocation(name):
    location_to_delete = Location.query.get_or_404(name)
    try:
        db.session.delete(location_to_delete)
        db.session.commit()
        return redirect("/locations/")
    except Exception as e:
        return f"There was an issue while deleting the Location: {str(e)}"

# 💡Route and Function to View Product Movements
@app.route("/movements/", methods=["POST", "GET"])
def viewMovements():
    if request.method == "POST" :
        product_id      = request.form["productId"]
        qty             = request.form["qty"]
        fromLocation    = request.form["fromLocation"]
        toLocation      = request.form["toLocation"]
        new_movement = ProductMovement(
            product_id=product_id, qty=qty, from_location=fromLocation, to_location=toLocation)
        try:
            db.session.add(new_movement)
            db.session.commit()
            return redirect("/movements/")
        except:
            return "There Was an issue while add a new Movement"
    else:
        products    = Product.query.order_by(Product.date_created).all()
        locations   = Location.query.order_by(Location.date_created).all()
        movs = ProductMovement.query\
        .join(Product, ProductMovement.product_id == Product.product_id)\
        .add_columns(
            ProductMovement.movement_id,
            ProductMovement.qty,
            Product.product_id, 
            ProductMovement.from_location,
            ProductMovement.to_location,
            ProductMovement.movement_time)\
        .all()
        movements   = ProductMovement.query.order_by(
            ProductMovement.movement_time).all()
        return render_template("movements.html", movements=movs, products=products, locations=locations)

# 💡Route and Function to Update Product Movements
@app.route("/update-movement/<int:id>", methods=["POST", "GET"])
def updateMovement(id):
    movement    = ProductMovement.query.get_or_404(id)
    products    = Product.query.order_by(Product.date_created).all()
    locations   = Location.query.order_by(Location.date_created).all()
    if request.method == "POST":
        movement.product_id  = request.form["productId"]
        movement.qty         = request.form["qty"]
        movement.from_location= request.form["fromLocation"]
        movement.to_location  = request.form["toLocation"]
        try:
            db.session.commit()
            return redirect("/movements/")
        except:
            return "There was an issue while updating the Product Movement"
    else:
        return render_template("update-movement.html", movement=movement, locations=locations, products=products)

# 💡Route and Function to Delete Product Movements
@app.route("/delete-movement/<int:id>")
def deleteMovement(id):
    movement_to_delete = ProductMovement.query.get_or_404(id)
    try:
        db.session.delete(movement_to_delete)
        db.session.commit()
        return redirect("/movements/")
    except:
        return "There was an issue while deleteing the Prodcut Movement"

# 💡Route and Function of Product Balance Report
@app.route("/product-balance/", methods=["POST", "GET"])
def productBalanceReport():
    movs = ProductMovement.query.\
        join(Product, ProductMovement.product_id == Product.product_id).\
        add_columns(
            Product.product_id, 
            ProductMovement.qty,
            ProductMovement.from_location,
            ProductMovement.to_location,
            ProductMovement.movement_time).\
        order_by(ProductMovement.product_id).\
        order_by(ProductMovement.movement_id).\
        all()
  
    balancedDict = defaultdict(lambda: defaultdict(dict))
    tempProduct = ''
    for mov in movs:
        row = mov[0]
        if(tempProduct == row.product_id):
            if(row.to_location and not "qty" in balancedDict[row.product_id][row.to_location]):
                balancedDict[row.product_id][row.to_location]["qty"] = 0
            elif (row.from_location and not "qty" in balancedDict[row.product_id][row.from_location]):
                balancedDict[row.product_id][row.from_location]["qty"] = 0
            if (row.to_location and "qty" in balancedDict[row.product_id][row.to_location]):
                balancedDict[row.product_id][row.to_location]["qty"] += row.qty
            if (row.from_location and "qty" in balancedDict[row.product_id][row.from_location]):
                balancedDict[row.product_id][row.from_location]["qty"] -= row.qty
        else:
            tempProduct = row.product_id
            if(row.to_location and not row.from_location):
                balancedDict[row.product_id][row.to_location]["qty"] = row.qty
    balancedDict = {k: dict(v) for k, v in balancedDict.items()}
    return render_template("product-balance.html", movements=balancedDict)

# 💡Route and Function to Get Location
@app.route("/movements/get-from-locations/", methods=["POST"])
def getLocations():
    product = request.form["productId"]
    location = request.form["location"]
    locationDict = defaultdict(lambda: defaultdict(dict))
    locations = ProductMovement.query.\
        filter( ProductMovement.product_id == product).\
        filter(ProductMovement.to_location != '').\
        add_columns(ProductMovement.from_location, ProductMovement.to_location, ProductMovement.qty).\
        all()
    for key, location in enumerate(locations):
        if(locationDict[location.to_location] and locationDict[location.to_location]["qty"]):
            locationDict[location.to_location]["qty"] += location.qty
        else:
            locationDict[location.to_location]["qty"] = location.qty
    return locationDict

# 💡Route and Function to get Duplicate Locations
@app.route("/dub-locations/", methods=["POST", "GET"])
def getDublicate():
    location = request.form["location"]
    locations = Location.query.\
        filter(Location.location_id == location).\
        all()
    print(locations)
    if locations:
        return {"output": False}
    else:
        return {"output": True}

# 💡Route and Function to get Duplicate Product and Upadte Location and Product Movements
@app.route("/dub-products/", methods=["POST", "GET"])
def getPDublicate():
    product_name = request.form["product_name"]
    products = Product.query.\
        filter(Product.product_id == product_name).\
        all()
    print(products)
    if products:
        return {"output": False}
    else:
        return {"output": True}
def updateLocationInMovements(oldLocation, newLocation):
    movement = ProductMovement.query.filter(ProductMovement.from_location == oldLocation).all()
    movement2 = ProductMovement.query.filter(ProductMovement.to_location == oldLocation).all()
    for mov in movement2:
        mov.to_location = newLocation
    for mov in movement:
        mov.from_location = newLocation
   
    db.session.commit()
    
def updateProductInMovements(oldProduct, newProduct):
    movement = ProductMovement.query.filter(ProductMovement.product_id == oldProduct).all()
    for mov in movement:
        mov.product_id = newProduct
  
    db.session.commit()


# 💡Route and Function to View Suppliers
@app.route("/suppliers/", methods=["POST", "GET"])
def viewSuppliers():
    if request.method == "POST":
        supplier_id = request.form["supplier_id"]
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
      
        new_supplier = Supplier(supplier_id=supplier_id, name=name, phone=phone, email=email)
        try:
            db.session.add(new_supplier)
            db.session.commit()
            return redirect("/suppliers/")
        except:
            return "There was an issue while adding a new Supplier"
    else:
        suppliers = Supplier.query.order_by(Supplier.date_created).all()
        return render_template("suppliers.html", suppliers=suppliers)

# 💡Route and Function to Update Suppliers
@app.route("/update-supplier/<int:id>", methods=["POST", "GET"])
def updateSupplier(id):
    supplier = Supplier.query.get_or_404(id)
    if request.method == "POST":
        supplier.supplier_id = request.form["supplier_id"]
        supplier.name = request.form["name"]
        supplier.phone = request.form["phone"]
        supplier.email = request.form["email"]
        try:
            db.session.commit()
            return redirect("/suppliers/")
        except:
            return "There was an issue while updating the Supplier"
    else:
        return render_template("update-supplier.html", supplier=supplier)

# 💡Route and Function to View Customers
@app.route("/customers/", methods=["POST", "GET"])
def viewCustomers():
    if request.method == "POST":
        customer_id = request.form["customer_id"]
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        new_customer = Customer(customer_id=customer_id, name=name, phone=phone, email=email)
        try:
            db.session.add(new_customer)
            db.session.commit()
            return redirect("/customers/")
        except:
            return "There was an issue while adding a new Customer"
    else:
        customers = Customer.query.order_by(Customer.date_created).all()
        return render_template("customers.html", customers=customers)

# 💡Route and Function to Update Customers
@app.route("/update-customer/<int:id>", methods=["POST", "GET"])
def updateCustomer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == "POST":
        customer.customer_id = request.form["customer_id"]
        customer.name = request.form["name"]
        customer.phone = request.form["phone"]
        customer.email = request.form["email"]
        try:
            db.session.commit()
            return redirect("/customers/")
        except:
            return "There was an issue while updating the Customer"
    else:
        return render_template("update-customer.html", customer=customer)

# 💡Route and Function to Delete Customers
@app.route("/delete-customer/<int:id>")
def deleteCustomer(id):
    customer_to_delete = Customer.query.get_or_404(id)
    try:
        db.session.delete(customer_to_delete)
        db.session.commit()
        return redirect("/customers/")
    except:
        return "There was an issue while deleting the Customer"

# 💡Route and Function to View Sales
@app.route("/sales/", methods=["POST", "GET"])
def viewSales():
    if request.method == "POST":
        product_id = request.form["product_id"]
        customer_id = request.form["customer_id"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        date_str = request.form["date"]
        
        # Convert date string to date object
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError as e:
            return f"There was an issue with the date format: {str(e)}"
        
        # Get the product and check stock
        product = Product.query.get(product_id)
        if product is None:
            return "Product not found."

        # Calculate total sold and remaining stock
        total_sold = db.session.query(db.func.sum(Sale.quantity)).filter_by(product_id=product_id).scalar() or 0
        remaining_stock = product.quantity - total_sold

        if quantity > remaining_stock:
            message = f"Not enough stock available. Only {remaining_stock} units left."
            products = Product.query.order_by(Product.date_created).all()
            customers = Customer.query.order_by(Customer.date_created).all()
            sales = Sale.query.order_by(Sale.date).all()
            return render_template("sales.html", sales=sales, products=products, customers=customers, message=message)

        new_sale = Sale(product_id=product_id, customer_id=customer_id, quantity=quantity, price=price, date=date)
        
        try:
            db.session.add(new_sale)
            db.session.commit()
            return redirect("/sales/")
        except Exception as e:
            return f"There was an issue while recording the sale: {str(e)}"
    else:
        products = Product.query.order_by(Product.date_created).all()
        customers = Customer.query.order_by(Customer.date_created).all()  # Fetch customers
        sales = Sale.query.order_by(Sale.date).all()
        return render_template("sales.html", sales=sales, products=products, customers=customers)

# 💡Route and Function to Update Sales
@app.route("/update-sale/<int:id>", methods=["POST", "GET"])
def updateSale(id):
    sale = Sale.query.get_or_404(id)
    products = Product.query.order_by(Product.date_created).all()
    if request.method == "POST":
        sale.product_id = request.form["product_id"]
        sale.quantity = request.form["quantity"]
        sale.price = request.form["price"]
        date_str = request.form["date"]
        
        # Convert date string to date object
        try:
            sale.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError as e:
            return f"There was an issue with the date format: {str(e)}"
        
        try:
            db.session.commit()
            return redirect("/sales/")
        except Exception as e:
            return f"There was an issue while updating the sale: {str(e)}"
    else:
        return render_template("update-sale.html", sale=sale, products=products)

# 💡Route and Function to Delete Sales
@app.route("/delete-sale/<int:id>")
def deleteSale(id):
    sale_to_delete = Sale.query.get_or_404(id)
    try:
        db.session.delete(sale_to_delete)
        db.session.commit()
        return redirect("/sales/")
    except Exception as e:
        return f"There was an issue while deleting the sale: {str(e)}"

# 💡Route and Function to Get balance Stock
@app.route("/balance-stock/")
def balanceStock():
    products = Product.query.all()
    sales = db.session.query(Sale.product_id, db.func.sum(Sale.quantity).label('total_sold')).group_by(Sale.product_id).all()

    sales_dict = {sale.product_id: sale.total_sold for sale in sales}

    balance_stock = []
    for product in products:
        total_sold = sales_dict.get(product.product_id, 0)
        remaining_stock = product.quantity - total_sold
        balance_stock.append({
            'product_id': product.product_id,
            'category': product.category,
            'price': product.price,
            'date_created': product.date_created,
            'quantity': product.quantity,
            'total_sold': total_sold,
            'remaining_stock': remaining_stock
        })

    return render_template("balance-stock.html", balance_stock=balance_stock)

# 💡Route and Function to get Invoice
@app.route("/invoice/")
def invoice():
    sales = db.session.query(Sale, Customer, Product)\
                      .join(Customer, Sale.customer_id == Customer.customer_id)\
                      .join(Product, Sale.product_id == Product.product_id)\
                      .all()
    return render_template("invoice.html", sales=sales)




# 💡Route and Function to get Dynamic Data from Inventory
@app.route('/export-text')
def export_to_text_file():
    # Query the database
    locations = Location.query.all()
    product_movements = ProductMovement.query.all()
    products = Product.query.all()
    suppliers = Supplier.query.all()
    customers = Customer.query.all()
    sales = Sale.query.all()

    # Prepare the content for the text file
    content = "Locations:\n"
    for location in locations:
        content += f"ID: {location.location_id}, Date Created: {location.date_created}\n"
    
    content += "\nProduct Movements:\n"
    for movement in product_movements:
        content += (f"ID: {movement.movement_id}, Product ID: {movement.product_id}, "
                    f"Quantity: {movement.qty}, From Location: {movement.from_location}, "
                    f"To Location: {movement.to_location}, Movement Time: {movement.movement_time}\n")
    
    content += "\nProducts:\n"
    for product in products:
        content += (f"ID: {product.product_id}, Quantity: {product.quantity}, "
                    f"Category: {product.category}, Price: {product.price}, "
                    f"Date Created: {product.date_created}\n")

    content += "\nSuppliers:\n"
    for supplier in suppliers:
        content += (f"ID: {supplier.id}, Supplier ID: {supplier.supplier_id}, "
                    f"Name: {supplier.name}, Phone: {supplier.phone}, "
                    f"Email: {supplier.email}, Date Created: {supplier.date_created}\n")
    
    content += "\nCustomers:\n"
    for customer in customers:
        content += (f"ID: {customer.id}, Customer ID: {customer.customer_id}, "
                    f"Name: {customer.name}, Phone: {customer.phone}, "
                    f"Email: {customer.email}, Date Created: {customer.date_created}\n")

    content += "\nSales:\n"
    for sale in sales:
        content += (f"ID: {sale.id}, Product ID: {sale.product_id}, "
                    f"Customer ID: {sale.customer_id}, Quantity: {sale.quantity}, "
                    f"Price: {sale.price}, Date: {sale.date}\n")

    # Ensure the instance path directory exists
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # Save the content to a text file
    text_path = os.path.join(app.instance_path, 'inventory_records.txt')
    with open(text_path, 'w', encoding='utf-8') as file:
        file.write(content)
        
        
    text_path = os.path.join(app.instance_path, 'inventory_records.txt')
    if os.path.exists(text_path):
        with open(text_path, 'r', encoding='utf-8') as file:
            content = file.read()
        # return jsonify({"data": content})
        return content
    else:
        # return jsonify({"error": "Text file not found"}), 404
        return 404

    # return text_path


# 💡Chat Bot Section
@app.route('/chatbot/', methods = ['GET','POST'])
def chatbot():

    generation_config = {
      "temperature": 1,
      "top_p": 0.95,
      "top_k": 64,
      "max_output_tokens": 8192,
      "response_mime_type": "text/plain",
    }
  
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        safety_settings=safety_settings,
        generation_config=generation_config,
    )

    # Reading the .csv file and .txt file as string so it can be used 
    # 🔹 Medicine.txt
    medicine_text_file = 'inventory/static/tx/Medicine.txt'
    with open(medicine_text_file, 'r', encoding='utf-8') as file:
        medicine_text_content = file.read()

    # 🔹 General Medicine FAQ's.txt
    general_medicine_text_file = 'inventory/static/tx/General Medication FAQs.txt'
    with open(general_medicine_text_file, 'r', encoding='utf-8') as file:
        general_medicine_text_content = file.read()
        
    # 🔹 Dummy Inventory.txt
    general_medicine_text_file = 'inventory/static/tx/dummy.txt'
    with open(general_medicine_text_file, 'r', encoding='utf-8') as file:
        dummy_text_content = file.read()

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    "You are MediBot chatbot who is working for NaaV. NaaV is a Pharmacy inventory management website so i want you to assist users in the Inventory related stuffs and medicine details and all\n\nYour job is to answer all the queries and questions asked by the users in the form of html code structure not the whole html file. So you have to guide them based on the custom data given to you which is related to the website so your task is:\n\nFirst step is to greet the user with a welcome message and tell the user what type of help you can do like\nTask 1 : Whether the user need to know the availability of a specific medication\nTask 2 : Including checking stock levels\nTask 3 : Reordering medications\nTask 4 : Updating inventory records\nTask 5 : Providing information on medicines and  interactions and side effects",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<p>Welcome to NaaV Pharmacy Inventory Management! 👋</p>\n\n<p>I am MediBot, your friendly assistant for all your inventory needs. How can I help you today? 😊</p>\n\n<p>Here are some tasks I can assist you with:</p>\n\n<ul>\n  <li><strong>Task 1:</strong> Check the availability of a specific medication.</li>\n  <li><strong>Task 2:</strong> Check stock levels for a particular medicine.</li>\n  <li><strong>Task 3:</strong> Reorder medications when stock is low.</li>\n  <li><strong>Task 4:</strong> Update inventory records with new shipments or adjustments.</li>\n  <li><strong>Task 5:</strong> Get information on medicines, including interactions and side effects.</li>\n</ul>\n\n<p>Just tell me what you need, and I'll do my best to help!</p>\n``` \n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "This is the text file which contains the information regarding some of the medicines, so refer this if user asks any question related to medicines make sure you give them the correct answer/response give them the information but not the medical advice. \nRemember, it's crucial to talk to a doctor or pharmacist before taking any new medications, even over-the-counter ones. They can assess your specific situation and recommend the safest and most effective treatment for you.",
                    medicine_text_content,
                    "In all my future inquiries, please ensure that the response is always presented in HTML format.\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "Got it! I will make sure to provide all information about medicines in HTML format, and I will never provide medical advice. \n\nJust ask away, and I will assist you with the medicine details from my database. 😊 \n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "What distinguishes naproxen from other pain relievers like ibuprofen and aspirin? Detail its chemical composition, dosage forms, strengths, and common side effects.\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<p>Naproxen, ibuprofen, and aspirin all belong to a class of medications called NSAIDs (nonsteroidal anti-inflammatory drugs). They work by reducing hormones that cause pain and swelling in the body.</p>\n\n<h3>Key Differences:</h3>\n<ul>\n  <li><strong>Duration of action:</strong> Naproxen has a longer duration of action (8-12 hours) compared to ibuprofen (4-6 hours) and aspirin (4-6 hours). This means you may need to take naproxen less frequently for pain relief.</li>\n  <li><strong>Specific uses:</strong> While all three can be used for general pain relief, naproxen is often preferred for conditions like arthritis due to its longer duration of action. Aspirin is also used as a blood thinner, while ibuprofen and naproxen are not typically used for this purpose.</li>\n</ul>\n\n<h3>Naproxen Details:</h3>\n\n<h4>Chemical Composition:</h4>\n<p>Naproxen</p>\n\n<h4>Dosage Forms:</h4>\n<ul>\n  <li>Tablets</li>\n  <li>Liquid Suspension</li>\n</ul>\n\n<h4>Strengths:</h4>\n<ul>\n  <li>250 mg</li>\n  <li>500 mg</li>\n  <li>750 mg</li>\n</ul>\n\n<h4>Common Side Effects:</h4>\n<p>It's important to remember that not everyone experiences side effects, and the severity can vary. Here are some common side effects of naproxen:</p>\n<ul>\n  <li>Nausea</li>\n  <li>Heartburn</li>\n  <li>Dizziness</li>\n</ul>\n\n<p>This information is for informational purposes only and does not constitute medical advice. Always talk to your doctor or pharmacist before taking any new medication.</p>\n```",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Could you elaborate on the mechanism of action of diclofenac in managing pain and inflammation? Provide insights into its chemical structure, dosage forms, strengths, and potential adverse effects.",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Diclofenac: Mechanism of Action for Pain and Inflammation</h3>\n\n<p>Diclofenac, like naproxen, ibuprofen, and aspirin, belongs to the NSAID (nonsteroidal anti-inflammatory drug) family.  It works by inhibiting the COX (cyclooxygenase) enzymes, COX-1 and COX-2. These enzymes are responsible for producing prostaglandins, which are chemicals that contribute to pain, inflammation, and fever.</p>\n\n<p>By blocking COX enzymes, diclofenac reduces the production of prostaglandins, thus leading to relief from pain and inflammation. </p>\n\n<h3>Diclofenac Details:</h3>\n\n<h4>Chemical Structure:</h4>\n<p>2-(2,6-Dichlorophenylamino)benzeneacetic acid </p>\n\n<h4>Dosage Forms:</h4>\n<ul>\n  <li>Tablets</li>\n  <li>Capsules</li>\n  <li>Liquid Suspension</li>\n  <li>Topical Gels/Creams</li>\n  <li>Eye Drops (for specific eye conditions)</li>\n</ul>\n\n<h4>Strengths:</h4>\n<p>Strengths vary depending on the dosage form. Common strengths for oral forms include:</p>\n<ul>\n  <li>25 mg</li>\n  <li>50 mg</li>\n  <li>75 mg (may be available in some regions)</li>\n  <li>100 mg (may be available in some regions as extended-release formulations)</li>\n</ul>\n\n<h4>Potential Adverse Effects:</h4>\n<p>Like all medications, diclofenac can cause side effects, although not everyone experiences them. Common side effects can include:</p>\n<ul>\n  <li>Stomach upset (heartburn, nausea, indigestion)</li>\n  <li>Dizziness</li>\n  <li>Headache</li>\n</ul>\n<p>More serious side effects are possible, especially with prolonged use. It's essential to discuss your medical history and any potential risks with your doctor or pharmacist.</p>\n\n<p><strong>Important Reminder:</strong> This information is for informational purposes only and does not constitute medical advice. Always consult with a doctor or pharmacist before taking any new medication, including diclofenac, to ensure it is safe and appropriate for you.</p>\n``` \n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Could you explain the pharmacological differences between lorazepam and diazepam in treating anxiety disorders? Detail their chemical structures, mechanisms of action, dosage forms, strengths, and common side effects.",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h2>Lorazepam vs. Diazepam for Anxiety</h2>\n\n<p>Lorazepam and diazepam are both benzodiazepines, a class of medications that act as central nervous system depressants. They are commonly prescribed for anxiety disorders, but have some important differences.</p>\n\n<h3>Pharmacological Differences</h3>\n\n<table>\n  <thead>\n    <tr>\n      <th>Feature</th>\n      <th>Lorazepam</th>\n      <th>Diazepam</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <td><strong>Chemical Structure</strong></td>\n      <td>7-Chloro-5-(o-chlorophenyl)-1,3-dihydro-3-hydroxy-2H-1,4-benzodiazepin-2-one</td>\n      <td>7-Chloro-1,3-dihydro-1-methyl-5-phenyl-2H-1,4-benzodiazepin-2-one</td>\n    </tr>\n    <tr>\n      <td><strong>Mechanism of Action</strong></td>\n      <td colspan=\"2\">Both enhance the effects of GABA, an inhibitory neurotransmitter in the brain, leading to a calming effect.</td>\n    </tr>\n    <tr>\n      <td><strong>Onset of Action</strong></td>\n      <td>Faster (15-30 minutes)</td>\n      <td>Slower (30-60 minutes)</td>\n    </tr>\n    <tr>\n      <td><strong>Duration of Action</strong></td>\n      <td>Intermediate (6-8 hours)</td>\n      <td>Longer (up to 48 hours, with active metabolites)</td>\n    </tr>\n  </tbody>\n</table>\n\n<h3>Dosage Forms & Strengths</h3>\n\n<p>Both medications are available in various forms, including tablets, oral solutions, and injectable forms (used primarily in hospital settings). Common strengths vary, and your doctor will determine the appropriate dose based on your individual needs.</p>\n\n<h3>Common Side Effects</h3>\n\n<p>Both lorazepam and diazepam share common side effects, including:</p>\n<ul>\n  <li>Drowsiness</li>\n  <li>Dizziness</li>\n  <li>Impaired coordination</li>\n  <li>Confusion</li>\n  <li>Amnesia (memory problems)</li>\n</ul>\n\n<p><strong>Important Considerations:</strong></p>\n<ul>\n  <li>Benzodiazepines can be habit-forming and should be used only as directed by a doctor.</li>\n  <li>They can interact with alcohol and other medications, so be sure to tell your doctor about all the medications you are taking.</li>\n  <li>Do not stop taking these medications abruptly without consulting your doctor.</li>\n</ul>\n\n<p><strong>Disclaimer:</strong> This information is for general knowledge and should not be considered medical advice. It's essential to consult with a qualified healthcare professional for personalized guidance and treatment plans.</p>\n```\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Describe the mechanism of action of omeprazole in treating gastroesophageal reflux disease (GERD) and peptic ulcers. ",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Omeprazole and its Role in Treating GERD and Peptic Ulcers</h3>\n\n<p>Omeprazole belongs to a class of drugs called proton pump inhibitors (PPIs). It provides relief from GERD and promotes the healing of peptic ulcers by effectively reducing the amount of acid produced in the stomach.  </p>\n\n<h4>Mechanism of Action:</h4>\n\n<ol>\n  <li><strong>Targeting the Proton Pump:</strong> Omeprazole specifically targets the proton pump, a system located in the cells lining the stomach.</li>\n  <li><strong>Blocking Acid Production:</strong> The proton pump is responsible for the final step in acid secretion. Omeprazole irreversibly binds to and blocks the action of this pump.</li>\n  <li><strong>Reducing Stomach Acidity:</strong>  By inhibiting the proton pump, omeprazole significantly reduces the amount of acid present in the stomach. This lower acidity provides relief from the symptoms of GERD, such as heartburn and regurgitation, and allows ulcers in the esophagus, stomach, or duodenum to heal.</li>\n</ol>\n\n<p><strong>Key Points:</strong></p>\n<ul>\n  <li>Omeprazole is taken orally and is available in various forms, including capsules, delayed-release tablets, and oral suspensions.</li>\n  <li>It is typically taken once a day, before a meal.</li>\n  <li>It's important to follow your doctor's instructions and complete the full course of treatment, even if your symptoms improve.</li>\n  <li>Like all medications, omeprazole can cause side effects, though not everyone experiences them. Common side effects are generally mild and may include headache, diarrhea, nausea, and stomach pain.</li>\n</ul>\n\n<p><strong>Remember:</strong> This information is for general knowledge and does not constitute medical advice. Always consult with your doctor or pharmacist for diagnosis and treatment of GERD or peptic ulcers.</p>\n``` \n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "How does atorvastatin contribute to reducing the risk of cardiovascular events? ",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Atorvastatin and Cardiovascular Event Reduction</h3>\n\n<p>Atorvastatin belongs to a class of medications called statins. These drugs play a crucial role in reducing the risk of cardiovascular events like heart attacks and strokes. </p>\n\n<h4>Mechanism of Action:</h4>\n<ol>\n  <li><strong>Cholesterol Synthesis Inhibition:</strong> Atorvastatin works primarily by inhibiting an enzyme called HMG-CoA reductase, which is essential for the production of cholesterol in the liver.</li>\n  <li><strong>Lowering LDL Cholesterol:</strong>  By reducing cholesterol synthesis, atorvastatin effectively lowers the levels of low-density lipoprotein (LDL) cholesterol, often referred to as \"bad\" cholesterol.</li>\n  <li><strong>Raising HDL Cholesterol:</strong>  Atorvastatin also modestly increases the levels of high-density lipoprotein (HDL) cholesterol, known as \"good\" cholesterol. </li>\n  <li><strong>Stabilizing Plaque:</strong> Beyond cholesterol management, atorvastatin helps stabilize plaque buildup within arteries.  This reduces the likelihood of plaque rupture, a major cause of heart attacks and strokes.</li>\n</ol>\n\n<p><strong>Benefits for Cardiovascular Health:</strong></p>\n\n<p>By effectively managing cholesterol levels and stabilizing plaque, atorvastatin provides significant benefits in reducing the risk of:</p>\n<ul>\n  <li>Heart Attacks</li>\n  <li>Strokes</li>\n  <li>The need for procedures like angioplasty or bypass surgery </li>\n</ul>\n\n<p><strong>Important Notes:</strong></p>\n<ul>\n  <li>Atorvastatin is a prescription medication, and your doctor will determine the appropriate dosage based on your cardiovascular risk factors and cholesterol levels.</li>\n  <li>Lifestyle modifications, such as a healthy diet and regular exercise, are crucial alongside atorvastatin therapy for optimal cardiovascular health. </li>\n  <li>As with any medication, side effects are possible. It's essential to discuss any concerns or potential side effects with your doctor.</li>\n</ul>\n\n<p><strong>Disclaimer:</strong> This information is intended for general knowledge and should not substitute medical advice. Consult your doctor or a qualified healthcare professional for diagnosis and treatment of cardiovascular conditions.</p> \n``` \n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Can you elaborate on the uses of metformin in managing type 2 diabetes mellitus?\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Metformin and Type 2 Diabetes Management</h3>\n\n<p>Metformin is a commonly prescribed medication for managing type 2 diabetes mellitus. It belongs to a class of drugs called biguanides and works in several ways to help control blood sugar levels.</p>\n\n<h4>Mechanisms of Action:</h4>\n\n<ol>\n  <li><strong>Reducing Glucose Production:</strong> Metformin lowers blood sugar by decreasing the amount of glucose produced by the liver.</li>\n  <li><strong>Improving Insulin Sensitivity:</strong>  It enhances the body's response to insulin, the hormone that regulates blood sugar. This allows cells to use glucose more effectively.</li>\n  <li><strong>Slowing Glucose Absorption: </strong> Metformin can also slightly slow down the absorption of glucose from the intestines into the bloodstream.</li>\n</ol>\n\n<h4>Benefits for Type 2 Diabetes:</h4>\n\n<p>By addressing these key aspects of blood sugar regulation, metformin helps:</p>\n<ul>\n  <li>Lower fasting blood sugar levels</li>\n  <li>Improve blood sugar control after meals</li>\n  <li>Reduce the risk of long-term diabetes complications (heart disease, nerve damage, kidney problems, eye problems)</li>\n</ul>\n\n<p><strong>Key Points:</strong></p>\n<ul>\n  <li>Metformin is typically taken orally, with or without food, as directed by your doctor.</li>\n  <li>Dosage is individualized based on blood sugar levels and other factors.</li>\n  <li>Lifestyle modifications, such as a healthy diet and regular exercise, are essential components of diabetes management alongside medication.</li>\n  <li>Common side effects of metformin may include gastrointestinal upset (nausea, diarrhea), but these often subside over time or with dosage adjustments.</li>\n</ul>\n\n<p><strong>Disclaimer:</strong> This information is provided for general knowledge and is not a substitute for professional medical advice. Always consult your doctor or pharmacist for diagnosis and treatment of diabetes. </p> \n``` \n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Describe the pharmacokinetics and pharmacodynamics of warfarin in preventing blood clot formation. Include information on its chemical structure, dosage forms, strengths, common side effects, and brand names.",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Warfarin: Anticoagulant Therapy</h3>\n\n<p>Warfarin is a powerful anticoagulant medication used to prevent the formation of harmful blood clots.  Understanding its pharmacokinetics (how the body processes the drug) and pharmacodynamics (how the drug affects the body) is crucial for its safe and effective use.</p>\n\n<h4>Pharmacokinetics:</h4>\n<ul>\n  <li><strong>Absorption:</strong>  Well-absorbed orally, reaching peak plasma concentrations in about 1-4 hours.</li>\n  <li><strong>Distribution:</strong>  Highly bound to plasma proteins (over 97%), mainly albumin.</li>\n  <li><strong>Metabolism:</strong> Metabolized in the liver by cytochrome P450 enzymes, primarily CYP2C9.</li>\n  <li><strong>Excretion:</strong>  Eliminated primarily in the urine as inactive metabolites.</li>\n  <li><strong>Half-Life:</strong> Long half-life, typically 20-60 hours, leading to a slow onset and offset of action (1-3 days for full effect).</li>\n</ul>\n\n<h4>Pharmacodynamics:</h4>\n<ul>\n  <li><strong>Vitamin K Antagonist:</strong> Warfarin inhibits the synthesis of vitamin K-dependent clotting factors (II, VII, IX, and X) in the liver, essential for blood clot formation.</li>\n  <li><strong>INR Monitoring: </strong> The prothrombin time (PT) and International Normalized Ratio (INR) are used to monitor the effects of warfarin and adjust dosage. INR measures the time it takes for blood to clot.</li>\n</ul>\n\n<h4>Chemical Structure:</h4>\n<p>4-Hydroxy-3-(3-oxo-1-phenylbutyl)-2H-1-benzopyran-2-one</p>\n\n<h4>Dosage Forms & Strengths:</h4>\n<ul>\n  <li>Tablets are the most common form.</li>\n  <li>Strengths: 1 mg, 2 mg, 2.5 mg, 3 mg, 4 mg, 5 mg, 6 mg, 7.5 mg, 10 mg</li>\n  <li>Dosage is highly individualized based on INR monitoring.</li>\n</ul>\n\n<h4>Common Side Effects:</h4>\n<p>The most significant risk associated with warfarin is bleeding. Other potential side effects can include:</p>\n<ul>\n  <li>Easy bruising</li>\n  <li>Gastrointestinal bleeding</li>\n  <li>Hair loss (rare)</li>\n  <li>Purple toe syndrome (rare)</li>\n</ul>\n\n<h4>Brand Names:</h4>\n<ul>\n  <li>Coumadin</li>\n  <li>Jantoven</li>\n  <li>Generic warfarin</li>\n</ul>\n\n<p><strong>Important Notes:</strong></p>\n<ul>\n  <li>Warfarin has numerous drug interactions and dietary restrictions. It's crucial to inform your healthcare provider about all medications, supplements, and dietary changes.</li>\n  <li>Regular INR monitoring is essential to ensure safe and effective anticoagulation.</li>\n</ul>\n\n<p><strong>Disclaimer:</strong> This information is for general knowledge and does not constitute medical advice. Always consult with a healthcare professional for personalized medical guidance.</p> \n``` \n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "What are the unique characteristics of duloxetine in managing depression and neuropathic pain?\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Duloxetine: A Dual-Action Approach to Depression and Neuropathic Pain</h3>\n\n<p>Duloxetine is classified as a serotonin-norepinephrine reuptake inhibitor (SNRI). What sets it apart from some other antidepressants is its dual mechanism of action, making it effective for both depression and certain types of chronic pain, including neuropathic pain.</p>\n\n<h4>How Duloxetine Works:</h4>\n\n<ol>\n  <li><strong>Enhancing Neurotransmitter Levels: </strong> Duloxetine increases levels of serotonin and norepinephrine in the brain. These neurotransmitters play key roles in regulating mood, sleep, and the perception of pain.</li>\n  <li><strong>Inhibiting Reuptake:</strong>  SNRIs like duloxetine work by blocking the reabsorption (reuptake) of serotonin and norepinephrine in the brain. This allows these neurotransmitters to remain active for longer periods, which can help to improve mood and reduce pain signals.</li>\n</ol>\n\n<h4>Benefits in Depression and Neuropathic Pain:</h4>\n<ul>\n  <li><strong>Depression:</strong> Duloxetine is approved to treat major depressive disorder (MDD). By increasing serotonin and norepinephrine, it can help alleviate symptoms of depression such as low mood, fatigue, and loss of interest.</li>\n  <li><strong>Neuropathic Pain:</strong>  Duloxetine is also effective in managing chronic pain conditions like diabetic peripheral neuropathy, fibromyalgia, and chronic musculoskeletal pain. Its mechanism of action in the spinal cord helps modulate pain signals, providing relief.</li>\n</ul>\n\n<h4>Dosage and Forms:</h4>\n\n<ul>\n  <li>Duloxetine is available in delayed-release capsules for oral administration.</li>\n  <li>Dosage varies depending on the condition being treated and individual patient factors.</li>\n  <li>It's crucial to follow your doctor's instructions and not adjust the dosage without their guidance.</li>\n</ul>\n\n<h4>Important Considerations:</h4>\n\n<ul>\n  <li>Like all medications, duloxetine can cause side effects, though not everyone experiences them. Common side effects might include nausea, dry mouth, constipation, and drowsiness.</li>\n  <li>It's essential to discuss your full medical history with your doctor before starting duloxetine, as it may interact with other medications or medical conditions.</li>\n  <li>Do not stop taking duloxetine abruptly, as this could lead to withdrawal symptoms. Your doctor will guide you on gradually tapering off the medication if needed.</li>\n</ul>\n\n<p><strong>Disclaimer: </strong>This information is for general knowledge purposes and does not constitute medical advice. It's crucial to consult with your doctor or a qualified healthcare professional for diagnosis and treatment of any health condition. </p>\n``` \n\n\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "How does albuterol function as a bronchodilator in the treatment of asthma and chronic obstructive pulmonary disease (COPD)? answer should be point to point ",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Albuterol: A Bronchodilator for Respiratory Relief</h3>\n\n<p>Albuterol is a medication commonly used to relieve bronchospasm (tightening of the airways) associated with asthma and chronic obstructive pulmonary disease (COPD). </p>\n\n<h4>Mechanism of Action:</h4>\n<ol>\n  <li><strong>Beta-2 Adrenergic Receptor Agonist:</strong> Albuterol acts on beta-2 adrenergic receptors, which are found in the smooth muscles of the airways.</li>\n  <li><strong>Relaxation of Airway Muscles:</strong> When albuterol stimulates these receptors, it causes the muscles surrounding the airways to relax.</li>\n  <li><strong>Bronchodilation:</strong> This relaxation widens the airways (bronchodilation), making it easier for air to flow in and out of the lungs.</li>\n</ol>\n\n<h4>Effects:</h4>\n<ul>\n  <li><strong>Quick Relief: </strong> Albuterol is a short-acting bronchodilator, providing rapid relief from symptoms such as wheezing, shortness of breath, and chest tightness.</li>\n  <li><strong>Improved Airflow: </strong> It improves airflow to the lungs, making breathing easier during an asthma attack or COPD exacerbation.</li>\n</ul>\n\n<h4>Methods of Administration:</h4>\n<ul>\n  <li><strong>Inhalers:</strong> Metered-dose inhalers (MDIs) and dry powder inhalers (DPIs) deliver albuterol directly to the lungs, allowing for faster action and fewer systemic side effects.</li>\n  <li><strong>Nebulizers:</strong> Albuterol can also be given through a nebulizer, which converts the liquid medication into a fine mist that is inhaled.</li>\n</ul>\n\n<p><strong>Disclaimer:</strong> This information is provided for general knowledge and does not constitute medical advice. Consult with your healthcare provider for diagnosis and treatment of respiratory conditions.</p>\n``` \n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "What distinguishes montelukast from other medications in managing asthma and allergic rhinitis? \n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Montelukast: A Different Approach to Asthma and Allergic Rhinitis</h3>\n\n<p>Montelukast stands out from many other asthma and allergic rhinitis medications because it belongs to a class of drugs called leukotriene receptor antagonists (LTRAs). Unlike some other treatments, it does not directly open up airways but rather blocks the action of leukotrienes. </p>\n\n<h4>How Montelukast Works:</h4>\n\n<ol>\n  <li><strong>Targeting Leukotrienes:</strong>  Montelukast blocks the action of leukotrienes, which are inflammatory chemicals the body releases in response to allergens (like pollen, dust mites, pet dander) and during asthma episodes.</li>\n  <li><strong>Reducing Airway Inflammation:</strong> By blocking leukotrienes, montelukast helps reduce inflammation and swelling in the airways.</li>\n  <li><strong>Preventing Asthma Symptoms:</strong> This anti-inflammatory effect is key in preventing asthma symptoms such as wheezing, coughing, shortness of breath, and chest tightness.</li>\n</ol>\n\n<h4>Key Distinctions:</h4>\n\n<ul>\n  <li><strong>Prophylactic Use:</strong> Montelukast is primarily used for the prevention of asthma attacks and allergic rhinitis symptoms. It is not a rescue medication for immediate relief during an attack.</li>\n  <li><strong>Targeting Inflammation:</strong> Unlike short-acting bronchodilators that quickly open up airways, montelukast works over time to reduce underlying inflammation, making it a good long-term control medication.</li>\n  <li><strong>Oral Administration:</strong>  Montelukast is taken orally as a tablet, chewable tablet, or granules, making it convenient for daily use.</li>\n</ul>\n\n<p><strong>Disclaimer:</strong>  Always consult with your healthcare professional for diagnosis and treatment of asthma or allergic rhinitis. This information is not a substitute for professional medical advice.</p>\n``` \n\n\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "This is the text file which contains the information regarding some of the medicines, so refer this if user asks any question related to medicines make sure you give them the correct answer/response give them the information but not the medical advice.\nRemember, it's crucial to talk to a doctor or pharmacist before taking any new medications, even over-the-counter ones. They can assess your specific situation and recommend the safest and most effective treatment for you.",
                    general_medicine_text_content,
                ],
            },
            {
                "role": "model",
                "parts": [
                    "<p>Please provide me with a specific question about medication. For example, you could ask:</p>\n\n```html\n<ul>\n  <li>What should I do if I miss a dose of my medication?</li>\n  <li>Can I take medications on an empty stomach?</li>\n  <li>Are generic medications as effective as brand-name ones?</li>\n</ul> \n``` \n\n<p>I will then provide you with an informative response in HTML format, based on the provided text file. Remember, I cannot offer medical advice. Always consult with a healthcare professional for personalized guidance.</p> \n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Are there any specific considerations for applying medication patches on areas with scars or tattoos?",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Medication Patches and Scars/Tattoos</h3>\n\n<p>It's generally recommended to <strong>avoid applying medication patches directly on scars or tattoos</strong> whenever possible. Here's why:</p>\n\n<ul>\n  <li><strong>Altered Absorption:</strong> Scars and tattoos can affect the way your skin absorbs medication. This could lead to either too little or too much medication entering your bloodstream.</li>\n  <li><strong>Skin Irritation:</strong>  Patches can trap moisture against the skin, which may irritate sensitive areas like scars or tattoos, potentially causing discomfort or a rash.</li>\n  <li><strong>Adhesive Issues:</strong> Patches may not adhere properly to uneven skin surfaces, such as raised scars or areas with tattoo ink.</li>\n</ul>\n\n<h4>What to Do:</h4>\n<ol>\n  <li><strong>Consult Your Doctor or Pharmacist:</strong>  They can advise you on the best placement for your specific patch and medication.</li>\n  <li><strong>Choose a Different Area:</strong>  Whenever possible, apply the patch to a clean, dry, and hairless area of skin that is free of scars, tattoos, cuts, or irritation.</li>\n  <li><strong>Rotate Sites:</strong>  If you need to use multiple patches or apply them over an extended period, rotate the application site each time to prevent skin irritation.</li>\n</ol>\n\n<p><strong>Remember:</strong>  Always follow the instructions provided with your medication patch and consult a healthcare professional if you have any concerns or questions.</p>\n```\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "How do I know if a medication patch is not adhering properly to my skin?",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Signs Your Medication Patch Might Not Be Adhering Properly:</h3>\n\n<p>It's crucial for a medication patch to stay securely in place for it to deliver the medication effectively. Here are some signs to watch out for:</p>\n\n<ul>\n  <li><strong>Visible Peeling:</strong>  If you notice the edges of the patch are lifting or peeling away from your skin, it's not adhering properly.</li>\n  <li><strong>Patch Feels Loose:</strong> If the patch feels loose or like it might fall off when you move, it needs better adhesion.</li>\n  <li><strong>Skin Irritation Around the Edges:</strong>  Irritation, redness, or itching around the edges of the patch can indicate that it's not sticking securely and may be rubbing against your skin.</li>\n  <li><strong>Medication Residue:</strong> If you find a sticky residue on your skin or clothing where the patch should be, it suggests the adhesive is failing.</li>\n  <li><strong>Unexpected Symptoms:</strong> If you experience a sudden return of symptoms that were under control with the patch, it could be a sign the patch is no longer delivering the medication properly.</li>\n</ul>\n\n<h4>What to Do If a Patch Is Not Adhering:</h4>\n<ol>\n  <li><strong>Do Not Re-Stick a Patch That Has Lost Adhesion:</strong> If a patch is more than slightly loose or has fallen off, do not try to reapply it. The adhesive may no longer be effective.</li>\n  <li><strong>Contact Your Doctor or Pharmacist: </strong> They can advise you on the appropriate course of action, such as applying a new patch or adjusting the dosage.</li>\n</ol>\n\n<p><strong>Important:</strong>  Never apply a medication patch to irritated or broken skin. If you experience severe skin irritation or any unusual symptoms, consult your doctor immediately.</p> \n```\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Can certain medications cause changes in taste perception or appetite?\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Medications and Their Effects on Taste and Appetite</h3>\n\n<p>Yes, certain medications can indeed cause changes in how we perceive taste (dysgeusia) or alter our appetite. </p>\n\n<h4>How Medications Can Affect Taste and Appetite:</h4>\n\n<ul>\n  <li><strong>Directly Affecting Taste Buds:</strong> Some medications can directly interact with taste buds on the tongue, leading to a metallic, bitter, or otherwise unpleasant taste in the mouth.</li>\n  <li><strong>Altering Nerve Signals:</strong> Certain drugs can interfere with the way nerves transmit taste signals from the tongue to the brain, distorting taste perception. </li>\n  <li><strong>Influencing Appetite Centers in the Brain:</strong> Some medications can affect areas of the brain that control hunger and satiety, leading to changes in appetite — either an increase or decrease.</li>  \n  <li><strong>Causing Side Effects:</strong> Medications that cause nausea, vomiting, dry mouth, or changes in saliva production can indirectly affect both taste and appetite.</li>\n</ul>\n\n<h4>Types of Medications Often Associated with Taste and Appetite Changes:</h4>\n\n<p>While many different drugs can potentially cause these effects, some common culprits include:</p>\n\n<ul>\n  <li><strong>Chemotherapy drugs</strong></li>\n  <li><strong>Antibiotics</strong></li>\n  <li><strong>Blood pressure medications (ACE inhibitors, ARBs)</strong></li>\n  <li><strong>Antidepressants and mood stabilizers</strong></li>\n  <li><strong>Medications for Parkinson’s disease</strong></li>\n  <li><strong>Antihistamines</strong></li>\n  <li><strong>Corticosteroids</strong></li>\n</ul>\n\n<h4>What to Do:</h4>\n<ul>\n  <li><strong>Talk to Your Doctor:</strong> If you experience significant taste changes or appetite problems after starting a new medication, consult your doctor. They can help determine if the medication is the cause and discuss potential solutions, such as adjusting the dosage or switching to a different drug.</li>\n  <li><strong>Don't Stop Medications Abruptly:</strong> Do not stop taking your medications without first talking to your doctor.</li>\n</ul>\n\n<p><strong>Important:</strong>  This information is provided for general knowledge and does not constitute medical advice. Always seek guidance from your healthcare professional for personalized medical care and advice.</p>\n```\n\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "What measures can I take to ensure that my medications remain effective during travel or in extreme weather conditions?",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Protecting Your Medications While Traveling and in Extreme Weather</h3>\n\n<p>Medications can be sensitive to changes in temperature and humidity. Here's how to keep your meds safe and effective during travel and challenging weather:</p>\n\n<h4>General Tips:</h4>\n\n<ul>\n  <li><strong>Original Packaging:</strong>  Always keep medications in their original, labeled containers. This helps identify the medication and provides important storage instructions.</li>\n  <li><strong>Carry-On Essentials: </strong> Keep essential medications (those you take daily or might need urgently) in your carry-on luggage. This prevents loss or delays in case of checked baggage issues.</li>\n  <li><strong>Doctor's Note:</strong> Carry a copy of your prescriptions and a letter from your doctor, especially if you have liquid medications or syringes.</li> \n</ul>\n\n<h4>Temperature Control:</h4>\n\n<ul>\n  <li><strong>Heat Protection:</strong>\n    <ul>\n      <li><strong>Insulated Bags:</strong> Use insulated bags or cooling packs, especially for medications that require refrigeration.</li>\n      <li><strong>Avoid Direct Sunlight:</strong> Never leave medications in direct sunlight or hot cars.</li>\n    </ul>\n  </li>\n  <li><strong>Cold Protection:</strong>\n    <ul>\n      <li><strong>Body Heat:</strong>  Keep medications close to your body (in an inner pocket) to protect them from freezing temperatures. </li>\n      <li><strong>Avoid Extreme Cold: </strong> Do not leave medications in checked baggage during very cold weather.</li>\n    </ul>\n  </li>\n</ul>\n\n<h4>Humidity:</h4>\n<ul>\n  <li><strong>Waterproof Containers:</strong> Store medications in waterproof containers or bags to protect them from moisture damage, especially in humid environments.</li>\n  <li><strong>Silica Gel Packs:</strong> Consider using silica gel packs inside medication containers to absorb excess moisture.</li>\n</ul>\n\n<h4>Additional Tips:</h4>\n\n<ul>\n  <li><strong>Check Destination Regulations: </strong> Research medication regulations at your destination, especially for controlled substances.</li>\n  <li><strong>Emergency Contacts: </strong> Keep a list of emergency contacts and allergies with your medications.</li>\n</ul>\n\n<p><strong>Remember:</strong> Always consult your doctor or pharmacist for specific storage recommendations for your medications. They can provide tailored advice for your individual needs and travel plans. </p>\n```\n\n\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "How can I safely dispose of medication packaging and containers to minimize environmental impact?",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Safe and Eco-Friendly Disposal of Medication Packaging</h3>\n\n<p>Disposing of medication packaging responsibly helps protect the environment and prevents accidental ingestion by children or animals. Here's how to do it right:</p>\n\n<h4>1. Check for Specific Instructions:</h4>\n<p>Some medications come with specific disposal instructions. Check the label or patient information leaflet for any guidance.</p>\n\n<h4>2.  Medication Take-Back Programs:</h4>\n<p>These programs are the best option! Many pharmacies, hospitals, and community centers offer safe disposal bins for unused or expired medications and their packaging.</p>\n\n<h4>3.  General Guidelines When Take-Back Programs Aren't Available:</h4>\n\n<ul>\n  <li><strong>Remove Personal Information:</strong>  Scratch out any personal information on prescription labels to protect your privacy.</li>\n  <li><strong>Mix with Undesirable Substances:</strong> Mix medications (except for inhalers and liquids) with an undesirable substance like used coffee grounds or kitty litter. This makes them less appealing to children and animals and unrecognizable for misuse.</li>\n  <li><strong>Securely Contain:</strong> Place the mixture in a sealed plastic bag or container to prevent leaks.</li>\n  <li><strong>Place in Household Trash: </strong> Dispose of the sealed bag or container in your household trash. Do not place it in recycling bins. </li>\n</ul>\n\n<h4>What NOT to Do:</h4>\n\n<ul>\n  <li><strong>Flush Medications:</strong>  Avoid flushing medications down the toilet or sink unless specifically instructed to do so. This can contaminate water supplies.</li>\n  <li><strong>Recycle Loose Packaging:</strong> Do not place loose medication packaging (blister packs, bottles) in recycling bins unless specifically permitted by your local recycling program. </li>\n</ul>\n\n<h4>Additional Tips:</h4>\n\n<ul>\n  <li><strong>Check for Local Regulations:</strong>  Some communities have specific guidelines for medication disposal, so it's a good idea to check with your local waste management authority.</li>\n  <li><strong>Use Online Resources:</strong>  Websites like the FDA and EPA offer information on medication disposal programs and best practices.</li>\n</ul>\n\n<p><strong>Remember:</strong> Safe disposal of medication packaging helps safeguard our environment and prevent potential harm.</p> \n```\n\n\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Are there any specific considerations to keep in mind when administering medication to elderly individuals or children?",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Special Considerations for Medication Administration: Elderly and Children</h3>\n\n<p>Administering medications to elderly individuals and children requires extra care due to age-related differences in how their bodies absorb, metabolize, and react to drugs. </p>\n\n<h4>Elderly Individuals:</h4>\n\n<ul>\n  <li><strong>Age-Related Changes:</strong> Aging can affect organ function (liver, kidneys), which can alter drug processing and increase the risk of side effects. </li>\n  <li><strong>Multiple Medications (Polypharmacy):</strong> Elderly individuals often take multiple medications, increasing the potential for drug interactions.</li>\n  <li><strong>Cognitive Impairment: </strong> Memory problems or confusion can make it challenging for some elderly individuals to take medications as prescribed.</li>\n  <li><strong>Swallowing Difficulties:</strong>  Difficulty swallowing (dysphagia) is more common in the elderly and may require medication adjustments (e.g., liquid forms).</li>\n</ul>\n\n<h4>Key Considerations for the Elderly:</h4>\n\n<ul>\n  <li><strong>Regular Medication Reviews: </strong>  Consult with a doctor or pharmacist regularly to review medications, dosages, and potential interactions.</li>\n  <li><strong>Simplified Regimens: </strong>  Ask about simplifying medication regimens to make them easier to manage.</li>\n  <li><strong>Clear Instructions:</strong>  Provide clear, written instructions, and use pill organizers to aid in adherence.</li>\n  <li><strong>Monitoring: </strong> Closely monitor for side effects and report any changes to the doctor.</li>\n</ul>\n\n\n<h4>Children:</h4>\n\n<ul>\n  <li><strong>Weight-Based Dosing:</strong>  Dosages for children are often calculated based on weight, not age. Always use the correct measuring device (oral syringe, not a household spoon).</li>\n  <li><strong>Liquid Forms:</strong> Liquid medications are often easier for children to swallow, but always double-check the dosage and use the provided measuring device.</li>\n  <li><strong>Age-Appropriate Explanations:</strong>  Explain the medication in terms the child can understand. </li>\n  <li><strong>Safety Measures: </strong> Store all medications out of reach of children, preferably in a locked cabinet.</li>\n</ul>\n\n<h4>Key Considerations for Children:</h4>\n\n<ul>\n  <li><strong>Never Assume Adult Dosages:</strong> Never give a child an adult medication or guess the dosage. Always consult a pediatrician.</li>\n  <li><strong>Be Aware of Allergies:</strong>  Pay close attention to any allergies your child has and inform healthcare providers.</li>\n  <li><strong>Use Child-Resistant Caps:</strong> Ensure all medication containers have child-resistant caps to prevent accidental ingestion.</li>\n  <li><strong>Be Patient:</strong>  Making medication time positive and encouraging can help with adherence, especially for young children.</li> \n</ul>\n\n<p><strong>Remember: </strong> This information is for general knowledge and should not substitute professional medical advice. Always consult with a pediatrician or other qualified healthcare provider for diagnosis and treatment of children and for any medication-related questions or concerns. </p> \n```",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Can changes in diet or exercise regimen affect the dosage or frequency of medication needed to manage a chronic condition?",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Diet, Exercise, and Medication Management</h3>\n\n<p>Yes, changes in diet and exercise can definitely influence the dosage or frequency of medication needed for chronic conditions. This is because these lifestyle factors can impact:</p>\n\n<ul>\n<li><strong>Blood Sugar Levels (Diabetes):</strong>  Exercise and diet are cornerstones of diabetes management.  They can improve insulin sensitivity, lowering blood sugar levels, which might necessitate adjustments to medication dosages.</li>\n<li><strong>Blood Pressure:</strong> Regular physical activity and a healthy diet can help lower blood pressure, potentially reducing the need for blood pressure medication or allowing for lower doses.</li>\n<li><strong>Cholesterol Levels:</strong> Exercise, along with a diet low in saturated and trans fats, can improve cholesterol levels. This might lead to adjustments in cholesterol-lowering medications (statins).</li>\n<li><strong>Weight Management:</strong>  Losing weight through diet and exercise can improve various health conditions, potentially reducing medication needs for conditions like type 2 diabetes, heart disease, and sleep apnea.</li>\n</ul>\n\n<h4>Important Considerations:</h4>\n\n<ul>\n<li><strong>Consult Your Doctor:</strong> Never adjust your medication dosage or frequency on your own. Always consult with your doctor before making any changes to your diet, exercise routine, or medication regimen.</li>\n<li><strong>Gradual Adjustments:</strong>  Changes to diet, exercise, or medication should be made gradually and under the guidance of your healthcare provider. This allows for close monitoring and adjustments as needed.</li>\n<li><strong>Individualized Approach:</strong> The impact of lifestyle changes on medication needs varies from person to person. Your doctor will consider your individual health history, medications, and response to treatment when making recommendations.</li>\n</ul>\n\n<p><strong>Remember:</strong>  While lifestyle modifications can be powerful tools in managing chronic conditions, they are not always a substitute for medication. Work closely with your healthcare team to create a comprehensive plan that meets your unique needs.</p>\n```\n\n\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Are there any specific protocols for safely discontinuing medication, particularly if it has been used long-term?",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Safely Discontinuing Medication: Tapering vs. Abrupt Cessation</h3>\n\n<p>Stopping medication, especially after long-term use, should never be done abruptly without consulting your doctor.  Here's why:</p>\n\n<h4>Risks of Abrupt Discontinuation:</h4>\n\n<ul>\n  <li><strong>Withdrawal Symptoms:</strong>  Suddenly stopping some medications can cause unpleasant or even dangerous withdrawal symptoms. These vary depending on the drug but can include anxiety, insomnia, dizziness, seizures, or flu-like symptoms.</li>\n  <li><strong>Rebound Effect (Relapse): </strong>  For conditions like depression, anxiety, or high blood pressure, abruptly stopping medication can cause a rapid return of symptoms, sometimes even more severe than before.</li>\n  <li><strong>Medical Complications:</strong>  In some cases, abrupt cessation can have serious medical consequences, such as heart problems with certain blood pressure medications. </li>\n</ul>\n\n<h4>Tapering: A Safer Approach</h4>\n\n<p>In many cases, doctors recommend a gradual reduction in dosage, known as \"tapering,\" to minimize withdrawal risks:</p>\n\n<ul>\n  <li><strong>Gradual Reduction:</strong>  The dosage is lowered slowly over a period of days, weeks, or even months, depending on the medication and how long it's been taken.</li>\n  <li><strong>Doctor-Supervised Plan:</strong> Your doctor will create a personalized tapering schedule based on your individual needs and medical history.</li> \n  <li><strong>Monitoring for Symptoms:</strong>  During tapering, your doctor will monitor you closely for any withdrawal symptoms or a return of your original condition.</li>\n</ul>\n\n<h4>Medications Often Requiring Tapering:</h4>\n\n<p>While always consult your doctor, these medication classes often require tapering:</p>\n<ul>\n  <li>Antidepressants (SSRIs, SNRIs, tricyclic antidepressants)</li>\n  <li>Benzodiazepines (anxiety medications like alprazolam, diazepam)</li>\n  <li>Corticosteroids (prednisone, methylprednisolone)</li>\n  <li>Some blood pressure medications (beta-blockers, clonidine)</li>\n</ul>\n\n<h4>Important Reminders:</h4>\n\n<ul>\n  <li><strong>Never Self-Adjust:</strong> Do not stop or reduce your medication dosage without direct instructions from your doctor.</li> \n  <li><strong>Open Communication:</strong>  Talk to your doctor about any concerns or side effects you're experiencing. They can help determine the safest and most effective way to manage your medications.</li>\n</ul> \n\n<p><strong>Disclaimer:</strong> This information is for general knowledge and should not substitute professional medical advice. Consult your healthcare provider for personalized guidance regarding stopping any medication.</p>\n```\n\n\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "How can I safely store medication while traveling in areas with extreme temperatures or humidity levels?",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Safeguarding Medications in Extreme Travel Conditions:</h3>\n\n<p>Traveling to places with extreme temperatures or high humidity requires extra care to ensure your medications stay safe and effective. Here's a guide:</p>\n\n<h4>General Tips:</h4>\n\n<ul>\n  <li><strong>Original Packaging:</strong> Always store medications in their original containers with the prescription label attached. This helps with identification and provides important storage information.</li>\n  <li><strong>Carry-On Luggage:</strong> Keep essential medications in your carry-on bag, ensuring they are accessible during travel and protected from extreme temperatures in the cargo hold.</li>\n  <li><strong>Doctor's Note:</strong> Carry a copy of your prescriptions, especially for medications requiring syringes or in liquid form, to avoid issues at security checkpoints.</li>\n</ul>\n\n<h4>Heat Protection:</h4>\n\n<ul>\n  <li><strong>Insulated Bags:</strong> Use insulated bags or cooling packs designed for medications, especially for those needing refrigeration. </li>\n  <li><strong>Avoid Direct Sunlight:</strong> Never leave medications exposed to direct sunlight or in a hot car, as heat can degrade them quickly.</li>\n  <li><strong>Ask About Storage at Your Accommodation:</strong> Inquire about storing medications in a refrigerator upon arrival, particularly in hot climates.</li>\n</ul>\n\n<h4>Cold Protection:</h4>\n\n<ul>\n  <li><strong>Body Heat:</strong> Keep medications close to your body, such as in an inside jacket pocket, to protect them from freezing temperatures.</li>\n  <li><strong>Insulated Packaging:</strong> Use insulated bags or wrap medications in clothing for extra protection during very cold weather.</li>\n  <li><strong>Avoid Checked Luggage in Extreme Cold: </strong> If traveling to extremely cold destinations, try to pack medications in your carry-on luggage to prevent freezing in the cargo hold.</li>\n</ul>\n\n<h4>Humidity Control:</h4>\n\n<ul>\n  <li><strong>Waterproof Containers:</strong> Store medications in waterproof bags or containers, especially in humid environments, to prevent moisture damage.</li>\n  <li><strong>Silica Gel Packs:</strong>  Consider adding silica gel packets inside medication containers to absorb excess moisture.</li>\n</ul>\n\n<h4>Additional Tips:</h4>\n\n<ul>\n  <li><strong>Plan Ahead:</strong> Research the climate of your destination and pack your medications accordingly.</li>\n  <li><strong>Consult Your Pharmacist:</strong> Ask your pharmacist for specific storage advice for your medications, as some may have unique requirements.</li> \n</ul>\n\n<p><strong>Remember:</strong> Taking proactive steps to protect your medications ensures their effectiveness and safeguards your health during your travels. </p>\n```",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Can medications interact with commonly used household products, such as cleaning agents or personal care items?",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Medication Interactions: Beyond the Medicine Cabinet</h3>\n\n<p>While we often think about drug interactions with food or other medications, it's important to be aware that certain household products can also interact with medications, potentially reducing their effectiveness or causing adverse effects. Here are some key things to consider:</p>\n\n<h4>1. Topical Medications and Skin Products:</h4>\n\n<ul>\n  <li><strong>Increased Absorption:</strong> Some skincare ingredients, like retinol or certain oils, can increase the absorption of topical medications, potentially leading to a higher dose than intended.</li>\n  <li><strong>Irritation:</strong> Combining certain medications with harsh soaps, fragrances, or exfoliating agents can irritate the skin, especially if you have sensitive skin or are using medicated creams.</li>\n</ul>\n\n<h4>2. Oral Medications and Grapefruit Juice:</h4>\n\n<p>Grapefruit juice is a well-known culprit for interacting with numerous medications. It can:</p>\n<ul>\n  <li><strong>Increase Drug Levels: </strong> Grapefruit juice can block the breakdown of certain drugs in the gut, leading to higher levels in the bloodstream and increasing the risk of side effects. </li>\n  <li><strong>Medications Affected:</strong> This interaction is known to occur with some cholesterol-lowering drugs (statins), some blood pressure medications, and certain anti-anxiety drugs, among others.</li>\n</ul>\n\n<h4>3.  Medications and Alcohol-Based Products:</h4>\n\n<ul>\n  <li><strong>Mouthwashes and Cough Syrups:</strong> Using alcohol-based mouthwashes or cough syrups while taking certain medications, like metronidazole (an antibiotic) or disulfiram (for alcohol dependence), can cause nausea, vomiting, flushing, or headaches. </li>\n</ul>\n\n<h4>4. General Precautions:</h4>\n\n<ul>\n  <li><strong>Read Labels Carefully:</strong>  Pay attention to product labels and warnings. Look for ingredients that might interact with your medications.</li>\n  <li><strong>Timing is Key:</strong> If you need to use both a medication and a potentially interacting product, try to space them out by a few hours.</li>\n  <li><strong>Consult Your Pharmacist:</strong> Your pharmacist is a valuable resource.  Discuss any concerns about potential interactions between your medications and household products.</li>\n</ul>\n\n<p><strong>Important Note:</strong>  Always follow your doctor's instructions and consult with them or a pharmacist if you have questions about potential interactions or are experiencing unusual symptoms.</p> \n```\n\n\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Can medications interact with herbal teas or supplements commonly used for health purposes?\n\nHow do I know if a medication I am prescribed is safe to take alongside recreational drugs or substances?\n\nAre there specific considerations to keep in mind when administering medication to children with special needs or developmental disorders?\n\nCan certain medications affect fertility or reproductive health in both men and women?\n\nWhat resources are available for individuals who require assistance with medication management but do not have access to reliable caregivers? answer only in HTML format ",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Medications and Herbal Interactions: Proceed with Caution</h3>\n\n<p>Yes, medications can definitely interact with herbal teas and supplements. While often perceived as \"natural,\" herbal products contain active compounds that can have potent effects on the body and interfere with medications.</p>\n\n<h4>Risks of Interactions:</h4>\n\n<ul>\n  <li><strong>Reduced Drug Effectiveness:</strong>  Some herbs can decrease the absorption or speed up the breakdown of certain medications, making them less effective.</li>\n  <li><strong>Increased Drug Effects and Side Effects:</strong> Conversely, some herbs can amplify the effects of medications, leading to higher drug levels in the body and an increased risk of side effects. </li>\n  <li><strong>New or Unexpected Symptoms:</strong> The combination of certain medications and herbs can create new side effects or worsen existing health conditions.</li>\n</ul>\n\n<h4>Common Herbs Known to Interact with Medications:</h4>\n\n<p>This is not an exhaustive list, but some frequently used herbs with interaction potential include:</p>\n<ul>\n  <li>St. John's Wort (often used for depression)</li>\n  <li>Ginkgo Biloba (memory enhancement)</li>\n  <li>Garlic (blood pressure, cholesterol)</li>\n  <li>Ginger (nausea)</li>\n  <li>Echinacea (immune support)</li>\n</ul>\n\n<h4>Essential Precautions:</h4>\n\n<ul>\n  <li><strong>Inform Your Doctor & Pharmacist:</strong>  Always tell your healthcare providers about ALL medications, herbs, and supplements you are taking, including over-the-counter products. </li>\n  <li><strong>Research and Reliable Sources:</strong>  If you are considering using herbal products, research them thoroughly and consult reliable sources, such as your doctor or a qualified herbalist. </li> \n  <li><strong>Start Low and Go Slow:</strong>  If you do use herbal products, start with a low dose and increase gradually, monitoring for any unusual effects.</li>\n</ul>\n\n<h3>Medications and Recreational Drugs: A Dangerous Mix</h3>\n\n<p>It is never safe to assume that a medication is safe to take alongside recreational drugs or substances. Combining prescription medications with recreational drugs can lead to unpredictable and potentially life-threatening consequences.</p>\n\n<h4>Serious Risks of Mixing:</h4>\n\n<ul>\n  <li><strong>Dangerous Interactions:</strong>  Recreational drugs can interact with medications in unpredictable ways, leading to serious health risks, such as heart problems, seizures, organ damage, or coma.</li>\n  <li><strong>Overdose:</strong>  The combined effects of medications and recreational drugs can increase the risk of overdose, even if you take a standard dose of each substance.</li>\n  <li><strong>Unpredictable Side Effects:</strong> Mixing substances can cause unexpected and potentially dangerous side effects, such as extreme drowsiness, agitation, paranoia, or hallucinations. </li>\n</ul>\n\n<h4>Seeking Guidance:</h4>\n\n<ul>\n  <li><strong>Open and Honest Communication:</strong> If you use recreational drugs, it's essential to be open and honest with your doctor about your substance use history. This information helps them prescribe medications safely and monitor for potential interactions. </li>\n  <li><strong>Alternatives and Support:</strong> If you're struggling with substance use, talk to your doctor about treatment options and support services.</li> \n</ul>\n\n<p><strong>Remember:</strong>  Your safety is paramount. Never mix medications and recreational drugs without first consulting a healthcare professional.</p>\n\n<h3>Medications and Children with Special Needs: Personalized Care is Essential</h3>\n\n<p>Administering medications to children with special needs or developmental disorders requires careful consideration and a highly individualized approach. Here's why:</p>\n\n<h4>Unique Challenges:</h4>\n\n<ul>\n  <li><strong>Communication Difficulties:</strong> Children with communication impairments may have trouble expressing side effects or discomfort.</li>\n  <li><strong>Sensory Sensitivities: </strong> Sensory sensitivities can make certain medication forms (like pills, liquid flavors, or injections) challenging. </li>\n  <li><strong>Behavioral Considerations:</strong> Some children might exhibit behavioral resistance to taking medication, requiring patience and alternative strategies.</li>\n  <li><strong>Underlying Medical Conditions:</strong>  Children with special needs might have co-occurring medical conditions that influence medication choice and dosage. </li>\n</ul>\n\n<h4>Key Strategies for Safe Medication Administration:</h4>\n\n<ul>\n  <li><strong>Open Communication with Healthcare Providers:</strong> Maintain ongoing, detailed conversations with your child's pediatrician, specialists, and pharmacists. Provide a thorough medical history, including all therapies and supplements.</li>\n  <li><strong>Personalized Medication Plans:</strong>  Work closely with the healthcare team to develop a tailored medication plan, considering your child's specific needs, preferences, and any potential challenges. </li>\n  <li><strong>Exploring Alternative Forms:</strong>  Discuss alternative medication forms with your pharmacist, such as liquids, chewable tablets, or transdermal patches, to find options that are easier for your child to take. </li>\n  <li><strong>Behavioral Support:</strong>  If your child has behavioral difficulties with medication, seek guidance from a therapist or behavioral specialist on positive reinforcement strategies. </li> \n  <li><strong>Close Monitoring and Follow-Up:</strong> Pay close attention to your child's response to medication, noting any side effects or changes in behavior. Maintain regular follow-up appointments with healthcare providers to adjust treatment plans as needed. </li>\n</ul>\n\n<p><strong>Remember:</strong> Collaboration, communication, and a compassionate, individualized approach are essential when managing medications for children with special needs.</p> \n\n<h3>Medications and Reproductive Health: Potential Impacts</h3>\n\n<p>Yes, certain medications can affect fertility and reproductive health in both men and women. It's crucial to be aware of these potential effects and discuss them with your doctor.</p>\n\n<h4>Medications That Can Impact Fertility:</h4>\n\n<p>The types of medications that may affect fertility vary widely but can include:</p>\n\n<ul>\n  <li><strong>Chemotherapy Drugs: </strong> Some chemotherapy drugs can damage eggs in women and sperm in men, potentially leading to infertility. </li>\n  <li><strong>Hormonal Therapies: </strong> Medications that affect hormones, such as birth control pills, hormone replacement therapy (HRT), and some testosterone therapies, can impact fertility while being used and for a period after stopping.</li>\n  <li><strong>Antipsychotics and Antidepressants: </strong> Some medications used to treat mental health conditions, such as certain antidepressants and antipsychotics, have been linked to fertility issues in some individuals. </li>\n  <li><strong>Other Medications:</strong>  Other medications that can potentially impact fertility include some antibiotics, some medications for autoimmune diseases, and certain blood pressure medications.</li>\n</ul>\n\n<h4>Important Considerations:</h4>\n\n<ul>\n  <li><strong>Open Communication:</strong>  Have a frank discussion with your doctor about your family planning goals before starting any new medication, especially if you are considering having children in the future.</li>\n  <li><strong>Fertility Preservation Options:</strong>  If you need to take a medication that could affect your fertility, talk to your doctor about fertility preservation options, such as egg or sperm freezing. </li>\n  <li><strong>Alternative Medications:</strong>  In some cases, alternative medications with a lower risk to fertility might be available. </li>\n</ul>\n\n<p><strong>Disclaimer:</strong> This information is for general awareness. Always consult with your doctor or a qualified healthcare professional to discuss your individual health situation, medications, and family planning goals.</p>\n\n<h3>Medication Management Support: Finding Resources</h3>\n\n<p>Managing medications can be challenging, especially without reliable caregiver support. Here are some resources that can help:</p>\n\n<h4>1. Your Pharmacist:</h4>\n\n<ul>\n  <li><strong>Medication Counseling:</strong> Pharmacists are medication experts! They can answer questions about your prescriptions, potential interactions, and side effects. </li>\n  <li><strong>Pill Organizers:</strong>  Ask about pill organizers to help you manage multiple medications and remember dosages.</li>\n  <li><strong>Medication Synchronization:</strong>  See if your pharmacy offers medication synchronization programs to simplify refills and pick-ups. </li>\n</ul>\n\n<h4>2. Community Resources:</h4>\n\n<ul>\n  <li><strong>Senior Centers: </strong> Senior centers often provide medication management programs or information on local resources. </li>\n  <li><strong>Social Services: </strong> Contact your local social services agency or Area Agency on Aging for assistance with medication management or connecting with home healthcare options. </li>\n</ul>\n\n<h4>3.  Technology and Apps:</h4>\n\n<ul>\n  <li><strong>Medication Reminder Apps:</strong>  Numerous apps send reminders to take medications and track dosages.</li>\n  <li><strong>Smart Pill Dispensers:</strong>  These devices can help organize medications and provide alerts when it's time to take them.</li>\n</ul>\n\n<h4>4.  Home Healthcare Agencies:</h4>\n\n<ul>\n  <li><strong>Professional Care:</strong> Consider contacting a home healthcare agency if you need more hands-on assistance with medication management, especially if you have complex needs.</li>\n</ul>\n\n<p><strong>Remember: </strong> You don't have to navigate medication management alone. Reach out to healthcare professionals and explore available resources to create a system that works for you.</p>\n```\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Can the effectiveness of certain medications be influenced by factors such as age, gender, or ethnicity?\n\nAre there alternative delivery methods for medications, such as transdermal patches or nasal sprays, that may be more suitable for certain individuals?\n\nHow can I safely dispose of unused or expired medications if there are no local take-back programs available?\n\nWhat precautions should be taken when administering medications to elderly individuals, particularly those with cognitive impairments? answer only in html format ",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Medications and Individual Factors: Age, Gender, Ethnicity</h3>\n\n<p>Yes, the effectiveness of medications can be influenced by factors like age, gender, and ethnicity. This is due to variations in how our bodies process drugs (pharmacokinetics) and how drugs interact with our bodies (pharmacodynamics).</p>\n\n<h4>Age-Related Considerations:</h4>\n\n<ul>\n  <li><strong>Infants & Children:</strong>  Immature organ systems and body composition differences require careful dosage adjustments based on weight or body surface area.</li>\n  <li><strong>Elderly:</strong>  Age-related decline in organ function (liver, kidneys) can alter drug metabolism and elimination, increasing the risk of side effects. Lower doses are often needed.</li>\n</ul>\n\n<h4>Gender Differences:</h4>\n\n<ul>\n  <li><strong>Body Composition:</strong>  Differences in body fat and water distribution can affect how drugs are distributed and absorbed. </li>\n  <li><strong>Hormonal Influences:</strong>  Hormonal fluctuations (menstrual cycle, menopause) can influence drug responses. </li>\n</ul>\n\n<h4>Ethnicity and Genetics:</h4>\n\n<ul>\n  <li><strong>Genetic Variations:</strong>  Genetic differences can affect drug-metabolizing enzymes, influencing how quickly a drug is broken down and eliminated.  This can lead to variations in drug response and side effects among ethnic groups.</li>\n</ul>\n\n<h4>Importance of Personalized Medicine:</h4>\n\n<p>Recognizing these individual factors highlights the importance of personalized medicine. Your healthcare provider considers these factors when selecting medications and dosages that are safe and effective for you. </p>\n\n<h3>Beyond Pills: Alternative Medication Delivery Methods</h3>\n\n<p>Yes, several alternative medication delivery methods can be more suitable for some people than traditional oral medications (pills or capsules):</p>\n\n<h4>1. Transdermal Patches:</h4>\n\n<ul>\n  <li><strong>How They Work:</strong>  Patches adhere to the skin, releasing medication slowly over time through the skin into the bloodstream.</li>\n  <li><strong>Benefits: </strong> Convenient (once-daily or less frequent application), steady medication levels, bypasses the digestive system (reducing stomach upset).</li>\n  <li><strong>Examples: </strong> Nicotine patches (smoking cessation), hormone replacement therapy (HRT), pain relievers (fentanyl).</li>\n</ul>\n\n<h4>2. Nasal Sprays:</h4>\n\n<ul>\n  <li><strong>How They Work:</strong>  Delivers medication through the nasal passages, either locally to treat nasal congestion or systemically (absorbed into the bloodstream).</li>\n  <li><strong>Benefits: </strong> Fast-acting, convenient for some nasal conditions (allergies, congestion), can be an alternative for medications not well-absorbed orally. </li>\n  <li><strong>Examples: </strong> Nasal decongestants, nasal corticosteroids (allergies), migraine medications (sumatriptan).</li> \n</ul>\n\n<h4>3.  Injections:</h4>\n\n<ul>\n  <li><strong>How They Work:</strong> Medication is injected directly into the bloodstream (intravenous), a muscle (intramuscular), or under the skin (subcutaneous). </li>\n  <li><strong>Benefits: </strong> Rapid action (especially intravenous), useful when oral intake is difficult or impossible, allows for precise dosage control.</li>\n  <li><strong>Examples:</strong>  Insulin (diabetes), some vaccines, certain antibiotics. </li>\n</ul>\n\n<h4>4.  Other Delivery Systems:</h4>\n<ul>\n  <li><strong>Implants: </strong> Small devices placed under the skin that release medication over an extended period (e.g., birth control implants).</li>\n  <li><strong>Inhalers:</strong>  Deliver medication directly to the lungs, commonly used for respiratory conditions like asthma and COPD.</li> \n</ul>\n\n<h4>Choosing the Right Method:</h4>\n\n<p>The most appropriate medication delivery method depends on factors like: </p>\n\n<ul>\n  <li>The specific medication and its properties</li>\n  <li>The medical condition being treated</li>\n  <li>Individual patient preferences and needs</li>\n</ul>\n\n<p>Always consult with your doctor or healthcare provider to discuss the best medication delivery method for your specific situation.</p>\n\n\n<h3>Safe Medication Disposal Without Take-Back Programs</h3>\n\n<p>If you don't have access to a medication take-back program, here are safe disposal methods to minimize environmental risks and prevent accidental ingestion:</p>\n\n<h4>1.  Check the Label:</h4> \n<p>Some medications have specific disposal instructions printed on the label or packaging. Follow those instructions first.</p>\n\n<h4>2. General Guidelines:</h4>\n<ul>\n  <li><strong>Mix with Undesirable Substances: </strong> Combine medications (except for inhalers, liquids, or needles) with undesirable substances like used coffee grounds, kitty litter, or dirt. This makes them less appealing to children and animals and unrecognizable for misuse.</li>\n  <li><strong>Seal in a Container:</strong>  Place the mixture in a sealed container, such as a zippered plastic bag or an empty plastic bottle with a lid. </li>\n  <li><strong>Conceal from View:</strong>  Place the sealed container inside a non-recyclable trash bag to further conceal it and prevent accidental discovery. </li>\n  <li><strong>Dispose of in Household Trash:</strong> Throw the sealed bag or container away in your household garbage. </li>\n  <li><strong>Remove Personal Information: </strong> Before discarding, scratch out all personal information on prescription labels to protect your privacy.</li> \n</ul>\n\n<h4>What NOT to Do:</h4>\n\n<ul>\n  <li><strong>Flush Medications:</strong> Avoid flushing medications down the toilet or drain unless specifically instructed by the label. This can contaminate water supplies. </li>\n  <li><strong>Recycle Loose Packaging:</strong>  Do not place pill bottles, blister packs, or other medication packaging in recycling unless specifically permitted by your local recycling program.</li>\n</ul>\n\n<h4>Additional Tips:</h4>\n\n<ul>\n  <li><strong>Check for Household Hazardous Waste Collections:</strong>  Some communities have designated collection events for hazardous waste, which may include medications.</li>\n  <li><strong>Contact Your Local Trash and Recycling Service: </strong>  Inquire about specific medication disposal guidelines in your area.  </li>\n</ul> \n\n<h3>Medications and Cognitive Impairment: Ensuring Safe Administration</h3>\n\n<p>Administering medications to elderly individuals with cognitive impairment, such as dementia or Alzheimer's disease, requires careful attention and strategies to ensure safety and adherence:</p>\n\n<h4>Challenges:</h4>\n\n<ul>\n  <li><strong>Memory Problems:</strong> Forgetting to take medications or taking doses multiple times. </li>\n  <li><strong>Confusion:</strong>  Difficulty understanding instructions, recognizing medications, or differentiating between bottles.</li>\n  <li><strong>Communication: </strong>  Inability to communicate side effects or discomfort effectively.</li>\n</ul>\n\n<h4>Safety Tips:</h4>\n\n<ul>\n  <li><strong>Simplified Medication Regimen:</strong> Work with the doctor to simplify the medication schedule (e.g., once-daily dosing, combining medications). </li>\n  <li><strong>Pill Organizers:</strong> Use pill organizers with clear compartments for each day and time, labeled with large print.</li>\n  <li><strong>Medication Reminders:</strong> Set alarms, use reminder apps, or enlist help from family or caregivers to provide prompts.  </li>\n  <li><strong>Clear Communication:</strong> When assisting with medication, clearly explain what the medication is for and how it should be taken. </li>\n  <li><strong>Supervise Medication Intake:</strong>  If possible, supervise medication intake to ensure it is swallowed and not pocketed or spit out.</li>\n  <li><strong>Store Medications Securely:</strong>  Keep all medications in a safe, locked location out of reach, as individuals with cognitive impairment might not recognize them as potentially harmful. </li>\n  <li><strong>Regular Monitoring:</strong> Monitor for side effects, changes in behavior, or signs that the medication is not working effectively. Communicate any concerns to the doctor promptly.</li> \n</ul>\n\n<p><strong>Remember: </strong> Patience, understanding, and open communication with the individual and their healthcare providers are essential for safe and effective medication management. </p> \n```",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Are there specific considerations for individuals with chronic liver or kidney disease when it comes to medication selection and dosing?",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Medications and Liver or Kidney Disease: A Cautious Approach </h3>\n\n<p>Individuals with chronic liver or kidney disease require special attention when it comes to medication selection and dosing. This is because the liver and kidneys play vital roles in how our bodies process and eliminate drugs (metabolism and excretion).</p>\n\n<h4>Liver Disease Considerations:</h4>\n\n<ul>\n  <li><strong>Impaired Metabolism:</strong> The liver breaks down (metabolizes) most medications. Liver disease can impair this process, leading to a buildup of drugs in the body, increasing the risk of side effects and toxicity.</li>\n  <li><strong>Dosage Adjustments:</strong>  Lower doses or longer intervals between doses are often necessary to prevent drug accumulation. In some cases, certain medications might be avoided altogether.</li>\n  <li><strong>Monitoring:</strong> Close monitoring for side effects and drug levels (through blood tests) is crucial. </li>\n</ul>\n\n<h4>Kidney Disease Considerations:</h4>\n\n<ul>\n  <li><strong>Reduced Excretion:</strong> The kidneys filter waste products and medications from the blood. Kidney disease can impair excretion, leading to a buildup of drugs in the body. </li>\n  <li><strong>Dosage Adjustments:</strong> Dose reductions or longer intervals between doses are often necessary to prevent drug toxicity. Some medications may be contraindicated (not safe to use). </li>\n  <li><strong>Monitoring:</strong> Regular monitoring of kidney function (through blood and urine tests) is essential to guide medication adjustments.</li>\n</ul>\n\n<h4>Medications That Often Require Adjustments:</h4>\n\n<p>Many medications can be affected by liver or kidney disease. Some common examples include:</p>\n<ul>\n  <li>Pain relievers (NSAIDs like ibuprofen, naproxen)</li>\n  <li>Diabetes medications (metformin, some sulfonylureas)</li>\n  <li>Heart medications (some beta-blockers, ACE inhibitors)</li>\n  <li>Antibiotics (certain classes may need adjustments)</li>\n</ul>\n\n<h4>Key Points for Safe Medication Use:</h4>\n\n<ul>\n  <li><strong>Inform Your Doctor:</strong>  Always inform your doctor about any history of liver or kidney disease. This is crucial for selecting appropriate medications and dosages.</li>\n  <li><strong>Medication Reconciliation: </strong>  Bring a list of ALL medications, including over-the-counter drugs, herbs, and supplements, to each doctor's appointment to review for potential interactions or adjustments.</li>\n  <li><strong>Don't Self-Medicate:</strong>  Avoid taking new medications, even over-the-counter ones, without consulting your doctor.</li>\n  <li><strong>Report Side Effects: </strong>  Report any new or worsening side effects to your healthcare provider promptly. </li>\n</ul>\n\n<p><strong>Remember: </strong> Open communication and careful medication management are essential for individuals with liver or kidney disease. By working closely with their healthcare providers, they can minimize risks and optimize their treatment plans.</p>\n```\n\n",
                ],
            },
            # {
            #     "role": "user",
            #     "parts": [
            #         "This is the dummy.text file so this file contains the details of the inventory so refer this to answer the questions asked by the user make sure you give the correct answer",
            #         export_to_text_file(),
            #     ],
            # },
            {
                "role": "user",
                "parts": [
                    "This is the dummy.text file so this file contains the details of the inventory so refer this to answer the questions asked by the user make sure you give the correct answer",
                    dummy_text_content,
                ],
            },
            {
                "role": "model",
                "parts": [
                    "Okay, I've got the inventory details from  `dummy.txt` loaded and ready to use! \n\nAsk me anything about:\n\n* **Product stock levels** \n* **Product locations**\n* **Past product movements** \n* **Supplier details**\n* **Customer information**\n* **Sales records**\n\nI'm here to help you manage your inventory efficiently! Just let me know what you need. 😊 \n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "can i get to know the Product stock levels",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```html\n<h3>Current Product Stock Levels:</h3>\n\n<table>\n  <thead>\n    <tr>\n      <th>Product ID</th>\n      <th>Quantity in Stock</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <td>prod001</td>\n      <td>20</td>\n    </tr>\n    <tr>\n      <td>prod002</td>\n      <td>15</td>\n    </tr>\n  </tbody>\n</table>\n``` \n",
                ],
            },
        ]
    )

    if request.method == 'POST':
        user_prompt = request.json.get('data')
        print(user_prompt)
        
        response = chat_session.send_message(user_prompt)
        # print("\n ChatBot : ",response.text)
        
        return jsonify({"response" : response.text})
        
    return render_template('chatbot.html')



# 💡ChatRoom
rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code

@app.route("/chatroom/", methods=["POST", "GET"])
def chatroom():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")




with app.app_context():
    db.create_all()
    print("Database and tables created.")
    
if (__name__ == "__main__"):
    app.run(debug=True)
