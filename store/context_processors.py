def get_cart_count(request):
    """
    Global Context Processor:
    Bu fonksiyon, sepetteki toplam ürün sayısını hesaplar ve
    sitenin HER sayfasında (navbar, footer vb.) kullanılabilir hale getirir.
    """
    cart = request.session.get("cart", {})

    try:
        # Calculate the total number of unwanted items in the cart.
        if isinstance(cart, dict):
            count = sum(cart.values())
        # If the structure is [item1, item2] (list), the length is taken.
        else:
            count = len(cart)
    except:
        # In case of a possible error, display the number as 0.
        count = 0

    # The calculated value is sent to the HTML pages.
    # It will now appear as {{ cart_count }} in HTML pages.
    return {"cart_count": count}
