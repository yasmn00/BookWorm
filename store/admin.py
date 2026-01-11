from django.contrib import admin
from django.db import connection
from django.contrib import messages
from .models import (
    Books,
    Categories,
    Users,
    Orders,
    OrderItems,
    Carts,
    CartItems,
    Reviews,
    Favorites,
    AdminNotifications,
    OrderStatusHistory,
)


# 1. USERS (With Privacy Protection)
# It integrates a special SQL scalar function (FN_HideName_Details) to hide user data (GDPR/Privacy protection).
class UsersAdmin(admin.ModelAdmin):
    list_display = ("userid", "get_masked_name_sql", "email", "usertype")
    search_fields = ("email",)
    list_filter = ("usertype",)

    # Overriding the default queryset to inject a raw SQL function.
    # This adds a 'masked_name' field to the query results dynamically.
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Calling the Database Function 'dbo.FN_HideName_Details'
        return qs.extra(select={"masked_name": "dbo.FN_HideName_Details(FullName)"})

    def get_masked_name_sql(self, obj):
        return obj.masked_name

    get_masked_name_sql.short_description = "Full Name (Privacy Protected)"  # Returns the dynamic field created by the extra() method above


# 2. ORDERS
class OrdersAdmin(admin.ModelAdmin):
    list_display = (
        "orderid",
        "get_customer_sql",
        "totalamount",
        "statuss",
        "orderdate",
    )
    list_filter = ("statuss", "orderdate")
    search_fields = ("orderid",)

    # The administrator can directly view critical order details but cannot edit them.
    # Status updates are managed by the vendors.
    readonly_fields = ("customerid", "orderdate", "totalamount", "statuss")

    # Disables the 'Add Order' button in Admin Panel.
    # Orders must be created via the Storefront
    def has_add_permission(self, request):
        return False

    def get_customer_sql(self, obj):
        if not obj.customerid:
            return "-"

        with connection.cursor() as cursor:
            # Fetch masked name using SQL Function
            sql = (
                "SELECT dbo.FN_HideName_Details(FullName) FROM Users WHERE UserID = %s"
            )
            cursor.execute(sql, [obj.customerid])
            row = cursor.fetchone()

        if row:
            return row[0]
        else:
            return "Unknown"

    get_customer_sql.short_description = "Customer (Privacy Protected)"


# 3. BOOKS (Linked with Stored Procedure 'SP_RemoveBook')
class BooksAdmin(admin.ModelAdmin):
    list_display = ("bookname", "author", "price", "stock", "categoryid")
    search_fields = ("bookname", "author")
    list_filter = ("categoryid",)

    # Single delete action
    def delete_model(self, request, obj):
        """Overrides the 'Delete' button behavior for a single object.
        Executes 'EXEC SP_RemoveBook' instead of Django's default delete.
        """
        try:
            with connection.cursor() as cursor:
                # Database call: Executing Stored Procedure
                sql = "EXEC SP_RemoveBook %s"
                cursor.execute(sql, [obj.bookid])

            messages.success(
                request,
                f"Book '{obj.bookname}' was deleted using SQL Stored Procedure.",
            )

        except Exception as e:
            # Handle SQL errors
            messages.error(
                request,
                f"DELETE ERROR: This book cannot be deleted because it exists in order history!",
            )

    # Bulk delete action
    def delete_queryset(self, request, queryset):
        deleted_count = 0
        error_occurred = False

        for book in queryset:
            try:
                with connection.cursor() as cursor:
                    sql = "EXEC SP_RemoveBook %s"
                    cursor.execute(sql, [book.bookid])
                    deleted_count += 1
            except (
                Exception
            ):  # Flag error if any book fails to delete (Foreign Key Constraint)
                error_occurred = True

        if deleted_count > 0:
            messages.success(
                request,
                f"{deleted_count} books deleted successfully using Stored Procedure.",
            )

        if error_occurred:
            messages.warning(
                request,
                "Some books could not be deleted due to existing order records.",
            )


# REGISTRATION
admin.site.register(Users, UsersAdmin)
admin.site.register(Books, BooksAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(Categories)
admin.site.register(OrderItems)
admin.site.register(Carts)
admin.site.register(CartItems)
admin.site.register(Reviews)
admin.site.register(Favorites)
admin.site.register(AdminNotifications)
admin.site.register(OrderStatusHistory)
