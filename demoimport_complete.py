#!/usr/bin/env python
"""
COMPLETE Demo Data Import Script for EzyGrocery
Creates sample data for ALL 28 MODELS
"""

import os
import django
import sys
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group
from ezygrocery.models import (
    # Location & Shops
    Moholla, Shop,
    # Products
    Category, MasterProduct, ShopProduct, MasterProductReview,
    # Orders
    Order, OrderItem, RefundRequest, Cart, CartItem,
    # Customers & Riders
    Customer, Rider,
    # Delivery
    DeliveryZone, DistanceSlab, SurgePolicy,
    # Rider Earnings
    RiderEarning, RiderCashDeposit,
    # Marketing
    Coupon, Promotion, HeroSlider, SpecialOffer,
    # Content
    BlogPost, FAQ, ContactMessage, SearchQuery,
    # Reports & Settings
    ShopSalesReport, StoreSettings, SitemapConfig
)

print("=" * 70)
print("COMPLETE EZYGROCERY DEMO DATA IMPORT - ALL 28 MODELS")
print("=" * 70)

# ==================== 1. USERS & GROUPS ====================
print("\n1️⃣ Creating Users & Groups...")

# Create superuser
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@ezygrocery.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print("✅ Superuser created: admin / admin123")
else:
    print("⚠️ Superuser exists")

# Create customer users
customer_user, created = User.objects.get_or_create(
    username='customer1',
    defaults={
        'email': 'customer1@example.com',
        'first_name': 'রহিম',
        'last_name': 'আহমেদ'
    }
)
if created:
    customer_user.set_password('customer123')
    customer_user.save()
    print("✅ Customer user created")

# Create rider user
rider_user, created = User.objects.get_or_create(
    username='rider1',
    defaults={
        'email': 'rider1@example.com',
        'first_name': 'করিম',
        'last_name': 'মিয়া'
    }
)
if created:
    rider_user.set_password('rider123')
    rider_user.save()
    print("✅ Rider user created")

# Create groups
shop_owners_group, _ = Group.objects.get_or_create(name='Shop Owners')
riders_group, _ = Group.objects.get_or_create(name='Riders')
customers_group, _ = Group.objects.get_or_create(name='Customers')
print("✅ Groups created")

# ==================== 2. MOHOLLAS ====================
print("\n2️⃣ Creating Mohollas...")
mohollas_data = [
    {'name': 'বাড্ডা', 'slug': 'badda', 'area_code': 'DH-BADDA-001', 'description': 'বাড্ডা ঢাকার একটি জনবহুল এলাকা', 'serial': 1},
    {'name': 'মধ্য বাড্ডা', 'slug': 'moddho-badda', 'area_code': 'DH-BADDA-002', 'description': 'মধ্য বাড্ডা এলাকা', 'serial': 2},
    {'name': 'উত্তর বাড্ডা', 'slug': 'uttor-badda', 'area_code': 'DH-BADDA-003', 'description': 'উত্তর বাড্ডা এলাকা', 'serial': 3},
]
mohollas = []
for data in mohollas_data:
    moholla, created = Moholla.objects.get_or_create(slug=data['slug'], defaults=data)
    mohollas.append(moholla)
    print(f"{'✅' if created else '⚠️'} {moholla.name}")

