###
#   module:     app.py   
#   Main app module
###

### external modules
from multiprocessing import synchronize
from unicodedata import category
from flask_cors import cross_origin
from flask import render_template, redirect, url_for, request, jsonify, session, Flask, g
from datetime import timedelta
import flask_login as flogin
import flask

### our modules
import database
import backend as be
import globals

### make global variables and cross module variables/classes less ugly
app = globals.app
db = database.db
user_logged_in = globals.user_logged_in
User = database.User
UserSchema = database.UserSchema
Category = database.Category
CategorySchema = database.CategorySchema
Order = database.Order
OrderSchema = database.OrderSchema
Product = database.Product
ProductSchema = database.ProductSchema

@(globals.loginManager).user_loader
def load_user(user_id):
    return be.getFlaskUser(user_id)

@app.before_request
def before_request():
    session.permanent = True
    flask.session.modified = True
    g.user = flogin.current_user
    if not '_user_id' in session:
        logout()

##
### Pages
##

@app.route('/', methods=['GET'])
@cross_origin()
def home():
    be.setCurrentPath(home.__name__)
    be.navigationSetPageActive('home')
    return render_template('/index.html', categories=database.getSubCategories(database.getCategoryByName('root')['id']), category=None, products=database.getProducts(), orders=database.getOrders(), logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_cats=database.getCategories(False), suggestions=database.getCategoryNames())

