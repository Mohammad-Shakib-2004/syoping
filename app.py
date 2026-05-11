import os

from werkzeug.utils import secure_filename



from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash,
    jsonify
)

import mysql.connector

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'

app.secret_key = "syoping_secret"

# DATABASE CONNECTION

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="test_db"
)

cursor = db.cursor(dictionary=True)

# HOME PAGE

@app.route('/')
def home():

    cursor.execute("SELECT * FROM products LIMIT 3")

    products = cursor.fetchall()

    return render_template(
        'home.html',
        products=products
    )


# SHOP PAGE

@app.route('/shop')
def shop():
    return render_template('shop.html')


# CATEGORIES PAGE

@app.route('/categories')
def categories():
    return render_template('categories.html')


# PRODUCTS PAGE

@app.route('/products')
def products():

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    return render_template(
        'products.html',
        products=products
    )


# PRODUCT DETAILS PAGE

@app.route('/product/<int:id>')
def product_details(id):

    cursor.execute(
        "SELECT * FROM products WHERE id = %s",
        (id,)
    )

    product = cursor.fetchone()

    return render_template(
        'product_details.html',
        product=product
    )


# CART PAGE

@app.route('/cart')
def cart():

    cart_items = []

    total = 0

    if 'cart' in session:

        cart = session['cart']

        for product_id, quantity in cart.items():

            cursor.execute(
                "SELECT * FROM products WHERE id = %s",
                (product_id,)
            )

            product = cursor.fetchone()

            if product:

                product['quantity'] = quantity

                product['subtotal'] = (
                    float(product['price']) * quantity
                )

                total += product['subtotal']

                cart_items.append(product)

    return render_template(
        'cart.html',
        cart_items=cart_items,
        total=total
    )


# CHECKOUT PAGE + ORDER SYSTEM

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        full_name = request.form['full_name']
        phone = request.form['phone']
        address_line = request.form['address_line']
        city = request.form['city']
        postal_code = request.form['postal_code']
        country = request.form['country']

        profile_image = request.files['profile_image']

        image_filename = ""

        if profile_image and profile_image.filename != '':

            image_filename = secure_filename(
                profile_image.filename
            )

            profile_image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    image_filename
                )
            )

        cart = session.get('cart', {})

        if not cart:
            return redirect('/cart')

        total_price = 0

        for product_id, quantity in cart.items():

            cursor.execute(
                "SELECT * FROM products WHERE id = %s",
                (product_id,)
            )

            product = cursor.fetchone()

            total_price += (
                float(product['price']) * quantity
            )

        # CREATE ORDER

        cursor.execute(
            """
            INSERT INTO orders
            (user_id, total_price, status)

            VALUES (%s, %s, %s)
            """,
            (
                session['user_id'],
                total_price,
                'Pending'
            )
        )

        db.commit()

        order_id = cursor.lastrowid

        # SAVE SHIPPING ADDRESS

        cursor.execute(
            """
            INSERT INTO shipping_addresses
            (
                user_id,
                full_name,
                phone,
                address_line,
                city,
                postal_code,
                country
            )

            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session['user_id'],
                full_name,
                phone,
                address_line,
                city,
                postal_code,
                country
            )
        )

        db.commit()

        # INSERT ORDER ITEMS

        for product_id, quantity in cart.items():

            cursor.execute(
                "SELECT * FROM products WHERE id = %s",
                (product_id,)
            )

            product = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    price
                )

                VALUES (%s, %s, %s, %s)
                """,
                (
                    order_id,
                    product_id,
                    quantity,
                    product['price']
                )
            )

        db.commit()

        # CLEAR CART

        session['cart'] = {}

        return redirect('/order_success')

    return render_template('checkout.html')


# ORDER SUCCESS

@app.route('/order_success')
def order_success():
    return render_template('order_success.html')


# MY ORDERS

@app.route('/my_orders')
def my_orders():

    if 'user_id' not in session:
        return redirect('/login')

    cursor.execute(
        """
        SELECT * FROM orders
        WHERE user_id = %s
        ORDER BY id DESC
        """,
        (session['user_id'],)
    )

    orders = cursor.fetchall()

    return render_template(
        'my_orders.html',
        orders=orders
    )














# PROFILE PAGE