# ==================== 3. SHOPS ====================
print("\n3️⃣ Creating Shops...")
shops_data = [
    {
        'name': 'বাড্ডা ফ্রেশ মার্ট', 'slug': 'badda-fresh-mart', 'moholla': mohollas[0], 'owner': admin_user,
        'address': 'বাড্ডা লিংক রোড, ঢাকা-১২১২', 'phone': '01711-123456', 'email': 'badda.fresh@gmail.com',
        'description': 'বাড্ডার সবচেয়ে বিশ্বস্ত মুদি দোকান', 'is_verified': True, 'serial': 1
    },
    {
        'name': 'মধ্য বাড্ডা সুপার শপ', 'slug': 'moddho-badda-super-shop', 'moholla': mohollas[1], 'owner': admin_user,
        'address': 'মধ্য বাড্ডা, ঢাকা-১২১২', 'phone': '01811-234567', 'email': 'moddho.badda@gmail.com',
        'description': 'মধ্য বাড্ডার আধুনিক সুপার শপ', 'is_verified': True, 'serial': 2
    },
]
shops = []
for data in shops_data:
    shop, created = Shop.objects.get_or_create(slug=data['slug'], defaults=data)
    shops.append(shop)
    print(f"{'✅' if created else '⚠️'} {shop.name}")

# ==================== 4. CATEGORIES ====================
print("\n4️⃣ Creating Categories...")
categories_data = [
    {'name': 'চাল ও ডাল', 'slug': 'rice-dal', 'serial': 1},
    {'name': 'তেল ও মসলা', 'slug': 'oil-spices', 'serial': 2},
    {'name': 'বিস্কুট ও স্ন্যাকস', 'slug': 'biscuits-snacks', 'serial': 3},
    {'name': 'পানীয়', 'slug': 'beverages', 'serial': 4},
]
categories = []
for data in categories_data:
    category, created = Category.objects.get_or_create(slug=data['slug'], defaults=data)
    categories.append(category)
    print(f"{'✅' if created else '⚠️'} {category.name}")

# ==================== 5. MASTER PRODUCTS ====================
print("\n5️⃣ Creating Master Products...")
products_data = [
    {'name': 'মিনিকেট চাল', 'sku': 'RICE-001', 'category': categories[0], 'brand': 'বাংলাদেশ', 'weight': '1kg', 'mrp': Decimal('65.00'), 
     'description': 'উন্নত মানের মিনিকেট চাল', 'product_image_url': 'https://via.placeholder.com/400x400.png?text=Rice'},
    {'name': 'তীর সয়াবিন তেল', 'sku': 'OIL-001', 'category': categories[1], 'brand': 'তীর', 'weight': '1L', 'mrp': Decimal('165.00'),
     'description': 'বিশুদ্ধ সয়াবিন তেল', 'product_image_url': 'https://via.placeholder.com/400x400.png?text=Oil'},
    {'name': 'লেক্সাস বিস্কুট', 'sku': 'BISCUIT-001', 'category': categories[2], 'brand': 'অলিম্পিক', 'weight': '300g', 'mrp': Decimal('30.00'),
     'description': 'সুস্বাদু বিস্কুট', 'product_image_url': 'https://via.placeholder.com/400x400.png?text=Biscuit'},
    {'name': 'কোকা-কোলা', 'sku': 'DRINK-001', 'category': categories[3], 'brand': 'Coca-Cola', 'weight': '500ml', 'mrp': Decimal('35.00'),
     'description': 'কোমল পানীয়', 'product_image_url': 'https://via.placeholder.com/400x400.png?text=Coke'},
]
master_products = []
for data in products_data:
    product, created = MasterProduct.objects.get_or_create(
        sku=data['sku'],
        defaults={
            'name': data['name'],
            'slug': data['sku'].lower().replace('-', '_'),
            'category': data['category'],
            'brand': data['brand'],
            'weight': data['weight'],
            'mrp': data['mrp'],
            'description': data['description'],
            'short_description': data['description'],
            'product_image_url': data['product_image_url'],
        }
    )
    master_products.append(product)
    print(f"{'✅' if created else '⚠️'} {product.name}")

# ==================== 6. SHOP PRODUCTS ====================
print("\n6️⃣ Creating Shop Products...")
count = 0
for shop in shops:
    for product in master_products:
        shop_product, created = ShopProduct.objects.get_or_create(
            shop=shop,
            master_product=product,
            defaults={
                'cost_price': product.mrp * Decimal('0.75'),
                'selling_price': product.mrp,
                'stock': 50,
                'is_active': True,
            }
        )
        if created:
            count += 1