@app.route("/nav/offers", methods=["GET"])
def offers():
    be.setCurrentPath(offers.__name__)
    be.navigationSetPageActive('offers')
    return render_template('/offers.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, farmers=database.getUsersByRole(2), suggestions=database.getCategoryNames())
    
    
@app.route("/nav/login", methods=["GET"])
def login():
    be.setCurrentPath(login.__name__)
    be.navigationSetPageActive('login')
    return render_template('/login.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=False)

@app.route("/nav/registration", methods=["GET"])
def registration():
    be.setCurrentPath(registration.__name__)
    be.navigationSetPageActive('registration')
    return render_template('/registration.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=0)

@app.route("/nav/user/customer", methods=["GET"])
def user_customer():
    be.setCurrentPath(user_customer.__name__)
    be.navigationSetPageActive('user_customer')
    return render_template('/user/customer.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, suggestions=database.getCategoryNames(), all_suggestions=database.getCategorySuggestions())
    
@app.route("/nav/user/farmer", methods=["GET"])
def user_farmer():
    be.setCurrentPath(user_farmer.__name__)
    be.navigationSetPageActive('user_farmer')
    return render_template('my_product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProductsBySeller(be.getLoggedUser()['id']), nav_pages=globals.nav_pages, suggestions=database.getCategoryNames(), orders=database.getOrders())
    
@app.route("/nav/user/settings", methods=["GET"])
def user_settings():
    be.setCurrentPath(user_settings.__name__)
    be.navigationSetPageActive('user_settings')
    return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, showPassword=None, suggestions=database.getCategoryNames())

@app.route("/nav/admin/categories", methods=["GET"])
def admin_categories():
    be.setCurrentPath(admin_categories.__name__)
    be.navigationSetPageActive('admin_categories')
    fruits = be.getFruits()
    veggies = be.getVegetables()
    return render_template('/admin/categories.html', fruit_categories=fruits, veggie_categories=veggies, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, suggestions=database.getCategoryNames())

@app.route("/nav/admin/suggestions", methods=["GET"])
def admin_suggestions():
    be.setCurrentPath(admin_suggestions.__name__)
    be.navigationSetPageActive('admin_suggestions')
    suggestions = be.getCategorySuggestions(closed=False)
    closed_suggestions = be.getCategorySuggestions(closed=True)
    return render_template('/admin/suggestions.html', cat_suggestions=suggestions, closed_suggestions=closed_suggestions, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, suggestions=database.getCategoryNames())

@app.route("/nav/admin/users", methods=["GET"])
def admin_users():
    be.setCurrentPath(admin_users.__name__)
    be.navigationSetPageActive('admin_usres')
    return render_template('/admin/users.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=None, suggestions=database.getCategoryNames())

@app.route("/nav/cart", methods=["GET"])
def cart():
    be.setCurrentPath(cart.__name__)
    be.navigationSetPageActive('cart')
    user = be.getLoggedUser()
    items = be.getUserCart(user['id'])
    return render_template('/cart.html', cart_items=items, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, suggestions=database.getCategoryNames(), products=database.getProducts())

@app.route("/nav/cart/delete%id=<int:id>", methods=["GET"])
def cart_delete_item(id):
    user = be.getLoggedUser()
    items = be.getUserCart(user['id'])
    removal = None
    for i in items:
        if i['product_id'] == id:
            removal = i
    items.remove(removal)
    database.modifyData(database.User, user['id'], 'cart', items)
    return redirect(url_for('cart'))

##
### Actions, requests
##
@app.route('/', methods=['POST'])
def get_user():
    # get all results and return json
    users = User.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users))

###
###
###

@app.route("/login", methods=["POST"])
def login_user():
    login = request.form.get("login")
    password = request.form.get("pass")
    if (be.validateUser(login, password)):
        user = be.getUserRow(user_email=login)
        #be.setLoggedUser(user)
        newUser = database.FlaskUser(user['id'], user['email'])
        flogin.login_user(newUser)
        #be.getLoggedUser()s.append(newUser)
        return redirect(url_for('home'))
    else:
        return render_template('/login.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=True)

@app.route("/logout", methods=["GET"])
def logout():
    flogin.logout_user()
    be.logoutUser()
    return redirect(url_for('home')) 

@app.route("/register", methods=["POST"])
def register_user():
    global user_logged_in
    login = request.form.get("login")
    password = request.form.get("pass")
    password2 = request.form.get("pass_repeat")
    name = request.form.get("name")
    isFarmer = request.form.get("role")
    if (password != password2):
        return render_template('/registration.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=-1)
    result = be.newUser(login, password, name, 3 - int(isFarmer))
    if (result == 0):
        user = database.getUserByEmail(login)
        #be.setLoggedUser(user)
        newUser = database.FlaskUser(user['id'], user['email'])
        flogin.login_user(newUser)
        return redirect(url_for('home'))     # or: after registration page
    else:
        return render_template('/registration.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=result)

@app.route("/nav/admin/users/<int:id>")
def admin_selected_user(id):
    return render_template('/admin/users.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=id, error=0, confirm=None, suggestions=database.getCategoryNames())

@app.route("/nav/admin/users/<int:id>", methods=["POST"])
def admin_selected_user_action(id):
    if 'user_btn' in request.form.keys() and request.form['user_btn'] == "0":
        return render_template('/admin/users.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=id, error=0, confirm=True)

    if 'modify_btn' in request.form.keys() and request.form['modify_btn'] == "0":
        return render_template('/admin/users_selected.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=-1)
    
    if 'reset_btn' in request.form.keys() and request.form['reset_btn'] == "0":
        return redirect(url_for('admin_users'))

    if be.getLoggedUser()['id'] == id:
        s = id
        error = 1
    else:
        r = be.removeUser(id)
        if (r != None):
            return be.printInternalError(r)
        s = None
        error = 0
    return render_template('/admin/users.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=s, error=error, confirm=False)
    
@app.route("/nav/admin/users/remove/<int:id>", methods=["GET"])
def admin_selected_user_remove(id):
    if be.getLoggedUser()['id'] == id:
        s = id
        error = 1
    else:
        r = be.removeUser(id)
        if (r != None):
            return be.printInternalError(r)
        s = None
        error = 0
    return render_template('/admin/users.html', done=True, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedID=s, error=error, confirm=False)
    

@app.route("/nav/admin/user_selected/<int:id>", methods=["POST"])
def admin_user_selected(id):
    be.setCurrentPath(admin_user_selected.__name__)
    be.addPathArgument('id', id)
    error = 0
    name = request.form['name']
    user = be.getUserRow(id)
    if ('email' in request.form):
        email = request.form['email']
    else:
        email = user['email']
    role = request.form['role']
    if ('permissions' in request.form):
        permissions = request.form['permissions']
    else:
        permissions = user['role']
    birthday = request.form['birthday']
    address = request.form['address']
    phone = request.form['phone']
    if ('password' in request.form):
        password = request.form['password']
    else:
        password = user['password']

    new_role = 4
    if (int(role) < 0):
        new_role = permissions
    else:
        new_role = role

    user = be.getUserRow(id)
    if (user['password'] == password and user['name'] == name and user['email'] == email and user['role'] == int(new_role) and user['birth_date'] == birthday and user['address'] == address and str(user['phone_number']) == phone):
        return render_template('/admin/users_selected.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=-1, suggestions=database.getCategoryNames())

    r = be.isEmail(email)
    if (r != 0 and user['email'] != email):
        return render_template('/admin/users_selected.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=r)

    r = be.isName(name)
    if (r != 0):
        return render_template('/admin/users_selected.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=r)
    
    r = be.isPassword(password)
    if (r != 0):
        return render_template('/admin/users_selected.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=r)
    
    r = be.isPhoneNumber(phone)
    if (r != 0):
        return render_template('/admin/users_selected.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=r)
    
    r = be.isDate(birthday)
    if (r != 0):
        return render_template('/admin/users_selected.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=r)
    
    r = be.isAddress(address)
    if (r != 0):
        return render_template('/admin/users_selected.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=r)

    be.editUserData(id, 'name', name)
    be.editUserData(id, 'email', email)
    be.editUserData(id, 'role', new_role)
    be.editUserData(id, 'birth_date', birthday)
    be.editUserData(id, 'address', address)
    be.editUserData(id, 'phone_number', phone)
    be.editUserData(id, 'password', password)
    return render_template('/admin/users_selected.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, all_users=database.getUsers(), selectedUser=database.getUser(id), error=error, suggestions=database.getCategoryNames())
  
#renders home page with all subcategories of selected category
@app.route("/home/cat=<string:id>", methods=["GET"])
def category(id):
    cat = database.getCategory(int(id))
    is_leaf = cat['leaf']
    if is_leaf:
        return render_template('/index.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, category=cat, products=database.getProductsByCategory(id), suggestions=database.getCategoryNames(), products_count=len(database.getProductsByCategory(id)))
    else:
        return render_template('/index.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, category=cat, categories=database.getSubCategories(id), suggestions=database.getCategoryNames())
    
@app.route("/product/<int:id>", methods=["GET"])
def product(id):
    prod = database.getProduct(id)
    return render_template('/product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, product=prod, seller=database.getUser(database.getProduct(id)['seller']), suggestions=database.getCategoryNames())

@app.route("/product/<int:id>", methods=["POST"])
def create_order(id):
    return render_template('/product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, product=database.getProduct(id), seller=database.getUser(database.getProduct(id)['seller']), suggestions=database.getCategoryNames())

@app.route("/farmer/<int:id>", methods=["GET"])
def open_farmer(id):
    return render_template('/user/farmer.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, farmer=database.getUser(id), products=database.getProductsBySeller(id), suggestions=database.getCategoryNames())

@app.route("/home/search>", methods=["POST"])
def search():
    name = request.form['search']
    cat = database.getCategoryByName(name)
    prod = database.getProductByNameOnly(name)
    if cat:
        if cat['leaf']:
            return render_template('/index.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, category=cat, products=database.getProductsByCategory(cat['id']), suggestions=database.getCategoryNames())
        else:
            return render_template('/index.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, category=cat, categories=database.getSubCategories(cat['id']), suggestions=database.getCategoryNames())
    elif prod:
        return render_template('/product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, product=database.getProduct(prod['id']), seller=database.getUser(prod['seller']), suggestions=database.getCategoryNames())
    else:
        return render_template('/index.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, suggestions=database.getCategoryNames(), category='not found', product='not found')

@app.route("/nav/user/customer/<int:id>", methods=["POST"])
def create_suggestion(id):
    name = request.form['category_name']
    parent = request.form['category_parent']
    description = request.form['category_description']
    leaf = request.form.get('final', False)
    if leaf == 'final':
        leaf = True
        
    
    parent_db = database.getCategoryByName(parent)
    if parent_db is None:
        return render_template('/user/customer.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=1, suggestions=database.getCategoryNames(), all_suggestions=database.getCategorySuggestions())

    if parent_db['leaf']:
        return render_template('/user/customer.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, error=2, suggestions=database.getCategoryNames(), all_suggestions=database.getCategorySuggestions())
    
    database.addCategorySuggestion(name, parent_db['id'],  leaf, description, id)
    return render_template('/user/customer.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), error=0, nav_pages=globals.nav_pages, suggestions=database.getCategoryNames(), all_suggestions=database.getCategorySuggestions())
 
@app.route("/nav/user/<int:id>", methods=["GET"])
def product_edit(id):
    product = database.getProduct(id)
    return render_template('my_product_selected.html', error=0, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, category=database.getCategory(product['category']) , product=product , products=database.getProductsBySeller(id), suggestions=database.getCategoryNames())

@app.route("/nav/user/farmer/remove<int:id>", methods=["POST"])
def product_remove(id):
    product = database.getProduct(id)
    be.removeProduct(id)
    return redirect(url_for('user_farmer'))

@app.route("/nav/admin/product_remove%id=<int:id>", methods=["GET"])
def product_remove_admin(id):
    product = database.getProduct(id)
    be.removeProduct(id)
    return redirect(url_for('admin_categories'))

@app.route("/nav/user/farmer/edit<int:id>", methods=["POST"])
def save_product_edit(id):
    product = database.getProduct(id)
    name = request.form['name']
    price = request.form['price']
    sell_type = request.form['sell_type']
    quantity = request.form['quantity']
    description = request.form['description']
    self_harvest = request.form['self_harvest']
    begin_date = request.form['begin_date']
    end_date = request.form['end_date']

    name_db = database.getProductByNameOnly(name)
    
    if name_db is not None and name_db['id'] != id:
        return render_template('my_product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, category=database.getCategory(product['category']) , product=product , products=database.getProductsBySeller(product['seller']), suggestions=database.getCategoryNames(), error=1, orders=database.getOrders())
    
    r = be.isName(name)
    if (r != 0):
        return render_template('my_product_selected.html', error=r, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, category=database.getCategory(product['category']) , product=product , products=database.getProductsBySeller(id), suggestions=database.getCategoryNames())

    r = be.isPrice(price)
    if (r != 0):
        return render_template('my_product_selected.html', error=r, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, category=database.getCategory(product['category']) , product=product , products=database.getProductsBySeller(id), suggestions=database.getCategoryNames())

    r = be.isQuantity(quantity)
    if (r != 0):
        return render_template('my_product_selected.html', error=r, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, category=database.getCategory(product['category']) , product=product , products=database.getProductsBySeller(id), suggestions=database.getCategoryNames())

    be.editProductData(id, 'name', name)
    be.editProductData(id, 'price', price)
    be.editProductData(id, 'sell_type', sell_type)
    be.editProductData(id, 'quantity', quantity)
    be.editProductData(id, 'description', description)
    
    
    if self_harvest == "True":
        be.editProductData(id, 'self_harvest', True)
        be.editProductData(id, 'begin_date', begin_date)
        be.editProductData(id, 'end_date', end_date)
    else:
        be.editProductData(id, 'self_harvest', False)
        be.editProductData(id, 'begin_date', None)
        be.editProductData(id, 'end_date', None)
    
    return render_template('my_product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, products=database.getProductsBySeller(product['seller']), suggestions=database.getCategoryNames(), category=database.getCategory(product['category']), product=product, error=0, orders=database.getOrders())

@app.route("/nav/user/new_product", methods=["GET"])
def create_product():
    return render_template('create_product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, suggestions=database.getLeafCategories())

@app.route("/nav/user/new_product", methods=["POST"])
def create_new_product():
    name = request.form['name']
    category = request.form['category']
    price = request.form['price']
    sell_type = request.form['sell_type']
    quantity = request.form['quantity']
    description = request.form['description']
    self_harvest = request.form['self_harvest']
    begin_date = request.form['begin_date']
    end_date = request.form['end_date']
    user=be.getLoggedUser()
    
    name_db = database.getProductByNameOnly(name)
    category_db = database.getCategoryByName(category)
    
    if name_db is not None:
        return render_template('my_product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProductsBySeller(user['id']), nav_pages=globals.nav_pages, suggestions=database.getCategoryNames(), error=2, orders=database.getOrders())
    
    if category_db is None:
        return render_template('my_product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProductsBySeller(user['id']), nav_pages=globals.nav_pages, suggestions=database.getCategoryNames(), error=3, orders=database.getOrders())
    
    if category_db['leaf'] == False:
        return render_template('my_product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProductsBySeller(user['id']), nav_pages=globals.nav_pages, suggestions=database.getCategoryNames(), error=4, orders=database.getOrders())
    
    if self_harvest == "True":
        self_harvest = True
    else:
        self_harvest = False
        begin_date = None
        end_date = None
        
    database.addProduct(name, category_db['id'], quantity, user['id'], price, sell_type, description, self_harvest, begin_date, end_date)
    return render_template('my_product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProductsBySeller(user['id']), nav_pages=globals.nav_pages, suggestions=database.getCategoryNames(), error=-1, orders=database.getOrders())
        
@app.route("/nav/user/order_confirm%id=<int:id>", methods=["GET"])
def order_status_complete(id):
    user = be.getLoggedUser()
    be.editCategoryData(id, 'status', 0)
    
    order = database.getOrder(id)
        
    return render_template('my_product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProductsBySeller(user['id']), nav_pages=globals.nav_pages, orders=database.getOrders(), suggestions=database.getCategoryNames(), error=6)

@app.route("/nav/user/order_cancel%id=<int:id>", methods=["GET"])
def order_status_cancel(id):
    user = be.getLoggedUser()
    be.editCategoryData(id, 'status', -1)
        
    return render_template('my_product.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProductsBySeller(user['id']), nav_pages=globals.nav_pages, orders=database.getOrders(), suggestions=database.getCategoryNames(), error=7)

  
@app.route("/nav/user/settings/orders", methods=["GET"])
def user_settings_orders():
    be.setCurrentPath(user_settings_orders.__name__)
    user = be.getLoggedUser()
    orders = be.getUserOrders(user)
    return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, page=1, user_orders=orders, suggestions=database.getCategoryNames())

@app.route("/nav/user/settings/calendar", methods=["GET"])
def user_settings_calendar():
    be.setCurrentPath(user_settings_calendar.__name__)
    user = be.getLoggedUser()
    cal = be.getUserCalendar(user)
    return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, page=2, user_calendar=cal, suggestions=database.getCategoryNames())

@app.route("/nav/user/settings/order/<int:id>", methods=["GET"])
def user_settings_order(id):
    be.setCurrentPath(user_settings_order.__name__)
    be.addPathArgument('id', id)
    order = database.getOrder(id)
    prod = order['product_list']
    quan = order['quantity_list']
    return render_template('/user/settings/order.html', order=order, quantities=quan, product_ids=prod, logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, actionShow=True, suggestions=database.getCategoryNames())

@app.route("/nav/user/settings/calendar/<int:id>", methods=["GET"])
def user_settings_event(id):
    be.setCurrentPath(user_settings_event.__name__)
    be.addPathArgument('id', id)
    cal = be.getUserCalendar(be.getLoggedUser())
    event = be.getCalendarEvent(cal, id)
    prod = database.getProduct(event[0], True)
    seller = database.getUser(prod['seller'])
    return render_template('/user/settings/calendar.html', logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, product=prod, seller=seller, eventDate=event[1], eventIndex=id, actionShow=True, suggestions=database.getCategoryNames())


@app.route("/nav/user/settings/account_removal", methods=["GET"])
def user_settings_accountRemoval():
    be.setCurrentPath(user_settings_accountRemoval.__name__)
    return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=3, user_calendar=be.getUserCalendar(be.getLoggedUser()))

@app.route("/nav/user/settings/edit_personal", methods=["GET"])
def user_settings_edit_personal():
    return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), edit=True, editType=0)

@app.route("/nav/user/settings/edit_login", methods=["GET"])
def user_settings_edit_login():
    return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), edit=True, editType=1)

@app.route("/nav/user/settings/edit_save/<int:t>", methods=["POST"])
def user_settings_edit_save(t):
    if (t == 0):
        bday = request.form['birthday']
        address = request.form['address']
        phone = request.form['phone']
        name = request.form['name']
        user = be.getLoggedUser()
        
        if (name == user['name'] and bday == user['birth_date'] and address == user['address'] and phone == str(user['phone_number'])):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=0, saved=True, error=-1)
        
        if (len(name) == 0):
            user = "User"

        r = be.isName(name)
        if (r != 0):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=0, saved=True, error=r)
        r = be.isDate(bday)
        if (r != 0):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=0, saved=True, error=r)
        r = be.isAddress(address)
        if (r != 0):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=0, saved=True, error=r)    
        r = be.isPhoneNumber(phone)
        if (r != 0):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=0, saved=True, error=r)
        
        
        be.editUserData(user['id'], 'name', name)
        be.editUserData(user['id'], 'birth_date', bday)
        be.editUserData(user['id'], 'address', address)
        be.editUserData(user['id'], 'phone_number', phone)
        return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=0, saved=True, error=0)
    elif (t == 1):
        email = request.form['email']
        password = request.form['password']
        user = be.getLoggedUser()
    
        if (email == user['email'] and password == user['password']):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=-1)
        
        if (email == user['email']):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), edit=True, editType=1, confirmPass=False, newPass=password)
        
        r = be.isEmail(email)
        if (r != 0):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=r)

        be.editUserData(user['id'], 'email', email)
        if (password == user['password']):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=0)
        return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), edit=True, editType=1, confirmPass=False, newPass=password)
    else:
        email = request.form['email']
        password = request.form['password']
        repeat = request.form['passconfirm']
        user = be.getLoggedUser()

        if (repeat != password):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=-2)
        
        r = be.isEmail(email)
        if (r != 0):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=r)
        
        r = be.isPassword(password)
        if (r != 0):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=r)

        be.editUserData(user['id'], 'email', email)
        be.editUserData(user['id'], 'password', password)
        return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=0, user_calendar=be.getUserCalendar(be.getLoggedUser()), editType=1, saved=True, error=0)
    
@app.route("/nav/user/settings/remove", methods=["POST"])
def user_settings_removeAccount():
    password = request.form['password']
    if (password != be.getLoggedUser()['password']):
            return render_template('/user/settings.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, page=3, user_calendar=be.getUserCalendar(be.getLoggedUser()), error=0)
    
    r = be.removeUser()
    if (r != None):
        return be.printInternalError(r)
    be.logoutUser()
    return redirect(url_for('home')) 

@app.route("/nav/user/settings/order/cancel%id=<int:id>", methods=["GET"])
def user_settings_order_cancel(id):
    order = database.getOrder(id)
    prod = order['product_list']
    quan = order['quantity_list']
    return render_template('/user/settings/order_cancel.html', order=order, quantities=quan, product_ids=prod, logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, actionShow=False, suggestions=database.getCategoryNames())

@app.route("/nav/user/settings/order/cancel/go%id=<int:id>", methods=["POST"])
def user_settings_order_cancel_go(id):
    order = database.getOrder(id)
    products = order['product_list']
    quantities = order['quantity_list']
    i = 0
    for product_id in products:
        c_prod = database.getProduct(product_id)
        database.modifyData(database.Product, product_id, 'quantity', c_prod['quantity'] + quantities[i])
        i = i + 1
    database.modifyData(database.Order, id, 'status', -1)
    return redirect(url_for('user_settings_orders'))

@app.route("/product/<int:id>%review_send", methods=["POST"])
def product_review(id):
    prod = database.getProduct(id)
    user = be.getLoggedUser()
    database.addProductReview(prod['id'], user['id'], request.form['review_desc'], int(request.form['review_select']))
    database.modifyData(database.Order, id, 'status', 2)
    return product(id)

@app.route("/nav/user/settings/order/repeat%id=<int:id>%page=<int:page>", methods=["GET"])
def user_settings_order_repeat(id, page):
    order = database.getOrder(id)
    prod = database.getProduct(order['product'])
    seller = database.getUser(prod['seller'])
    if (page == 0):
        return render_template('/user/settings/order_repeat.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, order=order, product=prod, seller=seller, page=0)
    elif (page == 1):
        return render_template('/user/settings/order_repeat.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, order=order, product=prod, seller=seller, page=1)
    elif (page == 2):
        return render_template('/user/settings/order_repeat.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, order=order, product=prod, seller=seller, page=2)
    else:
        return redirect(url_for('user_settings_orders'))

@app.route("/nav/new_order%id=<int:id>%repeat=<int:isRepeat>%quantity=<int:quantity>", methods=["GET"])
def new_order(id, isRepeat, quantity):
    be.setCurrentPath(new_order.__name__)
    be.addPathArgument('id', id)
    be.addPathArgument('isRepeat', isRepeat)
    be.addPathArgument('quantity', quantity)
    if (isRepeat == 1):
        user = be.getLoggedUser()
        order = database.getOrder(id)
        temp_cart = []
        i = 0
        for prod_id in order['product_list']:
            item = be.userCartNewItem(prod_id, order['quantity_list'][i])
            temp_cart.append(item)
            i = i + 1
        cart = temp_cart
        globals.temp_cart = cart
        total_cart_price = be.getTotalCartPrice(None, temp_cart)
        return render_template('/new_order.html', order=order, total_price=total_cart_price, cart=cart, isRepeat=True, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages)
    else:
        user = be.getLoggedUser()
        cart = be.getUserCart(user['id'])
        total_cart_price = be.getTotalCartPrice(user['id'])
        return render_template('/new_order.html', total_price=total_cart_price, cart=cart, isRepeat=False, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages)

@app.route("/product/order_product%id=<int:id>", methods=["POST"])
def order_product(id):
    quantity = request.form['quantity']
    return redirect(url_for('new_order', id=id, isRepeat=0, quantity=quantity))

@app.route("/product/cart_add%id=<int:id>", methods=["POST"])
def add_to_cart(id):
    quantity = request.form['quantity']
    item = be.userCartNewItem(id, quantity)
    u = be.getLoggedUser()
    be.userCartAddItem(u['id'], item)
    return render_template('/product.html', added_to_cart=True,logged=be.isUserLogged(), user=be.getLoggedUser(), products=database.getProducts(), nav_pages=globals.nav_pages, product=database.getProduct(id), seller=database.getUser(database.getProduct(id)['seller']), suggestions=database.getCategoryNames())
 
@app.route("/nav/new_event%id=<int:id>", methods=["GET"])
def new_event(id):
    user = be.getLoggedUser()
    be.addCalendarEvent(user, id)
    return redirect(url_for('home'))

@app.route("/nav/user/settings/calendar/remove_q%id=<int:id>", methods=["GET"])
def user_settings_calendar_remove_q(id):
    cal = be.getUserCalendar(be.getLoggedUser())
    event = be.getCalendarEvent(cal, id)
    prod = database.getProduct(event[0])
    seller = database.getUser(prod['seller'])
    return render_template('/user/settings/calendar_cancel.html', logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, product=prod, seller=seller, eventDate=event[1], eventIndex=id)

@app.route("/nav/user/settings/calendar/remove%id=<int:id>", methods=["POST"])
def user_settings_calendar_remove(id):
    loggedUser = be.getLoggedUser()
    cal = be.getUserCalendar(loggedUser)
    event = be.getCalendarEvent(cal, id)
    cal.remove(event)

    database.modifyData(database.User, loggedUser['id'], 'calendar', cal)
    return redirect(url_for('user_settings_calendar'))

@app.route("/nav/admin/category_detail%id=<int:id>", methods=["GET"])
def admin_categories_detail(id):
    be.setCurrentPath(admin_categories_detail.__name__)
    be.addPathArgument('id', id)
    category = database.getCategory(id)
    subs = be.getSubCategories(category['id'])
    return render_template('/admin/categories_detail.html', category=category, subcategories=subs, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages)
 
@app.route("/nav/admin/category_remove%id=<int:id>", methods=["GET"])
def admin_categories_remove(id):
    category = database.getCategory(id)
    higher_id = category['higher_category']
    be.removeCategory(category)

    higher = database.getCategory(higher_id)
    root = database.getCategoryByName('root')
    if (higher['higher_category'] == root['id']):
        return admin_categories()
    else:
        return admin_categories_detail(higher_id)

@app.route("/nav/admin/category_edit%id=<int:id>%type=<int:type>", methods=["GET"])
def admin_categories_edit(id, type):
    category = database.getCategory(id)
    subs = be.getSubCategories(category['id'])
    fruits = be.getFruits()
    veggies = be.getVegetables()
    if (type == 1):
        return render_template('/admin/categories.html', fruit_categories=fruits, veggie_categories=veggies, edit=True, editID=id, category=category, subcategories=subs, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages)
    else:
        higher = database.getCategory(category['higher_category'])
        category = higher
        subs = be.getSubCategories(category['id'])
        return render_template('/admin/categories_detail.html', fruit_categories=fruits, veggie_categories=veggies, edit=True, editID=id, category=category, subcategories=subs, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages)
    

@app.route("/nav/admin/category_edit_go%type=<int:type>%id=<int:id>", methods=["POST"])
def admin_category_edit(type, id):
    category = database.getCategory(id)
    subs = be.getSubCategories(category['id'])
    fruits = be.getFruits()
    veggies = be.getVegetables()
    newname = request.form['newname']
    database.modifyData(database.Category, category['id'], 'name', newname)
    if (type == 1):
        return redirect(url_for('admin_categories'))
    else:
        return redirect(url_for('admin_categories_detail', id=category['higher_category']))

@app.route("/nav/admin/suggestion_approve%id=<int:id>", methods=["GET"])
def admin_suggestion_approve(id):
    category = database.getCategorySuggestion(id)
    database.modifyData(database.CategorySuggestion, id, 'status', 1)
    database.addCategory(category['name'], category['higher_category'], category['leaf'])
    return admin_suggestions()

@app.route("/nav/admin/suggestion_deny%id=<int:id>", methods=["GET"])
def admin_suggestion_deny(id):
    category = database.getCategorySuggestion(id)
    database.modifyData(database.CategorySuggestion, id, 'status', 2)
    return admin_suggestions()


### TODO:
### Dont create order immediately but create sub-step 'summary' page and then create order
@app.route("/nav/new_order/go?isRepeat=<int:isRepeat>", methods=["POST"])
def new_order_go(isRepeat):
    buyer = be.getLoggedUser()
    if (isRepeat):
        cart = globals.temp_cart
    else:
        cart = be.getUserCart(buyer['id'])
    order = globals.last_url
    total_price = be.getTotalCartPrice(None, cart)

    for item in cart:
        prod = database.getProduct(item['product_id'])
        newQuantity = prod['quantity'] - int(item['quantity'])
        if newQuantity < 0:
            r = 164
            return render_template('/new_order.html', errorItem=item['product_id'], errorCode=r, repeatedOrder=True, logged=be.isUserLogged(), user=be.getLoggedUser(), nav_pages=globals.nav_pages, order=order)
    
    prod_list = []
    quantity_list = []
    for item in cart:
        prod = database.getProduct(item['product_id'])
        prod_list.append(item['product_id'])
        quantity_list.append(int(item['quantity']))
        newQuantity = prod['quantity'] - int(item['quantity'])
        database.modifyData(database.Product, prod['id'], 'quantity', newQuantity)

    be.addOrder(buyer['id'], prod_list, quantity_list, total_price)
    database.modifyData(database.User, buyer['id'], 'cart', [])
    globals.temp_cart = []
    return redirect(url_for('home'))

#####
###     INIT AND RUN
#####


be.loadJinjaGlobals()
be.navigationLoadPages()
be.logoutUser()

if __name__ == '__main__': 
    be.init()
    globals.app.run(debug=True)
