###
#   module:     backend.py   
#   Backend module
###

import globals
import database
import re
import datetime
import random
from flask import session, g

db = database
nav_current_page = globals.nav_current_page
logged_user = globals.logged_user

###
#   Functions and variables available in FrontEnd (Jinja2)
###

# load and init all functions to jinja2
def loadJinjaGlobals():
    app = globals.app
    app.jinja_env.globals.update(getSelfCollectionLocation=getSelfCollectionLocation)
    app.jinja_env.globals.update(getLoggedUserOrders=getLoggedUserOrders)
    app.jinja_env.globals.update(getLoggedUserSells=getLoggedUserSells)
    app.jinja_env.globals.update(getUsedCurrency=getUsedCurrency)
    app.jinja_env.globals.update(orderStatusToString=orderStatusToString)
    app.jinja_env.globals.update(productSellTypeToString=productSellTypeToString)
    app.jinja_env.globals.update(getMaxStringLength=getMaxStringLength)
    app.jinja_env.globals.update(getCategoryProducts=getCategoryProducts)
    app.jinja_env.globals.update(getUserName=getUserName)
    app.jinja_env.globals.update(getCategoryName=getCategoryName)
    app.jinja_env.globals.update(suggestionResultToString=suggestionResultToString)
    app.jinja_env.globals.update(getUserEmail=getUserEmail)
    app.jinja_env.globals.update(checkSuggestionConflicts=checkSuggestionConflicts)
    app.jinja_env.globals.update(getUserBirthdate=getUserBirthdate)
    app.jinja_env.globals.update(getUserAddress=getUserAddress)
    app.jinja_env.globals.update(getUserPhoneNumber=getUserPhoneNumber)
    app.jinja_env.globals.update(getProductReviews=getProductReviews)
    app.jinja_env.globals.update(getCartProductPrice=getCartProductPrice)
    app.jinja_env.globals.update(getProductSellerName=getProductSellerName)
    app.jinja_env.globals.update(getProductName=getProductName)
    app.jinja_env.globals.update(userWrittenReview=userWrittenReview)
    app.jinja_env.globals.update(userBoughtProduct=userBoughtProduct)
    app.jinja_env.globals.update(isMyProduct=isMyProduct)
    app.jinja_env.globals.update(isProductActive=isProductActive)
    app.jinja_env.globals.update(getProductQuantityString=getProductQuantityString)
    app.jinja_env.globals.update(zip=zip)
    app.jinja_env.globals.update(getProductSellType=getProductSellType)
    app.jinja_env.globals.update(today=today)
    app.jinja_env.globals.update(getRandomProducts=getRandomProducts)

def getRandomProducts():
    ps = database.getProducts()
    cnt = random.choice([3, 4, 5])
    l = []
    if (cnt > len(ps)):
        cnt = len(ps)
    for i in range(0, cnt):
        prod = random.choice(ps)
        l.append(prod)
    return l



def isProductActive(product_id):
    p = database.getProduct(product_id, True)
    return p['active']

def today():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def getProductSellType(product_id):
    p = database.getProduct(product_id)
    if p['sell_type'] == 0:
        return "pieces"
    elif p['sell_type'] == 1:
        return "kg"
    elif p['sell_type'] == 2:
        return "g"
    else:
        return "Unknown sell type "+str(p['sell_type'])

def isMyProduct(user_id, product_id):
    return database.isSellingProduct(product_id, user_id)

def userBoughtProduct(user_id, product_id):
    u = database.getUser(user_id)
    o = getUserOrders(u)
    for order in o:
        for bought_product_id in order['product_list']:
            if (bought_product_id == product_id):
                if (order['status'] == 0):
                    return True
    return False

def userWrittenReview(user_id, product_id):
    u = database.getUser(user_id)
    p_reviews = database.getReviewsOfProduct(product_id)
    for review in p_reviews:
        if review['reviewer_id'] == user_id:
            return True
    return False