print(f"✅ Created {count} shop products")

# ==================== 7. CUSTOMERS ====================
print("\n7️⃣ Creating Customers...")
customer, created = Customer.objects.get_or_create(
    user=customer_user,
    defaults={
        'moholla': mohollas[0],
        'phone': '01712-345678',
        'address': 'বাড্ডা, ঢাকা',
    }
)
print(f"{'✅' if created else '⚠️'} Customer profile")

# ==================== 8. RIDERS ====================
print("\n8️⃣ Creating Riders...")
rider, created = Rider.objects.get_or_create(
    user=rider_user,
    defaults={
        'nid': '1234567890123',
        'driving_license': 'DL-123456',
        'bike_registration': 'DHAKA-GA-1234',
        'phone': '01713-456789',
        'police_verification': True,
        'is_active': True,
        'rating': Decimal('4.8'),
        'total_deliveries': 150,
        'on_time_rate': Decimal('95.5'),
    }
)
print(f"{'✅' if created else '⚠️'} Rider profile")

# ==================== 9. DELIVERY ZONES ====================
print("\n9️⃣ Creating Delivery Zones...")
zones_data = [
    {'name': 'Dhaka City', 'base_fare': Decimal('60.00')},
    {'name': 'Dhaka Suburbs', 'base_fare': Decimal('80.00')},
    {'name': 'Outside Dhaka', 'base_fare': Decimal('130.00')},
]
for data in zones_data:
    zone, created = DeliveryZone.objects.get_or_create(name=data['name'], defaults=data)
    print(f"{'✅' if created else '⚠️'} {zone.name}")

# ==================== 10. DISTANCE SLABS ====================
print("\n🔟 Creating Distance Slabs...")
slabs_data = [
    {'min_distance': Decimal('0'), 'max_distance': Decimal('5'), 'additional_charge': Decimal('0')},
    {'min_distance': Decimal('5'), 'max_distance': Decimal('10'), 'additional_charge': Decimal('20')},
    {'min_distance': Decimal('10'), 'max_distance': Decimal('20'), 'additional_charge': Decimal('40')},
]
for data in slabs_data:
    slab, created = DistanceSlab.objects.get_or_create(
        min_distance=data['min_distance'],
        max_distance=data['max_distance'],
        defaults=data
    )
    print(f"{'✅' if created else '⚠️'} {slab.min_distance}-{slab.max_distance}km")

# ==================== 11. SURGE POLICIES ====================
print("\n1️⃣1️⃣ Creating Surge Policies...")
surge_data = [
    {'surge_type': 'peak_hour', 'min_amount': Decimal('20'), 'max_amount': Decimal('50'), 'is_active': True},
    {'surge_type': 'bad_weather', 'min_amount': Decimal('30'), 'max_amount': Decimal('80'), 'is_active': True},
]
for data in surge_data:
    policy, created = SurgePolicy.objects.get_or_create(surge_type=data['surge_type'], defaults=data)
    print(f"{'✅' if created else '⚠️'} {policy.surge_type}")

# ==================== 12. CARTS ====================
print("\n1️⃣2️⃣ Creating Carts...")
cart, created = Cart.objects.get_or_create(user=customer_user)
print(f"{'✅' if created else '⚠️'} Cart for customer")

# ==================== 13. CART ITEMS ====================
print("\n1️⃣3️⃣ Creating Cart Items...")
if master_products and shops:
    shop_product = ShopProduct.objects.filter(shop=shops[0], master_product=master_products[0]).first()
    if shop_product:
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            shop_product=shop_product,
            defaults={'quantity': 2}
        )
        print(f"{'✅' if created else '⚠️'} Cart item")

