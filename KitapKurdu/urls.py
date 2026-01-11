from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from store import views

urlpatterns = [
    # --- 1. GENERAL PAGES (Main navigation and search) ---
    # Admin panel entry point
    path("admin/", admin.site.urls),
    # Homepage: Lists all books
    path("", views.index, name="index"),
    # Filter books by category ID
    path("category/<int:category_id>/", views.index, name="index_category"),
    # Search functionality for books and authors
    path("search/", views.search_view, name="search_view"),
    # --- 2. AUTHENTICATION (User management) ---
    path("login/", views.login_view, name="login_view"),
    path("register/", views.register_view, name="register_view"),
    path("logout/", views.logout_view, name="logout_view"),
    # --- 3. BOOK & CART OPERATIONS (Shopping flow) ---
    # Product detail page: Shows specific book info based on book_id
    path("book/<int:book_id>/", views.product_detail, name="product_detail"),
    # Add item to cart session
    path("add-to-cart/<int:book_id>/", views.add_to_cart, name="add_to_cart"),
    # Cart page: Displays selected items
    path("cart/", views.cart_view, name="cart_view"),
    # Remove a specific item from the cart
    path(
        "remove-from-cart/<int:book_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    # Update item quantity (increase/decrease) in the cart
    path(
        "update-cart-item/<int:book_id>/<str:action>/",
        views.update_cart_item,
        name="update_cart_item",
    ),
    # --- 4. ORDER & NOTIFICATIONS (Checkout process) ---
    # Checkout page: Finalize order and payment
    path("checkout/", views.checkout_view, name="checkout_view"),
    # User's past orders history
    path("my-orders/", views.my_orders, name="my_orders"),
    # User notifications center
    path("notifications/", views.notifications_view, name="notifications_view"),
    # --- 5. FAVORITES (Wishlist functionality) ---
    # Add/Remove book from favorites list
    path(
        "toggle-favorite/<int:book_id>/", views.toggle_favorite, name="toggle_favorite"
    ),
    # Page displaying user's favorite books
    path("my-favorites/", views.my_favorites, name="my_favorites"),
    # --- 6. SELLER DASHBOARD (Vendor management) ---
    # Main dashboard for sellers
    path("seller-dashboard/", views.seller_dashboard, name="seller_dashboard"),
    # List of orders received by the seller
    path("seller-orders/", views.seller_orders, name="seller_orders"),
    # Form to add a new book to inventory
    path("seller-add-book/", views.seller_add_book, name="seller_add_book"),
    # List of products currently being sold by the seller
    path("seller-products/", views.seller_products, name="seller_products"),
    # Alternative path for seller's book management
    path("seller-books/", views.seller_books, name="seller_books"),
    # --- 7. REVIEWS (User feedback) ---
    # Submission endpoint for book reviews
    path("add-review/", views.add_review, name="add_review"),
]

# Configuration to serve media files (Images) during development mode (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