def getCartProductPrice(product_id, quantity, inactive=False):
    p = database.getProduct(product_id, inactive)
    return (p['price'] * int(quantity))

def getProductSellerName(product_id):
    p = database.getProduct(product_id)
    s = database.getUser(p['seller'])
    return s['name']

def getProductName(product_id, inactive=False):
    p = database.getProduct(product_id, inactive)
    return p['name']

def getProductReviews(product_id):
    return database.getReviewsOfProduct(product_id)

def getUserPhoneNumber(user_element):
    data = user_element['phone_number']
    if data == None:
        return ""
    else:
        return data

def getUserAddress(user_element):
    data = user_element['address']
    if data == None:
        return ""
    else:
        return data

def getUserBirthdate(user_element):
    data = user_element['birth_date']
    if data == None:
        return ""
    else:
        return data

def checkSuggestionConflicts(sugg_id, higher_id):
    sugg = database.getCategorySuggestion(sugg_id)
    parent_category = database.getCategory(higher_id)
    if (sugg['name'] == parent_category['name']):
        return parent_category
    else:
        subcats = getSubCategories(higher_id)
        for cat in subcats:
            if (cat['name'] == sugg['name']):
                return cat
    return None

def getUserEmail(user_id):
    u = database.getUser(user_id)
    return u['email']

def suggestionResultToString(result):
    if (result == 0):
        return "Pending"
    elif (result == 1):
        return "Approved"
    else:
        return "Denied"

def userCartNewItem(product_id, quantity):
    item = {
        "product_id": product_id,
        "quantity": quantity
    }
    return item

def userCartAddItem(user_id, item):
    u = database.getUser(user_id)
    c = u['cart']
    c.append(item)
    database.modifyData(database.User, user_id, 'cart', c)

def userCartRemoveItem(user_id, item):
    u = database.getUser(user_id)
    c = u['cart']
    c.remove(item)
    database.modifyData(database.User, user_id, 'cart', c)

def getTotalCartPrice(user_id, temp_cart=None):
    if (user_id == None):
        c = temp_cart
    else:
        u = database.getUser(user_id)
        c = u['cart']
    price = 0
    for item in c:
        price = price + getCartProductPrice(item['product_id'], item['quantity'])
    return price

def getUserCart(user_id):
    u = database.getUser(user_id)
    return u['cart']

def getUserName(user_id):
    u = database.getUser(user_id)
    return u['name']

def getCategoryName(category_id):
    c = database.getCategory(category_id)
    return c['name']

def getCategoryProducts(category_id):
    l = []
    for prod in database.getProducts():
        if (prod['category'] == category_id):
            l.append(prod)
    return l

def getMaxStringLength():
    return database.DB_STRING_LONG_MAX

def getProductQuantityString(product_id):
    p = database.getProduct(product_id)
    type = p['sell_type']
    if (type == 0):
        return "pieces"
    elif (type == 1):
        return "kg"
    elif (type == 2):
        return "g"
    else:
        return "?"

def productSellTypeToString(sell_type):
    if sell_type == 0:
        return "in pieces"
    elif sell_type == 1:
        return "in 1 kg"
    elif sell_type == 2:
        return "in 1 g"
    else:
        return "Unknown sell type "+str(sell_type)

def orderStatusToString(order_status):
    if order_status == 0:
        return "Completed"
    elif order_status == 1:
        return "Processing"
    elif order_status == 2:
        return "Reviewed"
    elif order_status == -1:
        return "Cancelled"
    else:
        return "Unknown"

def getUsedCurrency():
    return "ISC"

def getLoggedUserSells():
    list = []
    product_list = []
    user = getLoggedUser()
    if user == None:
        return list

    for product in database.getProducts():
        if database.isSellingProduct(product['id'], user['id'], inactive=True):
            product_list.append(product)

    if len(product_list) == 0:
        return list
    
    orderAdd = False
    for order in database.getOrders():
        for prod in order['product_list']:
            for farmer_prods in product_list:
                if farmer_prods['id'] == prod:
                    orderAdd = True
                    break
            if (orderAdd == True):
                list.append(order)
                break

    
    return list