# ==================== 14. ORDERS ====================
print("\n1️⃣4️⃣ Creating Orders...")
order, created = Order.objects.get_or_create(
    order_number='ORD-2024-001',
    defaults={
        'user': customer_user,
        'shop': shops[0],
        'total_amount': Decimal('500.00'),
        'status': 'delivered',
        'full_name': 'রহিম আহমেদ',
        'email': 'customer1@example.com',
        'phone': '01712-345678',
        'address': 'বাড্ডা, ঢাকা',
        'delivery_charge': Decimal('60.00'),
        'rider': rider,
    }
)
print(f"{'✅' if created else '⚠️'} Order")

# ==================== 15. ORDER ITEMS ====================
print("\n1️⃣5️⃣ Creating Order Items...")
if master_products and shops:
    shop_product = ShopProduct.objects.filter(shop=shops[0], master_product=master_products[0]).first()
    if shop_product:
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            shop_product=shop_product,
            defaults={'quantity': 2, 'price': shop_product.selling_price}
        )
        print(f"{'✅' if created else '⚠️'} Order item")

# ==================== 16. REFUND REQUESTS ====================
print("\n1️⃣6️⃣ Creating Refund Requests...")
refund, created = RefundRequest.objects.get_or_create(
    order=order,
    defaults={
        'requested_by': customer_user,
        'reason': 'damaged',
        'amount': Decimal('100.00'),
        'is_approved': False,
    }
)
print(f"{'✅' if created else '⚠️'} Refund request")

# ==================== 17. RIDER EARNINGS ====================
print("\n1️⃣7️⃣ Creating Rider Earnings...")
earning, created = RiderEarning.objects.get_or_create(
    rider=rider,
    order=order,
    defaults={
        'base_payout': Decimal('50.00'),
        'distance_bonus': Decimal('10.00'),
        'surge_bonus': Decimal('0.00'),
        'incentive': Decimal('5.00'),
        'total': Decimal('65.00'),
        'date': timezone.now().date(),
    }
)
print(f"{'✅' if created else '⚠️'} Rider earning")

# ==================== 18. RIDER CASH DEPOSITS ====================
print("\n1️⃣8️⃣ Creating Rider Cash Deposits...")
deposit, created = RiderCashDeposit.objects.get_or_create(
    rider=rider,
    date=timezone.now().date(),
    defaults={
        'total_collected': Decimal('1000.00'),
        'deposited_amount': Decimal('1000.00'),
        'discrepancy': Decimal('0.00'),
        'deposited_at': timezone.now(),
        'verified': True,
    }
)
print(f"{'✅' if created else '⚠️'} Cash deposit")

# ==================== 19. COUPONS ====================
print("\n1️⃣9️⃣ Creating Coupons...")
coupon, created = Coupon.objects.get_or_create(
    code='WELCOME10',
    defaults={
        'discount_type': 'percentage',
        'discount_value': Decimal('10.00'),
        'minimum_amount': Decimal('500.00'),
        'valid_from': timezone.now(),
        'valid_to': timezone.now() + timedelta(days=30),
        'is_active': True,
    }
)
print(f"{'✅' if created else '⚠️'} Coupon")

# ==================== 20. PROMOTIONS ====================
print("\n2️⃣0️⃣ Creating Promotions...")
promotion, created = Promotion.objects.get_or_create(
    title='বিশেষ ছাড়',
    defaults={
        'description': 'সব পণ্যে বিশেষ ছাড়',
        'start_date': timezone.now(),
        'end_date': timezone.now() + timedelta(days=7),
        'is_active': True,
        'serial': 1,
    }
)
print(f"{'✅' if created else '⚠️'} Promotion")

# ==================== 21. HERO SLIDERS ====================
print("\n2️⃣1️⃣ Creating Hero Sliders...")
slider, created = HeroSlider.objects.get_or_create(
    title='তাজা পণ্য প্রতিদিন',
    defaults={
        'subtitle': 'আপনার দোরগোড়ায়',
        'description': 'সেরা মুদি দোকান থেকে অর্ডার করুন',
        'button_text': 'এখনই কিনুন',
        'is_active': True,
        'serial': 1,
    }
)
print(f"{'✅' if created else '⚠️'} Hero slider")

