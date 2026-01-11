from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.db import connection
from store.models import Users, Orders, Books, Categories, Favorites, Orderitems


# HOMEPAGE (INDEX)
def index(request, category_id=None):
    """
    Renders the homepage.
    Filters books by category if selected and highlights user favorites.
    """
    # Get all categories for the sidebar/menu
    categories = Categories.objects.all()

    # Get books (Filter by category if ID is provided, else get all)
    if category_id:
        books = Books.objects.filter(categoryid=category_id)
    else:
        books = Books.objects.all()

    # Get user's favorite book IDs (to show filled hearts)
    favorite_ids = []

    # Check if user is logged in
    if "user_id" in request.session:
        favorite_ids = Favorites.objects.filter(
            userid=request.session["user_id"]
        ).values_list("bookid", flat=True)

    # Prepare data for the template
    context = {
        "books": books,  # List of books
        "categories": categories,  # List of categories
        "favorite_ids": favorite_ids,  # List of favorite IDs
    }

    return render(request, "index.html", context)


# REGISTER
def register_view(request):
    """Handles user registration.
    Checks for existing email and hashes the password before saving.
    """
    if request.method == "POST":
        # Get form data
        full_name = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Check if email is already taken
        if Users.objects.filter(email=email).exists():
            messages.warning(request, "This email address is already registered!")
            return redirect("register_view")

        # Create new user instance
        new_user = Users(
            fullname=full_name,
            email=email,
            passwordhash=make_password(password),  # Hash password for security
            usertype="customer",
        )

        # Save to database
        new_user.save()

        messages.success(request, "Registration successful! Please log in.")
        return redirect("login_view")

    return render(request, "register.html")


# LOGIN
def login_view(request):
    """
    Handles user login.
    Verifies credentials and sets session variables.
    """
    if request.method == "POST":
        # Get input data
        email = request.POST.get("username")
        password = request.POST.get("password")

        try:
            # Get user by email
            user = Users.objects.get(email=email)

            # Verify password
            if check_password(password, user.passwordhash):

                # Create Session
                request.session["user_id"] = user.userid
                request.session["user_name"] = user.fullname
                request.session["user_type"] = user.usertype

                messages.success(request, f"Welcome, {user.fullname}!")

                # Redirect based on user type (Seller vs Customer)
                if user.usertype in ["seller", "satıcı"]:
                    return redirect("seller_dashboard")
                else:
                    return redirect("index")

            else:
                messages.error(request, "Invalid password!")

        except Users.DoesNotExist:
            messages.error(request, "No account found with this email address.")

    return render(request, "login.html")


# SELLER DASHBOARD
def seller_dashboard(request):
    """
    Renders the main dashboard for sellers.
    Security: Checks if user is logged in.
    """
    if "user_id" not in request.session:
        return redirect("login_view")

    return render(request, "seller_dashboard.html")  # Was: satici_paneli.html


