from django.db import models

"""This file defines the mapping between Python objects and the MSSQL Database tables.
Note: 'managed = False' is used because the database schema is managed externally 
via SQL Scripts, not by Django migrations.
"""


# 1. ADMIN NOTIFICATIONS
# Stores system alerts and notifications intended for administrators.
# Used to track critical system events or user activities.
class AdminNotifications(models.Model):
    notificationid = models.AutoField(db_column="NotificationID", primary_key=True)
    message = models.CharField(
        db_column="Message",
        max_length=255,
        blank=True,
        null=True,
        db_collation="Turkish_CI_AS",
    )
    createdat = models.DateTimeField(db_column="CreatedAt", blank=True, null=True)
    isread = models.BooleanField(db_column="IsRead", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "AdminNotifications"


# 2. CATEGORIES
# Lookup table for Book Categories
class Categories(models.Model):
    categoryid = models.AutoField(db_column="CategoryID", primary_key=True)
    categoryname = models.CharField(
        db_column="CategoryName", max_length=100, db_collation="Turkish_CI_AS"
    )

    def __str__(self):
        return self.categoryname

    class Meta:
        managed = False
        db_table = "Categories"


# 3. BOOKS
# Represents the books in the inventory.
# Includes details such as pricing, stock levels, and author information.


class Books(models.Model):
    bookid = models.AutoField(db_column="BookID", primary_key=True)
    bookname = models.CharField(
        db_column="BookName", max_length=100, db_collation="Turkish_CI_AS"
    )
    categoryid = models.IntegerField(db_column="CategoryID")
    author = models.CharField(
        db_column="Author", max_length=100, db_collation="Turkish_CI_AS"
    )
    price = models.DecimalField(db_column="Price", max_digits=6, decimal_places=2)
    stock = models.IntegerField(db_column="Stock")
    averagerating = models.DecimalField(
        db_column="AverageRating", max_digits=3, decimal_places=2, blank=True, null=True
    )
    isactive = models.BooleanField(db_column="IsActive", default=True)
    image = models.ImageField(
        upload_to="books/", null=True, blank=True, db_column="ImageUrl"
    )

    def __str__(self):
        return self.bookname

    class Meta:
        managed = False
        db_table = "Books"


# 4. USERS
"""
    Represents registered users in the system.
    Includes custom logic for privacy protection (GDPR(KVKK) compliance).
"""


class Users(models.Model):
    userid = models.AutoField(db_column="UserID", primary_key=True)
    fullname = models.CharField(
        db_column="FullName", max_length=100, db_collation="Turkish_CI_AS"
    )
    email = models.CharField(
        db_column="Email", unique=True, max_length=150, db_collation="Turkish_CI_AS"
    )
    passwordhash = models.CharField(
        db_column="PasswordHash", max_length=200, db_collation="Turkish_CI_AS"
    )
    usertype = models.CharField(
        db_column="Usertype",
        max_length=20,
        blank=True,
        null=True,
        db_collation="Turkish_CI_AS",
    )

    class Meta:
        managed = False
        db_table = "Users"

    @property
    def get_masked_name(self):
        # Masks the user's name for privacy compliance (GDPR/KVKK).
        if not self.fullname:
            return ""

        words = self.fullname.split()
        masked_words = []

        for word in words:
            if len(word) > 1:
                # First letter + asterisks for the rest
                masked = word[0] + "*" * (len(word) - 1)
                masked_words.append(masked)
            else:
                masked_words.append(word)

        return " ".join(masked_words)


# 5. ORDERS
"""
    Represents the header information of a customer order.
    Stores the total amount, date, and current status.
    """


class Orders(models.Model):
    orderid = models.AutoField(db_column="OrderID", primary_key=True)
    customerid = models.IntegerField(db_column="CustomerID")
    statuss = models.CharField(
        db_column="Statuss", max_length=30, db_collation="Turkish_CI_AS"
    )
    orderdate = models.DateTimeField(db_column="OrderDate")
    totalamount = models.DecimalField(
        db_column="TotalAmount", max_digits=10, decimal_places=2
    )
    shippingaddress = models.CharField(
        db_column="ShippingAddress",
        max_length=255,
        blank=True,
        null=True,
        db_collation="Turkish_CI_AS",
    )

    class Meta:
        managed = False
        db_table = "Orders"


# 6. ORDER ITEMS
# Represents individual products within an order.
class OrderItems(models.Model):
    orderitemid = models.AutoField(db_column="OrderItemID", primary_key=True)
    orderid = models.IntegerField(db_column="OrderID")
    bookid = models.IntegerField(db_column="BookID")
    quantity = models.IntegerField(db_column="Quantity")
    productprice = models.DecimalField(
        db_column="ProductPrice", max_digits=6, decimal_places=2
    )

    class Meta:
        managed = False
        db_table = "OrderItems"


# 7. CARTS
# Temporarily storing the products selected by the user before the payment process.
class Carts(models.Model):
    cartid = models.AutoField(db_column="CartID", primary_key=True)
    userid = models.ForeignKey(Users, models.DO_NOTHING, db_column="UserID")
    createdat = models.DateTimeField(db_column="CreatedAt")

    class Meta:
        managed = False
        db_table = "Carts"


# 8. CART ITEMS
# Specific items inside a user's shopping cart.
class CartItems(models.Model):
    cartitemid = models.AutoField(db_column="CartItemID", primary_key=True)
    cartid = models.ForeignKey(Carts, models.DO_NOTHING, db_column="CartID")
    bookid = models.IntegerField(db_column="BookID")
    quantity = models.IntegerField(db_column="Quantity")

    class Meta:
        managed = False
        db_table = "CartItems"
        unique_together = (("cartid", "bookid"),)


# 9. FAVORITES
# It allows users to save the products they like.
class Favorites(models.Model):
    favoriteid = models.AutoField(db_column="FavoriteID", primary_key=True)
    userid = models.IntegerField(db_column="UserID")
    bookid = models.IntegerField(db_column="BookID")

    class Meta:
        managed = False
        db_table = "Favorites"


# 10. REVIEWS
# User feedback and star ratings for books.
class Reviews(models.Model):
    reviewid = models.AutoField(db_column="RewiewID", primary_key=True)
    userid = models.IntegerField(db_column="UserID")
    bookid = models.IntegerField(db_column="BookID")
    star = models.IntegerField(db_column="star")  # Check if this is lowercase in DB
    comment = models.CharField(
        db_column="Comment",
        max_length=500,
        blank=True,
        null=True,
        db_collation="Turkish_CI_AS",
    )

    class Meta:
        managed = False
        db_table = "Reviews"


# 11. ORDER STATUS HISTORY
"""Audit log for tracking changes in order status.
    Useful for seeing when an order went from 'Pending' to 'Shipped'.
"""


class OrderStatusHistory(models.Model):
    historyid = models.AutoField(db_column="HistoryID", primary_key=True)
    orderid = models.IntegerField(db_column="OrderID", blank=True, null=True)
    oldstatus = models.CharField(
        db_column="OldStatus",
        max_length=50,
        blank=True,
        null=True,
        db_collation="Turkish_CI_AS",
    )
    newstatus = models.CharField(
        db_column="NewStatus",
        max_length=50,
        blank=True,
        null=True,
        db_collation="Turkish_CI_AS",
    )
    changedate = models.DateTimeField(db_column="ChangeDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "OrderStatusHistory"
