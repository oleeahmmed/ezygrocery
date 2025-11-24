"""
Context processors for ezygrocery app
"""
from .models import StoreSettings, Category, Promotion, SpecialOffer, Coupon, SearchQuery, Order


def store_settings(request):
    """Add store settings to context"""
    try:
        settings = StoreSettings.get_settings()
        return {
            'store_settings': settings,
            'STORE_NAME': settings.store_name,
            'STORE_LOGO': settings.logo,
            'STORE_PHONE': settings.contact_phone,
            'STORE_EMAIL': settings.contact_email,
        }
    except Exception as e:
        print(f"[SEO Context] Error: {e}")
        return {
            'store_settings': None,
            'STORE_NAME': 'আমার ফ্রেশ বিডি',
            'STORE_LOGO': None,
            'STORE_PHONE': '',
            'STORE_EMAIL': '',
        }


def cart_items(request):
    """Add cart items count to context"""
    try:
        if request.user.is_authenticated:
            from .models import Cart
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                return {'cart_items_count': cart.total_items}
        return {'cart_items_count': 0}
    except:
        return {'cart_items_count': 0}


def categories_processor(request):
    """Add active categories to context"""
    try:
        categories = Category.objects.filter(is_active=True)[:10]
        return {'categories': categories}
    except:
        return {'categories': []}


def trending_searches(request):
    """Add trending searches to context"""
    try:
        searches = SearchQuery.objects.all()[:5]
        return {'trending_searches': searches}
    except:
        return {'trending_searches': []}


def promotions_processor(request):
    """Add active promotions to context"""
    try:
        from django.utils import timezone
        now = timezone.now()
        promotions = Promotion.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )[:5]
        return {'promotions': promotions}
    except:
        return {'promotions': []}


def special_offers_processor(request):
    """Add active special offers to context"""
    try:
        offers = SpecialOffer.objects.filter(is_active=True)[:3]
        return {'special_offers': offers}
    except:
        return {'special_offers': []}


def coupons_processor(request):
    """Add active coupons to context"""
    try:
        from django.utils import timezone
        now = timezone.now()
        coupons = Coupon.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now
        )[:5]
        return {'active_coupons': coupons}
    except:
        return {'active_coupons': []}


def get_new_orders_badge(request):
    """Add new orders count for admin"""
    try:
        if request.user.is_authenticated and request.user.is_staff:
            count = Order.get_new_orders_count(request)
            return {'new_orders_count': count}
        return {'new_orders_count': None}
    except:
        return {'new_orders_count': None}