@app.route('/profile', methods=['GET', 'POST'])
def profile():

    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    cursor = db.cursor(dictionary=True)

    # GET USER

    cursor.execute(
        "SELECT * FROM users WHERE id = %s",
        (user_id,)
    )

    user = cursor.fetchone()

    # GET PROFILE

    cursor.execute(
        "SELECT * FROM user_profiles WHERE user_id = %s",
        (user_id,)
    )

    profile = cursor.fetchone()

    # CREATE EMPTY PROFILE IF NOT EXISTS

    if not profile:

        cursor.execute(
            """
            INSERT INTO user_profiles (user_id)
            VALUES (%s)
            """,
            (user_id,)
        )

        db.commit()

        cursor.execute(
            "SELECT * FROM user_profiles WHERE user_id = %s",
            (user_id,)
        )

        profile = cursor.fetchone()

    # UPDATE PROFILE

    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        address_line = request.form['address_line']
        city = request.form['city']
        postal_code = request.form['postal_code']
        country = request.form['country']

        # IMAGE UPLOAD

        profile_image = request.files.get('profile_image')

        image_filename = profile['profile_image']

        if profile_image and profile_image.filename != '':

            image_filename = secure_filename(
                profile_image.filename
            )

            profile_image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    image_filename
                )
            )

        # UPDATE USERS TABLE

        cursor.execute(
            """
            UPDATE users
            SET
                fullname = %s,
                email = %s
            WHERE id = %s
            """,
            (
                fullname,
                email,
                user_id
            )
        )

        # UPDATE PROFILE TABLE

        cursor.execute(
            """
            UPDATE user_profiles
            SET
                phone = %s,
                profile_image = %s,
                address_line = %s,
                city = %s,
                postal_code = %s,
                country = %s
            WHERE user_id = %s
            """,
            (
                phone,
                image_filename,
                address_line,
                city,
                postal_code,
                country,
                user_id
            )
        )

        db.commit()

        flash("Profile updated successfully!")

        return redirect('/profile')

    return render_template(
        'profile.html',
        user=user,
        profile=profile
    )


























# ORDER DETAILS