# ==================== 22. SPECIAL OFFERS ====================
print("\n2️⃣2️⃣ Creating Special Offers...")
offer, created = SpecialOffer.objects.get_or_create(
    title='সপ্তাহান্তে বিশেষ ছাড়',
    defaults={
        'subtitle': 'সব পণ্যে ১৫% পর্যন্ত ছাড়',
        'discount_percentage': 15,
        'button_text': 'এখনই কিনুন',
        'is_active': True,
        'serial': 1,
    }
)
print(f"{'✅' if created else '⚠️'} Special offer")

# ==================== 23. BLOG POSTS ====================
print("\n2️⃣3️⃣ Creating Blog Posts...")
blog, created = BlogPost.objects.get_or_create(
    slug='healthy-eating-tips',
    defaults={
        'title': 'স্বাস্থ্যকর খাবারের টিপস',
        'author': admin_user,
        'excerpt': 'স্বাস্থ্যকর খাবার খাওয়ার কিছু টিপস',
        'content': 'স্বাস্থ্যকর খাবার খাওয়া খুবই গুরুত্বপূর্ণ...',
        'is_published': True,
        'published_at': timezone.now(),
    }
)
print(f"{'✅' if created else '⚠️'} Blog post")

# ==================== 24. FAQS ====================
print("\n2️⃣4️⃣ Creating FAQs...")
faq, created = FAQ.objects.get_or_create(
    question='কিভাবে অর্ডার করবো?',
    defaults={
        'answer': 'আপনার এলাকা নির্বাচন করুন, পণ্য বাছাই করুন এবং চেকআউট করুন।',
        'category': 'অর্ডার',
        'is_active': True,
        'serial': 1,
    }
)
print(f"{'✅' if created else '⚠️'} FAQ")

# ==================== 25. CONTACT MESSAGES ====================
print("\n2️⃣5️⃣ Creating Contact Messages...")
message, created = ContactMessage.objects.get_or_create(
    email='customer@example.com',
    subject='পণ্য সম্পর্কে জিজ্ঞাসা',
    defaults={
        'name': 'করিম মিয়া',
        'phone': '01712-345678',
        'message': 'আমি জানতে চাই...',
        'is_read': False,
    }
)
print(f"{'✅' if created else '⚠️'} Contact message")

# ==================== 26. SEARCH QUERIES ====================
print("\n2️⃣6️⃣ Creating Search Queries...")
search, created = SearchQuery.objects.get_or_create(
    query='চাল',
    defaults={'count': 10}
)
print(f"{'✅' if created else '⚠️'} Search query")

# ==================== 27. SHOP SALES REPORTS ====================
print("\n2️⃣7️⃣ Creating Shop Sales Reports...")
report, created = ShopSalesReport.objects.get_or_create(
    shop=shops[0],
    date=timezone.now().date(),
    defaults={
        'total_orders': 10,
        'total_sales': Decimal('5000.00'),
        'total_items_sold': 50,
    }
)
print(f"{'✅' if created else '⚠️'} Sales report")

# ==================== 28. MASTER PRODUCT REVIEWS ====================
print("\n2️⃣8️⃣ Creating Product Reviews...")
review, created = MasterProductReview.objects.get_or_create(
    master_product=master_products[0],
    user=customer_user,
    defaults={
        'shop': shops[0],
        'rating': 5,
        'title': 'খুব ভালো পণ্য',
        'comment': 'পণ্যের মান অসাধারণ',
        'is_verified_purchase': True,
        'is_approved': True,
    }
)
print(f"{'✅' if created else '⚠️'} Product review")

