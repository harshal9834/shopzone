from .mongo_utils import get_cart_collection

def cart_count_processor(request):
    """
    Context processor to make cart_count available in all templates.
    Avoids having to pass 'cart_count' in every single view function.
    """
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_col = get_cart_collection()
            # Count distinct products in the user's cart
            # Or count total items if preferred. Here we count documents.
            cart_count = cart_col.count_documents({'user_id': request.user.id})
        except Exception:
            cart_count = 0
            
    return {'cart_count': cart_count}