@app.route('/order/<int:order_id>')
def order_details(order_id):

    if 'user_id' not in session:
        return redirect('/login')

    cursor.execute(
        """
        SELECT * FROM orders
        WHERE id = %s
        AND user_id = %s
        """,
        (
            order_id,
            session['user_id']
        )
    )

    order = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            order_items.*,
            products.name,
            products.image

        FROM order_items

        JOIN products
        ON order_items.product_id = products.id

        WHERE order_items.order_id = %s
        """,
        (order_id,)
    )

    items = cursor.fetchall()

    return render_template(
        'order_details.html',
        order=order,
        items=items
    )


# CONTACT PAGE

@app.route('/contact')
def contact():
    return render_template('contact.html')


# CUSTOMER LOGIN

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            """
            SELECT * FROM users
            WHERE email = %s
            AND password = %s
            """,
            (
                email,
                password
            )
        )

        user = cursor.fetchone()

        if user:

            session['user_id'] = user['id']

            flash("Login Successful!")

            return redirect('/')

        else:

            flash("Invalid Email or Password")

            return redirect('/login')

    return render_template('login.html')


# CUSTOMER REGISTER

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            flash("Email already registered!")

            return redirect('/register')

        cursor.execute(
            """
            INSERT INTO users
            (fullname, email, password)

            VALUES (%s, %s, %s)
            """,
            (
                fullname,
                email,
                password
            )
        )

        db.commit()

        flash("Account created successfully!")

        return redirect('/login')

    return render_template('register.html')


# USER LOGOUT

@app.route('/logout')
def logout():

    session.pop('user_id', None)

    flash("Logged out successfully!")

    return redirect('/')


# ADMIN LOGIN

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":

            session['admin'] = True

            return redirect('/admin_dashboard')

    return render_template('admin_login.html')


# ADMIN DASHBOARD

@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin' not in session:
        return redirect('/admin_login')

    return render_template('admin_dashboard.html')


# ADMIN ORDERS

@app.route('/admin_orders')
def admin_orders():

    if 'admin' not in session:
        return redirect('/admin_login')

    cursor.execute(
        """
        SELECT
            orders.*,
            users.fullname

        FROM orders

        JOIN users
        ON orders.user_id = users.id

        ORDER BY orders.id DESC
        """
    )

    orders = cursor.fetchall()

    return render_template(
        'admin_orders.html',
        orders=orders
    )


# UPDATE ORDER STATUS

@app.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):

    if 'admin' not in session:
        return redirect('/admin_login')

    status = request.form['status']

    cursor.execute(
        """
        UPDATE orders
        SET status = %s
        WHERE id = %s
        """,
        (
            status,
            order_id
        )
    )

    db.commit()

    flash("Order status updated!")

    return redirect('/admin_orders')


# MANAGE PRODUCTS

@app.route('/manage_products')
def manage_products():

    if 'admin' not in session:
        return redirect('/admin_login')

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    return render_template(
        'manage_products.html',
        products=products
    )


# ADD PRODUCT

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():

    if 'admin' not in session:
        return redirect('/admin_login')

    if request.method == 'POST':

        name = request.form['name']
        price = request.form['price']
        description = request.form['description']

        image = request.files['image']

        image_filename = secure_filename(
            image.filename
        )

        image.save(
            'static/images/' + image_filename
        )

        cursor.execute(
            """
            INSERT INTO products
            (name, price, image, description)

            VALUES (%s, %s, %s, %s)
            """,
            (
                name,
                price,
                image_filename,
                description
            )
        )

        db.commit()

        flash("Product added successfully!")

        return redirect('/manage_products')

    return render_template('add_product.html')


# EDIT PRODUCT

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):

    if 'admin' not in session:
        return redirect('/admin_login')

    cursor.execute(
        "SELECT * FROM products WHERE id = %s",
        (id,)
    )

    product = cursor.fetchone()

    if request.method == 'POST':

        name = request.form['name']
        price = request.form['price']
        description = request.form['description']

        image = request.files['image']

        if image.filename != "":

            image_filename = secure_filename(
                image.filename
            )

            image.save(
                'static/images/' + image_filename
            )

        else:

            image_filename = product['image']

        cursor.execute(
            """
            UPDATE products

            SET
                name = %s,
                price = %s,
                image = %s,
                description = %s

            WHERE id = %s
            """,
            (
                name,
                price,
                image_filename,
                description,
                id
            )
        )

        db.commit()

        flash("Product updated successfully!")

        return redirect('/manage_products')

    return render_template(
        'edit_product.html',
        product=product
    )


# DELETE PRODUCT

@app.route('/delete_product/<int:id>')
def delete_product(id):

    if 'admin' not in session:
        return redirect('/admin_login')

    cursor.execute(
        "DELETE FROM products WHERE id = %s",
        (id,)
    )

    db.commit()

    flash("Product deleted successfully!")

    return redirect('/manage_products')


# ADMIN LOGOUT

@app.route('/admin_logout')
def admin_logout():

    session.pop('admin', None)

    return redirect('/admin_login')


# ADD TO CART

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):

    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    product_id = str(id)

    if product_id in cart:

        cart[product_id] += 1

    else:

        cart[product_id] = 1

    session['cart'] = cart

    cart_count = sum(cart.values())

    return jsonify({
        "success": True,
        "message": "Product added to cart",
        "cart_count": cart_count
    })


# INCREASE QUANTITY

@app.route('/increase_quantity/<int:id>')
def increase_quantity(id):

    cart = session.get('cart', {})

    product_id = str(id)

    if product_id in cart:

        cart[product_id] += 1

    session['cart'] = cart

    return jsonify({
        "success": True
    })


# DECREASE QUANTITY

@app.route('/decrease_quantity/<int:id>')
def decrease_quantity(id):

    cart = session.get('cart', {})

    product_id = str(id)

    if product_id in cart:

        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    session['cart'] = cart

    return jsonify({
        "success": True
    })


# REMOVE FROM CART

@app.route('/remove_from_cart/<int:id>')
def remove_from_cart(id):

    cart = session.get('cart', {})

    product_id = str(id)

    if product_id in cart:
        del cart[product_id]

    session['cart'] = cart

    return jsonify({
        "success": True
    })


# CLEAR CART

@app.route('/clear_cart')
def clear_cart():

    session.pop('cart', None)

    return "Cart Cleared"









@app.route('/search')
def search():

    query = request.args.get('query')

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="test_db"
    )

    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM products
        WHERE name LIKE %s
    """

    search_term = "%" + query + "%"

    cursor.execute(sql, (search_term,))

    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "search_results.html",
        products=products,
        query=query
    )







@app.route('/live_search')
def live_search():

    query = request.args.get('query')

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="test_db"
    )

    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM products
        WHERE name LIKE %s
        LIMIT 5
    """

    search_term = "%" + query + "%"

    cursor.execute(sql, (search_term,))

    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(products)







# RUN APP

if __name__ == '__main__':
    app.run(debug=True)