# SELLER ORDERS
def seller_orders(request):
    """
    Displays orders to the seller and allows status updates.
    Uses raw SQL and Stored Procedures for performance.
    """
    if "user_id" not in request.session:
        return redirect("login_view")

    # UPDATE ORDER STATUS
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("new_status")

        try:
            with connection.cursor() as cursor:
                # Calls SP_UpdateOrderStatus
                cursor.execute(
                    "EXEC SP_UpdateOrderStatus %s, %s", [order_id, new_status]
                )
            messages.success(request, f"Order #{order_id} updated successfully.")
        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect("seller_orders")

    # LIST ORDERS
    grouped_orders = {}

    try:
        with connection.cursor() as cursor:
            # Fetch data from View: VW_OrderDetails
            # Note: Ensure these column names match your English SQL View definition
            sql = """
                SELECT 
                    OrderID, OrderDate, CustomerName, BookName, Quantity, TotalAmount, Status 
                FROM VW_OrderDetails 
                ORDER BY OrderDate DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()

            for row in rows:
                o_id = row[0]  # Order ID

                # Grouping logic: If order not in dict, initialize it
                if o_id not in grouped_orders:
                    grouped_orders[o_id] = {
                        "order_id": o_id,
                        "date": row[1],
                        "customer": row[2],  # Customer Name
                        "status": row[6],
                        "grand_total": 0,
                        "items": [],  # List of books in this order
                    }

                # Add book details to the items list
                grouped_orders[o_id]["items"].append(
                    {"name": row[3], "quantity": row[4], "price": row[5]}
                )

                # Calculate total for this order group
                grouped_orders[o_id]["grand_total"] += row[5]

    except Exception as e:
        print(f"Error fetching orders: {e}")

    # Convert dictionary values to list for the template
    return render(
        request, "seller_orders.html", {"orders": list(grouped_orders.values())}
    )


# SELLER PRODUCTS
def seller_products(request):
    """
    Lists products and allows stock updates.
    """
    # Security Check
    if "user_id" not in request.session:
        return redirect("login_view")

    # UPDATE STOCKkk
    if request.method == "POST":
        book_id = request.POST.get("book_id")
        new_stock = request.POST.get("new_stock")

        if book_id and new_stock:
            try:
                with connection.cursor() as cursor:
                    # Calls SP_UpdateStock Defined in DB Report
                    sql = "EXEC SP_UpdateStock %s, %s"
                    cursor.execute(sql, [book_id, new_stock])

                messages.success(request, "Stock updated successfully.")
            except Exception as e:
                messages.error(request, f"Error: {e}")

        return redirect("seller_products")  # Refresh page

    # LIST ALL PRODUCTS
    products = []
    try:
        with connection.cursor() as cursor:
            # Fetch book inventory
            cursor.execute(
                "SELECT BookID, BookName, Author, Price, Stock, ImageUrl FROM Books ORDER BY BookID DESC"
            )
            rows = cursor.fetchall()

            for row in rows:
                products.append(
                    {
                        "id": row[0],
                        "name": row[1],
                        "author": row[2],
                        "price": row[3],
                        "stock": row[4],
                        "image": row[5],
                    }
                )
    except Exception as e:
        print(f"Error fetching products: {e}")

    return render(request, "seller_products.html", {"products": products})


# SELLER ADD BOOK
def seller_add_book(request):
    """
    Allows the seller to add a new book to the inventory.
    """
    # Security Check
    if "user_id" not in request.session:
        return redirect("login_view")

    # Fetch categories for the dropdown menu
    categories = Categories.objects.all()

    if request.method == "POST":
        # Get form data
        book_name = request.POST.get("book_name")
        author_name = request.POST.get("author")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        category_id = request.POST.get("category")
        image_file = request.FILES.get("image")

        # Get the category object
        selected_category = Categories.objects.get(categoryid=category_id)

        # Create and save the new book
        new_book = Books(
            bookname=book_name,
            author=author_name,
            price=price,
            stock=stock,
            categoryid=selected_category.categoryid,
            image=image_file,
            isactive=True,
        )
        new_book.save()

        messages.success(request, "Book added successfully!")
        return redirect("seller_dashboard")  # or 'seller_books'

    return render(request, "seller_add_book.html", {"categories": categories})


# VIEW 8: SELLER BOOKS
def seller_books(request):
    """
    Lists all books for the seller and handles stock updates.
    """
    #  Security Check
    if "user_id" not in request.session:
        messages.warning(request, "You must be logged in.")
        return redirect("login_view")

    # STOCK UPDATE
    if request.method == "POST":
        book_id = request.POST.get("book_id")
        new_stock = request.POST.get("new_stock")

        if book_id and new_stock:
            try:
                with connection.cursor() as cursor:
                    # Execute Stored Procedure
                    sql = "EXEC SP_UpdateStock %s, %s"
                    cursor.execute(sql, [book_id, new_stock])

                messages.success(request, "Stock updated successfully.")
            except Exception as e:
                messages.error(request, f"Error: {e}")

        return redirect("seller_books")

    # LIST BOOKS
    books = []
    try:
        with connection.cursor() as cursor:
            # Fetch book data using raw SQL
            cursor.execute(
                "SELECT BookID, BookName, Author, Price, Stock, CategoryID FROM Books ORDER BY BookID DESC"
            )
            rows = cursor.fetchall()

            for row in rows:
                books.append(
                    {
                        "id": row[0],
                        "name": row[1],
                        "author": row[2],
                        "price": row[3],
                        "stock": row[4],
                        "category_id": row[5],
                    }
                )
    except Exception as e:
        print(f"Error: {e}")

    return render(request, "seller_books.html", {"books": books})


# SEARCH
def search_view(request):
    """
    Handles the search bar functionality.
    Uses raw SQL LIKE queries to find matching books.
    """
    query = request.GET.get("q")  # Search term
    categories = Categories.objects.all()  # Keep sidebar menu consistent

    found_books = []

    if query:
        # Raw SQL for searching in Name or Author columns
        sql = """
            SELECT * FROM Books 
            WHERE BookName LIKE %s OR Author LIKE %s
        """
        params = [f"%{query}%", f"%{query}%"]

        # objects.raw() allows us to access model properties in the template
        found_books = Books.objects.raw(sql, params)

    context = {
        "books": found_books,  # 'index.html' expects 'books' key
        "categories": categories,  # Required for layout
        "search_query": query,
    }

    # Render results using the main homepage template
    return render(request, "index.html", context)


# DETAIL
def product_detail(request, book_id):
    """
    Displays detailed information about a specific book.
    Includes recommendation engine, favorite status check,
    and privacy-focused reviews fetching.
    """
    # Get the requested book
    book = get_object_or_404(Books, bookid=book_id)

    # Recommended Books.Same category, exclude current book
    recommended_books = Books.objects.filter(categoryid=book.categoryid).exclude(
        bookid=book.bookid
    )[:4]

    # Check Favorite Status
    is_favorite = False
    if "user_id" in request.session:
        is_favorite = Favorites.objects.filter(
            userid=request.session["user_id"], bookid=book_id
        ).exists()

    # Fetch Reviews
    reviews = []
    try:
        with connection.cursor() as cursor:
            # Using SQL Function FN_HideName_Details to mask user names ("y*** k***")
            sql = """
                SELECT 
                    R.Comment, 
                    R.star, 
                    dbo.FN_HideName_Details(U.FullName) 
                FROM Reviews R
                JOIN Users U ON R.UserID = U.UserID
                WHERE R.BookID = %s
                ORDER BY R.RewiewID DESC
            """
            cursor.execute(sql, [book_id])
            rows = cursor.fetchall()

            for row in rows:
                reviews.append(
                    {
                        "comment": row[0],
                        "star": row[1],
                        "user_name": row[2],  # Masked name from DB
                    }
                )
    except Exception as e:
        print(f"Error fetching reviews: {e}")

    # Context for Template
    context = {
        "book": book,
        "recommended_books": recommended_books,
        "is_favorite": is_favorite,
        "reviews": reviews,
    }

    return render(request, "product_detail.html", context)


# CART PAGE
def cart_view(request):
    """
    Renders the shopping cart page.
    Calculates subtotals and grand total from session data.
    """
    # Retrieve cart from session (defaults to empty dict)
    cart = request.session.get("cart", {})

    cart_details = []
    grand_total = 0

    # If cart is not empty, fetch book details
    if cart:
        # Get list of Book IDs from session keys
        book_ids = list(cart.keys())

        # Fetch all relevant books in one query
        db_books = Books.objects.filter(bookid__in=book_ids)

        # Calculate totals
        for book in db_books:
            # Get quantity from session cart dictionary
            quantity = cart[str(book.bookid)]
            total_price = book.price * quantity
            grand_total += total_price

            # Append to display list
            cart_details.append(
                {"book": book, "quantity": quantity, "total_price": total_price}
            )

    # Render Cart
    context = {"cart_items": cart_details, "grand_total": grand_total}
    return render(request, "cart.html", context)


# LOGOUT
def logout_view(request):
    """
    Logs the user out by clearing the session.
    """
    # Flush all session data (ID, Name, Cart, etc.)
    request.session.flush()

    messages.success(request, "Logged out successfully.")
    return redirect("index")


# ADD TO CART
def add_to_cart(request, book_id):
    """
    Adds a book to the session-based cart.
    Does not interact with DB directly, only updates session JSON.
    """
    # Get current cart
    cart = request.session.get("cart", {})

    # Session keys must be strings
    book_id_str = str(book_id)
    if book_id_str in cart:
        cart[book_id_str] += 1
    else:
        cart[book_id_str] = 1

    # Save to session
    request.session["cart"] = cart
    request.session.modified = True

    messages.success(request, "Added to cart! 🛒")

    # Return to the previous page
    referer = request.META.get("HTTP_REFERER", "index")
    # Clean up URL
    referer = referer.split("#")[0]

    return redirect(f"{referer}#book-{book_id}")


# UPDATE CART ITEM
def update_cart_item(request, book_id, action):
    """
    Increases or decreases item quantity in the cart.
    """
    cart = request.session.get("cart", {})
    book_id_str = str(book_id)

    if book_id_str in cart:
        if action == "increase":
            cart[book_id_str] += 1

        elif action == "decrease":
            if cart[book_id_str] > 1:
                cart[book_id_str] -= 1
            else:
                # Remove item if quantity drops below 1
                del cart[book_id_str]

        # Save changes
        request.session["cart"] = cart
        request.session.modified = True

    return redirect("cart_view")


# MY ORDERS /USER PROFILE
def my_orders(request):
    """
    Displays the order history for the logged-in user.

    Database Logic:
    - Uses the SQL View 'VW_OrderDetails' to join Orders, OrderItems, and Books tables efficiently.
    - Uses the SQL Function 'FN_EstimatedDelivery' to calculate arrival dates dynamically
      based on the order date.
    """
    # Authentication Check
    if "user_id" not in request.session:
        messages.warning(
            request, "Siparişlerinizi görüntülemek için giriş yapmanız gerekmektedir."
        )
        return redirect("login_view")

    user_id = request.session["user_id"]
    grouped_orders = {}

    try:
        with connection.cursor() as cursor:
            # SQL QUERY
            # We fetch detailed order info using a View and a Scalar Function
            sql = """
                SELECT 
                    OrderID,              -- 0
                    OrderDate,            -- 1
                    BookName,             -- 2
                    Quantity,             -- 3
                    UnitPrice,            -- 4
                    TotalAmount,          -- 5
                    Status,               -- 6
                    BookID,               -- 7 (Required for linking to product page)
                    dbo.FN_EstimatedDelivery(OrderDate) -- 8 (Calculated via DB Function)
                FROM VW_OrderDetails 
                WHERE CustomerID = %s
                ORDER BY OrderDate DESC
            """
            cursor.execute(sql, [user_id])
            rows = cursor.fetchall()

            for row in rows:
                o_id = row[0]

                # Grouping logic ,Create the main order header if it doesn't exist
                if o_id not in grouped_orders:
                    # Handle potential none values from function
                    estimated_date = row[8] if row[8] else row[1]

                    grouped_orders[o_id] = {
                        "order_id": o_id,
                        "date": row[1],
                        "status": row[6],
                        "grand_total": 0,  # Calculated from items below
                        "estimated_delivery": estimated_date,
                        "items": [],
                    }

                # Add book details to the items list
                grouped_orders[o_id]["items"].append(
                    {
                        "book_name": row[2],
                        "quantity": row[3],
                        "price": row[4],
                        "book_id": row[7],  # Used for anchor tags in HTML
                    }
                )

                # Aggregate total
                grouped_orders[o_id]["grand_total"] += row[5]

    except Exception as e:
        print(f"Error fetching order history: {e}")
        messages.error(request, "An error occurred while loading orders.")

    return render(request, "my_orders.html", {"orders": list(grouped_orders.values())})


# TOGGLE FAVORITE ADD/REMOVE
def toggle_favorite(request, book_id):
    """
    Toggles the favorite status of a book for the logged-in user.
    If the book is already in favorites, it removes it.
    If not, it adds it.
    """
    # Security Check
    if "user_id" not in request.session:
        messages.warning(request, "You must be logged in to manage favorites.")
        return redirect("login_view")

    user_id = request.session["user_id"]

    # Check Database Logic
    favorite = Favorites.objects.filter(userid=user_id, bookid=book_id).first()

    if favorite:
        # If exists delete ,remove from favorites
        favorite.delete()
        messages.success(request, "Removed from favorites. 💔")
    else:
        # If not exists create (Add to favorites)
        new_favorite = Favorites(userid=user_id, bookid=book_id)
        new_favorite.save()
        messages.success(request, "Added to favorites! ❤️")

    # Redirect to the previous page
    referer = request.META.get("HTTP_REFERER", "index")
    referer = referer.split("#")[0]  # Clean URL
    return redirect(f"{referer}#book-{book_id}")


# MY FAVORITES PAGE


def my_favorites(request):
    """
    Displays the list of books marked as favorite by the user.
    """
    # Security Check
    if "user_id" not in request.session:
        messages.warning(request, "Please log in to view your favorites.")
        return redirect("login_view")

    user_id = request.session["user_id"]

    # Get User's Favorite Book IDs (e.g., [1, 5, 8])
    fav_book_ids = Favorites.objects.filter(userid=user_id).values_list(
        "bookid", flat=True
    )

    # Fetch Book Details from 'Books' Table
    favorite_books = Books.objects.filter(bookid__in=fav_book_ids)

    # Context for Template
    context = {
        "books": favorite_books,
        "favorite_ids": fav_book_ids,
    }

    return render(request, "my_favorites.html", context)  # Was: favorilerim.html


# REMOVE FROM CART
def remove_from_cart(request, book_id):
    """
    Completely removes a specific item from the session cart.
    """
    cart = request.session.get("cart", {})
    book_id_str = str(book_id)

    # Check if item exists in cart
    if book_id_str in cart:
        del cart[book_id_str]

        # Save changes to session
        request.session["cart"] = cart
        request.session.modified = True

        messages.success(request, "Item removed from cart 🗑️")

    return redirect("cart_view")  # Redirect back to cart page


#  CHECKOUT (WITH STORED PROCEDURES)
def checkout_view(request):
    """
    Finalizes the order using Database Tables and Stored Procedures.

    Logic:
    1. Transfers Session Cart data into SQL Tables ('Carts' & 'CartItems').
    2. Calls 'SP_CalculateCartTotal' to handle taxes/discounts in DB.
    3. Calls 'SP_CreateOrder' to move items from Cart to Orders table.
    """
    # Login Check
    if "user_id" not in request.session:
        messages.warning(request, "Please log in to complete your order.")
        return redirect("login_view")

    # Preparation
    cart = request.session.get("cart", {})
    user_id = request.session.get("user_id")
    # In a real scenario, you would fetch this from a UserAddresses table
    address = "Default Delivery Address"

    # Check if cart is empty
    if not cart:
        messages.warning(request, "Your cart is empty! Please add books first.")
        return redirect("index")

    try:
        with connection.cursor() as cursor:
            # Check if user already has a temporary cart container in DB
            cursor.execute("SELECT CartID FROM Carts WHERE UserID = %s", [user_id])
            row = cursor.fetchone()

            if row:
                cart_id = row[0]
            else:
                # Create a new Cart container
                cursor.execute("INSERT INTO Carts (UserID) VALUES (%s)", [user_id])
                # Get the ID of the newly created cart
                cursor.execute("SELECT SCOPE_IDENTITY()")
                cart_id = cursor.fetchone()[0]

            # First, clear old items for this cart to prevent duplication
            cursor.execute("DELETE FROM CartItems WHERE CartID = %s", [cart_id])

            sql_insert = (
                "INSERT INTO CartItems (CartID, BookID, Quantity) VALUES (%s, %s, %s)"
            )
            # Loop through session cart and insert into SQL
            for b_id, quantity in cart.items():
                cursor.execute(sql_insert, [cart_id, b_id, quantity])

            # Calculate Total Amount (Logic handles taxes/discounts inside SQL)
            sql_calc = """
                DECLARE @OutTotal DECIMAL(10, 2);
                EXEC SP_CalculateCartTotal %s, @OutTotal OUTPUT;
                SELECT @OutTotal;
            """
            cursor.execute(sql_calc, [user_id])
            total_amount = cursor.fetchone()[0]

            # Create The Actual Order
            # Takes data from CartItems and moves it to OrderItems via SQL logic
            sql_order = """
                DECLARE @OutOrderID INT;
                EXEC SP_CreateOrder %s, %s, %s, @OutOrderID OUTPUT;
                SELECT @OutOrderID;
            """
            cursor.execute(sql_order, [user_id, address, total_amount])
            new_order_id = cursor.fetchone()[0]

        del request.session["cart"]
        request.session.modified = True

        messages.success(
            request, f"Order placed successfully! Order No: {new_order_id} 🎉"
        )
        return redirect("index")

    except Exception as e:
        print(f"CHECKOUT ERROR: {e}")
        messages.error(request, "An error occurred while creating the order.")
        return redirect("cart_view")


#  NOTIFICATIONS
def notifications_view(request):
    """
    Fetches system notifications from the 'AdminNotifications' table.
    """
    notification_list = []
    try:
        with connection.cursor() as cursor:
            # Fetch messages ordered by date (Newest first)
            cursor.execute(
                "SELECT Message, CreatedAt FROM AdminNotifications ORDER BY CreatedAt DESC"
            )
            rows = cursor.fetchall()

            for row in rows:
                notification_list.append({"message": row[0], "date": row[1]})

    except Exception as e:
        print(f"Notification Error: {e}")

    return render(request, "notifications.html", {"notifications": notification_list})


# ADD REVIEW
def add_review(request):
    """
    Handles submitting a new review.
    Uses 'SP_AddReview' to ensure the user has actually purchased/received the book.
    """
    if request.method == "POST":
        # Login Check
        if "user_id" not in request.session:
            messages.warning(request, "You must be logged in to post a review.")
            return redirect("login_view")

        # Get Data from Form
        user_id = request.session["user_id"]
        book_id = request.POST.get("book_id")
        comment_text = request.POST.get("comment_text")  # Was: yorum_metni
        rating = request.POST.get("rating")  # Was: yildiz
        order_id = request.POST.get("order_id")  # Hidden input in HTML

        # Determine where to redirect after processing
        next_url = request.POST.get("next_url", "my_orders")

        try:
            with connection.cursor() as cursor:
                # Call Stored Procedure
                # Logic: Returns 1 if successful, 0 if order not delivered yet.
                sql = """
                    DECLARE @Result INT;
                    EXEC @Result = SP_AddReview %s, %s, %s, %s, %s;
                    SELECT @Result;
                """
                params = [order_id, user_id, book_id, rating, comment_text]

                cursor.execute(sql, params)
                row = cursor.fetchone()

                if row and row[0] == 1:
                    messages.success(
                        request, "Review and rating saved successfully! 🌟"
                    )
                else:
                    messages.warning(
                        request, "You can only review items that have been delivered."
                    )

        except Exception as e:
            print(f"REVIEW SP ERROR: {e}")
            messages.error(request, "Technical error while saving review.")

        # Redirect logic
        if next_url == "my_orders":
            return redirect("my_orders")
        else:
            # Redirect back to the book detail page
            return redirect(f"/book/{book_id}")  # Ensure URL pattern matches

    return redirect("index")