def getLoggedUserOrders():
    list = []
    user = getLoggedUser()
    if user == None:
        return list
    
    for order in database.getOrders():
        if user['id'] == order['buyer']:
            list.append(order)
    
    return list


# returns address string if OK; 1 if product not found; 2 if seller/user not found
def getSelfCollectionLocation(event):
    product_id = event[0]
    product = database.getProduct(product_id)
    if (product == None):
        return 1
    seller = database.getUser(product['seller'])
    if (seller == None):
        return 2
    return seller['address']

###
#   Backend functions
###

#
#   Product
#

def removeProduct(removal_id):
    r = database.modifyData(database.Product, removal_id, 'active', False)
    if (r != None):
        return r
    r = database.modifyData(database.Product, removal_id, 'category', None)
    if (r != None):
        return r
    r = database.modifyData(database.Product, removal_id, 'quantity', None)
    if (r != None):
        return r
    r = database.modifyData(database.Product, removal_id, 'description', None)
    if (r != None):
        return r
    return r



#
#   String check functions
#   validates string, always returns 0 if OK

# 10 invalid format
def isName(string):
    if not (re.search("^[A-z ]+$", string)):
        return 10
    return 0

# 11 invalid format
def isAddress(string):
    if not (re.search("^[A-z0-9 .]+$", string)):
        return 11
    return 0

# 12 invalid format
def isDate(string):
    if not (re.search("^[0-9 \-]+$", string)):
        return 12
    return 0

# 13 invalid format
def isPhoneNumber(string):
    if not (re.search("^[0-9 \+]+$", string)):
        return 13
    try:
        x = int(string)
    except:
        return 13
    if (x > database.DB_INT_MAX or x < database.DB_INT_MIN):
        return 13
    return 0

# 14 invalid format
def isEmail(string):
    if not (re.search("[A-z0-9.]+@[A-z0-9]+([.][A-z0-9])+", string)):
        return 14
    return 0

# 150 too short, 151 too long
def isPassword(string):
    if len(string) < 5:
        return 150
    if len(string) > database.DB_STRING_SHORT_MAX:
        return 151
    return 0

# 160 empty string; 161 NaN; 162 zero-negative number; 163 too great number; 
def isQuantity(string):
    if (len(string) < 1):
        return 160
    try:
        x = int(string)
    except:
        return 161
    if (x <= 0):
        return 162
    if (x > database.DB_INT_MAX):
        return 163

    return 0

# 170 empty string; 171 NaN; 172 zero-negative number; 173 too great number;
def isPrice(string):
    if (len(string) < 1):
        return 170
    try:
        x = int(string)
    except:
        return 171
    if (x < 0):
        return 172
    if (x > database.DB_INT_MAX):
        return 173

    return 0

#
#   Current path functions
#

def setCurrentPath(url_func_name):
    globals.path.clear()
    globals.path.append(url_func_name)
    globals.path.append([])

def addPathArgument(key, value):
    curr_args = globals.path[1]
    new_arg = [key, value]
    curr_args.append(new_arg)
    globals.path[1] = curr_args

#
#   Categories
#

def removeCategory(category_element):
    database.removeData(database.Category, category_element['id'])

def getCategorySuggestions(closed=None):
    suggs = database.getCategorySuggestions()
    if (closed == None):
        return suggs
    elif (closed == True):
        closed_suggs = []
        for x in suggs:
            if x['status'] != 0:
                closed_suggs.append(x)
        return closed_suggs
    else:
        open_suggs = []
        for x in suggs:
            if x['status'] == 0:
                open_suggs.append(x)
        return open_suggs 

# looks for subcategories
def getSubCategories(category_id):
    result = []
    category_element = database.getCategory(category_id)
    for subcat in database.getCategories():
        if subcat['higher_category'] == category_element['id']:
            result.append(subcat)

    return result