# ==================== 29. STORE SETTINGS ====================
print("\n2️⃣9️⃣ Creating Store Settings...")
settings, created = StoreSettings.objects.get_or_create(
    pk=1,
    defaults={
        'store_name': 'কাছের দোকান',
        'contact_email': 'info@kacherdokan.com',
        'contact_phone': '01711-123456',
        'address': 'বাড্ডা, ঢাকা-১২১২',
        'store_description': 'আপনার আশেপাশের সেরা মুদি দোকান',
        'delivery_charge_inside_dhaka': Decimal('60.00'),
        'delivery_charge_outside_dhaka': Decimal('130.00'),
    }
)
print(f"{'✅' if created else '⚠️'} Store settings")

# ==================== 30. SITEMAP CONFIG ====================
print("\n3️⃣0️⃣ Creating Sitemap Config...")
sitemap, created = SitemapConfig.objects.get_or_create(
    pk=1,
    defaults={
        'include_products': True,
        'include_categories': True,
        'include_shops': True,
        'include_mohollas': True,
        'include_blog_posts': True,
    }
)
print(f"{'✅' if created else '⚠️'} Sitemap config")

# ==================== SUMMARY ====================
print("\n" + "=" * 70)
print("✅ COMPLETE DEMO DATA IMPORT FINISHED!")
print("=" * 70)
print("\n📊 DATABASE SUMMARY:")
print(f"  1. Users: {User.objects.count()}")
print(f"  2. Groups: {Group.objects.count()}")
print(f"  3. Mohollas: {Moholla.objects.count()}")
print(f"  4. Shops: {Shop.objects.count()}")
print(f"  5. Categories: {Category.objects.count()}")
print(f"  6. Master Products: {MasterProduct.objects.count()}")
print(f"  7. Shop Products: {ShopProduct.objects.count()}")
print(f"  8. Customers: {Customer.objects.count()}")
print(f"  9. Riders: {Rider.objects.count()}")
print(f"  10. Delivery Zones: {DeliveryZone.objects.count()}")
print(f"  11. Distance Slabs: {DistanceSlab.objects.count()}")
print(f"  12. Surge Policies: {SurgePolicy.objects.count()}")
print(f"  13. Carts: {Cart.objects.count()}")
print(f"  14. Cart Items: {CartItem.objects.count()}")
print(f"  15. Orders: {Order.objects.count()}")
print(f"  16. Order Items: {OrderItem.objects.count()}")
print(f"  17. Refund Requests: {RefundRequest.objects.count()}")
print(f"  18. Rider Earnings: {RiderEarning.objects.count()}")
print(f"  19. Rider Cash Deposits: {RiderCashDeposit.objects.count()}")
print(f"  20. Coupons: {Coupon.objects.count()}")
print(f"  21. Promotions: {Promotion.objects.count()}")
print(f"  22. Hero Sliders: {HeroSlider.objects.count()}")
print(f"  23. Special Offers: {SpecialOffer.objects.count()}")
print(f"  24. Blog Posts: {BlogPost.objects.count()}")
print(f"  25. FAQs: {FAQ.objects.count()}")
print(f"  26. Contact Messages: {ContactMessage.objects.count()}")
print(f"  27. Search Queries: {SearchQuery.objects.count()}")
print(f"  28. Shop Sales Reports: {ShopSalesReport.objects.count()}")
print(f"  29. Product Reviews: {MasterProductReview.objects.count()}")
print(f"  30. Store Settings: {StoreSettings.objects.count()}")
print(f"  31. Sitemap Config: {SitemapConfig.objects.count()}")

print("\n🔐 LOGIN CREDENTIALS:")
print("  Admin: admin / admin123")
print("  Customer: customer1 / customer123")
print("  Rider: rider1 / rider123")

print("\n🌐 ACCESS:")
print("  Admin Panel: http://127.0.0.1:8000/admin/")
print("  Website: http://127.0.0.1:8000/")
print("=" * 70)