# returns list of all categories under 'Vegetables' category
def getVegetables():
    veggies = []
    r = database.getCategoryByName('Vegetables')
    veggies_id = r['id']
    for cat in database.getCategories():
        if (cat['higher_category'] == veggies_id):
            veggies.append(cat)
    return veggies

# returns list of all categories under 'Fruits' category
def getFruits():
    fruits = []
    r = database.getCategoryByName('Fruits')
    fruits_id = r['id']
    for cat in database.getCategories():
        if (cat['higher_category'] == fruits_id):
            fruits.append(cat)

    return fruits

#
#   Users
#

def isUserLogged(user_id):
    for logged_id in globals.logged_users:
        if logged_id['id'] == user_id:
            return True
    return False

# returns user row element in UserSchema format
# primary searches by USER ID, if specified, EMAIL is used instead
# if both specified, searches by both and if found, returns first non NoneType value
def getUserRow(user_id=None, user_email=None):
    if (user_id == None) and (user_email == None):
        return None

    if (user_id != None) and (user_email != None):
        r = database.getUser(user_id)
        if (r != None):
            return r
        else:
            return database.getUser(user_email)
    
    if (user_id != None):
        return database.getUser(user_id)

    if (user_email != None):
        return database.getUserByEmail(user_email)

def editUserData(user_id, user_data, value):
    database.modifyData(database.User, user_id, user_data, value)

# returns None OK; or string of first error/exception
def removeUser(user_id=None):
    if user_id == None:
        getLoggedUser()
        removal_id = globals.logged_user['id']
    else:
        removal_id = user_id

    r = database.modifyData(database.User, removal_id, 'account_status', False)
    if (r != None):
        return r
    r = database.modifyData(database.User, removal_id, 'email', None)
    if (r != None):
        return r
    r = database.modifyData(database.User, removal_id, 'address', None)
    if (r != None):
        return r
    r = database.modifyData(database.User, removal_id, 'phone_number', None)
    if (r != None):
        return r
    r = database.modifyData(database.User, removal_id, 'birth_date', None)
    if (r != None):
        return r
    r = database.modifyData(database.User, removal_id, 'password', None)
    if (r != None):
        return r
    r = database.modifyData(database.User, removal_id, 'calendar', None)
    if (r != None):
        return r
    r = database.modifyData(database.User, removal_id, 'cart', None)

    selling_products = database.getProductsBySeller(removal_id, True)
    for prod in selling_products:
        r = removeProduct(prod['id'])
        if (r != None):
            return r
    return r
    
    

def editProductData(product_id, product_data, value):
    database.modifyData(database.Product, product_id, product_data, value)
    
def editCategoryData(category_id, category_data, value):
    database.modifyData(database.Order, category_id, category_data, value)

# returns: 0 OK; 1 user exists; 2 bad password format; 3 too long name; 4 invalid email format
def newUser(login, password, name, role):
    if (database.getUserByEmail(login) != None):
        return 1
    if isPassword(password) != 0:
        return 2
    if isName(name) != 0:
        if len(name) != 0:
            return 3
    if isEmail(login) != 0:
        return 4
    if len(name) > database.DB_STRING_SHORT_MAX:
        return 5
    if (len(name) < 1):
        name = "User"
    database.addUser(login, name, password, role)
    return 0

def validateUser(login, password):
    user = database.getUserByEmail(login)
    if (user != None and user['password'] == password and user['account_status']):
        return True
    return False

def getLoggedUser():
    #if (globals.logged_user == None or globals.user_logged_in == False):
    #    return database.unregistered_user
    #user_id = globals.logged_user['id']
    #new_user = database.getUser(user_id)
    #globals.logged_user = new_user
    if not '_user_id' in session:
        return database.unregistered_user
    else:
        r = database.getUser(int(session['_user_id']))
        if (r == None):
            print('User '+str(session['_user_id'])+' is in session, but not found. Logging out.')
            return database.unregistered_user
        else:
            return r

def isUserLogged():
    if not '_user_id' in session:
        return False
    else:
        r = database.getUser(int(session['_user_id']))
        if (r != None):
            return True
        else:
            return False

def getFlaskUser(user_id):
    if (len(globals.logged_users) == 0):
        loadUsers()
    for x in globals.logged_users:
        if (x.id == user_id):
            return x
    return None

def setLoggedUser(user):
    #globals.logged_user = user
    #globals.user_logged_in = True

    selectedUser = getFlaskUser(user['id'])
    selectedUser.logged = True

def logoutUser(user=None):
    if user != None:
        selectedUser = getFlaskUser(user['id'])
        selectedUser.logged = False
        g.user = None

def getUserOrders(user):
    id = user['id']
    order_list = []
    for order_row in database.getOrders():
        if (order_row['buyer'] == id):
            order_list.append(order_row)
    return order_list

def getUserCalendar(user):
    calendar_id_list = user['calendar']
    return calendar_id_list

def isUserModerator(user):
    if (user['role'] == 1):
        return True
    return False

def isUserAdmin(user):
    if (user['role'] == 0):
        return True
    return False

#
#   Orders
#

def addOrder(user_id, product_id_list, quantity_list, price=None, date=None, status=1):
    user_id = int(user_id)
    if (date == None):
        today = datetime.datetime.today()
        day = today.day
        month = today.month
        year = today.year
        date = str(year) + "-" + str(month) + "-" + str(day)

    database.addOrder(user_id, product_id_list, quantity_list, price, date, status)

#
#   Calendar (events, self collections)
#

def removeCalendarEvent(user, event):
    calendar = user['calendar']
    calendar.remove(event)
    database.modifyData(database.User, user['id'], 'calendar', calendar)

def addCalendarEvent(user, product_id):
    calendar = user['calendar']
    event = []
    prod = database.getProduct(product_id)
    date_f = prod['begin_date']
    date_t = prod['end_date']
    event.append(product_id)
    event.append(date_f)
    event.append(date_t)
    calendar.append(event)
    database.modifyData(database.User, user['id'], 'calendar', calendar)

def getCalendarEvent(calendar, index):
    return calendar[index]

#
#   Navigation bar
#

def navigationAddHiddenPage(url, text):
    navigationAddPage(url, text, True)

def navigationAddPage(url, text, hidden=False):
    h_transl = False
    if hidden == True:
        h_transl = None
    globals.nav_pages.append([url, h_transl, text])

# loads navigation bar pages
def navigationLoadPages():
    if (len(globals.nav_pages) == 0):
        navigationAddPage('home', 'Home')
        navigationAddPage('offers', 'Farmers')
        navigationAddPage('user_customer', 'Suggestions')
        navigationAddPage('user_farmer', 'My Products')
        navigationAddPage('admin_suggestions', 'Category suggestions')
        navigationAddPage('admin_categories', 'Category management')
        navigationAddPage('admin_users', 'User management')

        navigationAddHiddenPage('login', 'Login page')
        navigationAddHiddenPage('registration', 'Registration')
        navigationAddHiddenPage('user_settings', 'My profile')
        navigationAddHiddenPage('cart', 'Shopping cart')

# sets page active in navigation bar
def navigationSetPageActive(page_name):
    for x in globals.nav_pages:
        if x[1] == None:
            continue
        if x[0] == page_name:
            x[1] = True
        else:
            x[1] = False

def navigationGetPageActive():
    for x in globals.nav_pages:
        if (x[1] == True):
            return x[0]
    return None

#
#   Other
#

def printInternalError(additional_text):
    return "Internal error: Unable to remove this account. Please contact website administrator.<br><br>Error:<br>"+additional_text

def loadUsers():
    db_users = database.getUsers()
    globals.logged_users.clear()
    for u in db_users:
        if (u['account_status'] == True):
            fu = database.FlaskUser(u['id'], u['email'])
            globals.logged_users.append(fu)

def init():
    database.create_db()
