from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
from decimal import Decimal


# ==================== BASE MODELS ====================

class TimeStampedModel(models.Model):
    """Abstract base model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="তৈরির সময়")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="আপডেটের সময়")
    
    class Meta:
        abstract = True


class SEOModel(TimeStampedModel):
    """Abstract base model for SEO fields with timestamps"""
    # Meta Tags
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO title (max 60 characters)")
    meta_description = models.TextField(max_length=160, blank=True, help_text="SEO description (max 160 characters)")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="SEO keywords (comma separated)")
    
    # Open Graph Tags
    og_title = models.CharField(max_length=60, blank=True, help_text="Open Graph title")
    og_description = models.TextField(max_length=160, blank=True, help_text="Open Graph description")
    og_image = models.ImageField(upload_to='seo/', null=True, blank=True, help_text="Open Graph image (1200x630px)")
    og_type = models.CharField(max_length=50, default='website', blank=True, help_text="Open Graph type")
    
    # Twitter Card Tags
    twitter_card = models.CharField(max_length=50, default='summary_large_image', blank=True)
    twitter_title = models.CharField(max_length=60, blank=True)
    twitter_description = models.TextField(max_length=160, blank=True)
    twitter_image = models.ImageField(upload_to='seo/twitter/', null=True, blank=True)
    
    # Canonical URL
    canonical_url = models.URLField(blank=True, help_text="Canonical URL for this page")
    
    # Robots Meta
    robots_index = models.BooleanField(default=True, help_text="Allow search engines to index")
    robots_follow = models.BooleanField(default=True, help_text="Allow search engines to follow links")
    
    class Meta:
        abstract = True


# ==================== মহল্লা এবং দোকান ====================

class Moholla(SEOModel):
    """মহল্লা/এলাকা with SEO"""
    name = models.CharField(max_length=200, verbose_name="মহল্লার নাম")
    slug = models.SlugField(unique=True, verbose_name="স্লাগ")
    area_code = models.CharField(max_length=50, unique=True, verbose_name="এরিয়া কোড")
    description = models.TextField(blank=True, verbose_name="বিবরণ")
    image = models.ImageField(upload_to='mohollas/', blank=True, null=True, verbose_name="ছবি")
    is_active = models.BooleanField(default=True, verbose_name="সক্রিয়")
    serial = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        verbose_name = "মহল্লা"
        verbose_name_plural = "মহল্লা সমূহ"
        ordering = ['serial', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f"/area/{self.slug}/"
    
    def get_meta_title(self):
        return self.meta_title or f"{self.name} - স্থানীয় দোকান | আমার ফ্রেশ বিডি"
    
    def get_meta_description(self):
        return self.meta_description or f"{self.name} এলাকার সেরা দোকান থেকে কিনুন। তাজা পণ্য, দ্রুত ডেলিভারি।"


class Shop(SEOModel):
    """দোকান with full SEO"""
    name = models.CharField(max_length=200, verbose_name="দোকানের নাম")
    slug = models.SlugField(unique=True, verbose_name="স্লাগ")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops', verbose_name="মালিক")
    moholla = models.ForeignKey(Moholla, on_delete=models.CASCADE, related_name='shops', verbose_name="মহল্লা")
    address = models.TextField(verbose_name="ঠিকানা")
    phone = models.CharField(max_length=15, verbose_name="ফোন নম্বর")
    email = models.EmailField(blank=True, verbose_name="ইমেইল")
    logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True, verbose_name="লোগো")
    banner = models.ImageField(upload_to='shop_banners/', blank=True, null=True, verbose_name="ব্যানার")
    description = models.TextField(blank=True, verbose_name="দোকানের বিবরণ")
    business_type = models.CharField(max_length=100, blank=True, help_text="e.g., Grocery Store")
    opening_hours = models.TextField(blank=True, help_text="e.g., Mon-Sat: 9AM-9PM")
    price_range = models.CharField(max_length=50, blank=True, help_text="e.g., $, $$")
    is_active = models.BooleanField(default=True, verbose_name="সক্রিয়")
    is_verified = models.BooleanField(default=False, verbose_name="যাচাইকৃত")
    serial = models.PositiveIntegerField(default=0, verbose_name="সিরিয়াল")
    total_cancellations = models.PositiveIntegerField(default=0)
    suspended_until = models.DateTimeField(null=True, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    last_penalty_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "দোকান"
        verbose_name_plural = "দোকান সমূহ"
        ordering = ['serial', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.moholla.name}"
    
    def get_absolute_url(self):
        return f"/shop/{self.slug}/"
    
    def get_meta_title(self):
        return self.meta_title or f"{self.name} - {self.moholla.name} | আমার ফ্রেশ বিডি"
    
    def get_meta_description(self):
        desc = f"{self.name} থেকে কিনুন {self.moholla.name} এ।"
        if self.description:
            desc += f" {self.description[:100]}"
        return self.meta_description or desc
    
    def get_og_image_url(self):
        if self.og_image:
            return self.og_image.url
        elif self.banner:
            return self.banner.url
        elif self.logo:
            return self.logo.url
        return None
    
    def total_sales(self):
        from django.db.models import Sum
        total = self.orders.filter(status='delivered').aggregate(total=Sum('total_amount'))['total']
        return total or 0
    
    def total_orders(self):
        return self.orders.count()
    
    def total_products(self):
        return self.shop_products.filter(is_active=True).count()


# ==================== ক্যাটাগরি ====================

class Category(SEOModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    description = models.TextField(blank=True, help_text="Category description for SEO")
    serial = models.PositiveIntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['serial', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f"/category/{self.slug}/"
    
    def get_meta_title(self):
        return self.meta_title or f"{self.name} - আমার ফ্রেশ বিডি"
    
    def get_meta_description(self):
        return self.meta_description or f"{self.name} ক্যাটাগরির সেরা পণ্য কিনুন।"
    
    def get_og_image_url(self):
        if self.og_image:
            return self.og_image.url
        elif self.image:
            return self.image.url
        return None


# ==================== মূল পণ্য সিস্টেম ====================

class MasterProduct(SEOModel):
    """মূল পণ্য - সিস্টেমে একবার তৈরি হবে"""
    name = models.CharField(max_length=200, verbose_name="পণ্যের নাম")
    slug = models.SlugField(unique=True, verbose_name="স্লাগ")
    sku = models.CharField(max_length=100, unique=True, verbose_name="SKU")
    barcode = models.CharField(max_length=100, blank=True, verbose_name="বারকোড")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='master_products', verbose_name="ক্যাটাগরি")
    description = models.TextField(verbose_name="বিবরণ")
    short_description = models.CharField(max_length=255, blank=True, verbose_name="সংক্ষিপ্ত বিবরণ")
    features = models.TextField(blank=True, verbose_name="বৈশিষ্ট্য")
    image = models.ImageField(upload_to='master_products/', blank=True, null=True, verbose_name="মূল ছবি")
    image_2 = models.ImageField(upload_to='master_products/', blank=True, null=True, verbose_name="ছবি ২")
    image_3 = models.ImageField(upload_to='master_products/', blank=True, null=True, verbose_name="ছবি ৩")
    product_image_url = models.URLField(blank=True, verbose_name="পণ্যের ছবি URL", help_text="If no image uploaded, use this URL")
    brand = models.CharField(max_length=100, blank=True, verbose_name="ব্র্যান্ড")
    model_number = models.CharField(max_length=100, blank=True, verbose_name="মডেল নম্বর")
    weight = models.CharField(max_length=50, blank=True, verbose_name="ওজন")
    dimensions = models.CharField(max_length=100, blank=True, verbose_name="মাপ")
    gtin = models.CharField(max_length=50, blank=True, verbose_name="GTIN")
    mpn = models.CharField(max_length=100, blank=True, verbose_name="MPN")
    mrp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="MRP")
    is_active = models.BooleanField(default=True, verbose_name="সক্রিয়")
    
    class Meta:
        verbose_name = "মূল পণ্য"
        verbose_name_plural = "মূল পণ্য সমূহ"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def get_absolute_url(self):
        return f"/product/{self.slug}/"
    
    def total_shops_selling(self):
        return self.shop_products.filter(is_active=True).count()
    
    def lowest_price(self):
        from django.db.models import Min
        result = self.shop_products.filter(is_active=True).aggregate(
            min_price=Min('selling_price')
        )
        return result['min_price']
    
    def highest_price(self):
        from django.db.models import Max
        result = self.shop_products.filter(is_active=True).aggregate(
            max_price=Max('selling_price')
        )
        return result['max_price']
    
    def average_rating(self):
        from django.db.models import Avg
        result = self.master_reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg('rating')
        )
        return result['avg_rating'] or 0
    
    def total_reviews(self):
        return self.master_reviews.filter(is_approved=True).count()


class ShopProduct(TimeStampedModel):
    """দোকানের পণ্য"""
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop_products', verbose_name="দোকান")
    master_product = models.ForeignKey(MasterProduct, on_delete=models.CASCADE, related_name='shop_products', verbose_name="মূল পণ্য")
    shop_sku = models.CharField(max_length=100, blank=True, verbose_name="দোকানের SKU")
    product_image_url = models.URLField(blank=True, verbose_name="পণ্যের ছবি URL", help_text="Override product image with this URL")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ক্রয় মূল্য")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="বিক্রয় মূল্য")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="ছাড়ের মূল্য")
    stock = models.PositiveIntegerField(default=0, verbose_name="স্টক")
    low_stock_alert = models.PositiveIntegerField(default=10, verbose_name="কম স্টক সতর্কতা")
    location_in_shop = models.CharField(max_length=100, blank=True, verbose_name="দোকানে অবস্থান")
    notes = models.TextField(blank=True, verbose_name="নোট")
    is_active = models.BooleanField(default=True, verbose_name="সক্রিয়")
    is_featured = models.BooleanField(default=False, verbose_name="ফিচারড")
    
    class Meta:
        verbose_name = "দোকানের পণ্য"
        verbose_name_plural = "দোকানের পণ্য সমূহ"
        ordering = ['-created_at']
        unique_together = ['shop', 'master_product']
        indexes = [
            models.Index(fields=['shop', 'is_active']),
            models.Index(fields=['master_product', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.master_product.name} - {self.shop.name}"
    
    @property
    def is_on_sale(self):
        return self.discount_price is not None and self.discount_price < self.selling_price
    
    @property
    def final_price(self):
        return self.discount_price if self.is_on_sale else self.selling_price
    
    @property
    def discount_percentage(self):
        if self.discount_price and self.selling_price > 0:
            return ((self.selling_price - self.discount_price) / self.selling_price) * 100
        return 0
    
    @property
    def profit_margin(self):
        return self.final_price - self.cost_price
    
    @property
    def profit_percentage(self):
        if self.cost_price > 0:
            return ((self.final_price - self.cost_price) / self.cost_price) * 100
        return 0
    
    @property
    def is_low_stock(self):
        return self.stock <= self.low_stock_alert
    
    @property
    def is_out_of_stock(self):
        return self.stock == 0
    
    def get_absolute_url(self):
        return f"/shop/{self.shop.slug}/product/{self.master_product.slug}/"


class MasterProductReview(TimeStampedModel):
    """মূল পণ্যের রিভিউ"""
    master_product = models.ForeignKey(MasterProduct, on_delete=models.CASCADE, related_name='master_reviews', verbose_name="মূল পণ্য")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ব্যবহারকারী")
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="দোকান")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="রেটিং")
    title = models.CharField(max_length=200, verbose_name="রিভিউ শিরোনাম")
    comment = models.TextField(verbose_name="মন্তব্য")
    is_verified_purchase = models.BooleanField(default=False, verbose_name="যাচাইকৃত ক্রয়")
    is_approved = models.BooleanField(default=False, verbose_name="অনুমোদিত")
    
    class Meta:
        verbose_name = "মূল পণ্য রিভিউ"
        verbose_name_plural = "মূল পণ্য রিভিউ সমূহ"
        ordering = ['-created_at']
        unique_together = ['master_product', 'user']
    
    def __str__(self):
        return f"{self.master_product.name} - {self.rating}★ by {self.user.username}"


# ==================== কার্ট সিস্টেম ====================

class Cart(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    
    def __str__(self):
        if self.user:
            return f"Cart - {self.user.username}"
        return f"Cart - {self.session_key}"
    
    @property
    def total_price(self):
        from django.db.models import Sum, F
        total = self.items.aggregate(
            total=Sum(F('shop_product__selling_price') * F('quantity'))
        )['total']
        return total or 0
    
    @property
    def total_items(self):
        from django.db.models import Sum
        total = self.items.aggregate(total=Sum('quantity'))['total']
        return total or 0


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    shop_product = models.ForeignKey(ShopProduct, on_delete=models.CASCADE, verbose_name="দোকানের পণ্য")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    class Meta:
        unique_together = ['cart', 'shop_product']
    
    def __str__(self):
        return f"{self.quantity} x {self.shop_product.master_product.name}"
    
    @property
    def total_price(self):
        if not self.shop_product or not self.quantity:
            return 0
        return self.shop_product.final_price * self.quantity



# ==================== কাস্টমার ====================

class Customer(TimeStampedModel):
    """কাস্টমার প্রোফাইল"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    moholla = models.ForeignKey(Moholla, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="মহল্লা")
    phone = models.CharField(max_length=15, verbose_name="ফোন নম্বর")
    address = models.TextField(verbose_name="ঠিকানা")
    avatar = models.ImageField(upload_to='customers/', blank=True, null=True, verbose_name="ছবি")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="জন্মতারিখ")
    
    class Meta:
        verbose_name = "ক্রেতা"
        verbose_name_plural = "ক্রেতা সমূহ"
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    
    def total_orders(self):
        return Order.objects.filter(user=self.user).count()


# ==================== রাইডার ====================

class Rider(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rider_profile')
    nid = models.CharField(max_length=20, unique=True, verbose_name="NID")
    driving_license = models.CharField(max_length=50)
    bike_registration = models.CharField(max_length=50)
    police_verification = models.BooleanField(default=False)
    phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    total_deliveries = models.PositiveIntegerField(default=0)
    on_time_rate = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


# ==================== অর্ডার সিস্টেম ====================

class Order(TimeStampedModel):
    """অর্ডার"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    DELIVERY_LOCATION_CHOICES = [
        ('inside_dhaka', 'Inside Dhaka'),
        ('outside_dhaka', 'Outside Dhaka')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='orders', verbose_name="দোকান")
    order_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    delivery_location = models.CharField(max_length=20, choices=DELIVERY_LOCATION_CHOICES, default='inside_dhaka')
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_instructions = models.TextField(blank=True)
    rider = models.ForeignKey(Rider, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    expected_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.CharField(max_length=200, blank=True)
    is_viewed = models.BooleanField(default=False, verbose_name='Admin Viewed')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "অর্ডার"
        verbose_name_plural = "অর্ডার সমূহ"
    
    def __str__(self):
        return f"{self.order_number} - {self.shop.name}"
    
    @staticmethod
    def get_new_orders_count(request):
        count = Order.objects.filter(is_viewed=False).count()
        return count if count > 0 else None


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    shop_product = models.ForeignKey(ShopProduct, on_delete=models.CASCADE, verbose_name="দোকানের পণ্য")
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at time of order")
    
    def __str__(self):
        return f"{self.quantity} x {self.shop_product.master_product.name}"
    
    @property
    def subtotal(self):
        if self.price is not None and self.quantity is not None:
            return self.price * self.quantity
        return 0


class RefundRequest(TimeStampedModel):
    REFUND_REASON_CHOICES = [
        ('wrong_item', 'Wrong Item'),
        ('missing_item', 'Missing Item'),
        ('damaged', 'Damaged Product'),
        ('merchant_cancel', 'Merchant Cancellation'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50, choices=REFUND_REASON_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_approved = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)



# ==================== রিপোর্ট ====================

class ShopSalesReport(models.Model):
    """দোকান বিক্রয় রিপোর্ট"""
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='sales_reports', verbose_name="দোকান")
    date = models.DateField(verbose_name="তারিখ")
    total_orders = models.PositiveIntegerField(default=0, verbose_name="মোট অর্ডার")
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="মোট বিক্রয়")
    total_items_sold = models.PositiveIntegerField(default=0, verbose_name="মোট পণ্য বিক্রিত")
    
    class Meta:
        verbose_name = "বিক্রয় রিপোর্ট"
        verbose_name_plural = "বিক্রয় রিপোর্ট সমূহ"
        unique_together = ['shop', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.shop.name} - {self.date} - ৳{self.total_sales}"


# ==================== রাইডার আর্নিং ====================

class RiderCashDeposit(TimeStampedModel):
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    date = models.DateField()
    total_collected = models.DecimalField(max_digits=10, decimal_places=2)
    deposited_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discrepancy = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposited_at = models.DateTimeField()
    verified = models.BooleanField(default=False)


class RiderEarning(models.Model):
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    base_payout = models.DecimalField(max_digits=8, decimal_places=2)
    distance_bonus = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    surge_bonus = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    incentive = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()


# ==================== ডেলিভারি কনফিগারেশন ====================

class DeliveryZone(models.Model):
    name = models.CharField(max_length=50)
    base_fare = models.DecimalField(max_digits=6, decimal_places=2)


class DistanceSlab(models.Model):
    min_distance = models.DecimalField(max_digits=5, decimal_places=2)
    max_distance = models.DecimalField(max_digits=5, decimal_places=2)
    additional_charge = models.DecimalField(max_digits=6, decimal_places=2)


class SurgePolicy(models.Model):
    SURGE_TYPE_CHOICES = [
        ('peak_hour', 'Peak Hour'),
        ('bad_weather', 'Bad Weather'),
        ('event', 'Special Event'),
        ('rider_shortage', 'Rider Shortage'),
    ]
    surge_type = models.CharField(max_length=20, choices=SURGE_TYPE_CHOICES)
    min_amount = models.DecimalField(max_digits=6, decimal_places=2)
    max_amount = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)



# ==================== কুপন সিস্টেম ====================

class Coupon(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code
    
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_to:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        return True
    
    def calculate_discount(self, amount):
        if not self.is_valid() or amount < self.minimum_amount:
            return 0
        
        if self.discount_type == 'percentage':
            discount = (amount * self.discount_value) / 100
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
            return discount
        else:
            return self.discount_value


# ==================== প্রোমোশন এবং স্লাইডার ====================

class Promotion(SEOModel):
    """Promotion with SEO"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='promotions/')
    link_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    serial = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['serial', '-start_date']
    
    def __str__(self):
        return self.title
    
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date


class HeroSlider(TimeStampedModel):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='hero_sliders/')
    button_text = models.CharField(max_length=50, default='Shop Now')
    button_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    serial = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['serial']
    
    def __str__(self):
        return self.title


class SpecialOffer(TimeStampedModel):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    discount_percentage = models.PositiveIntegerField(null=True, blank=True)
    background_color = models.CharField(max_length=50, default='bg-gradient-to-r from-orange-400 to-red-500')
    button_text = models.CharField(max_length=50, default='এখনই কিনুন')
    button_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    serial = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['serial', '-created_at']
    
    def __str__(self):
        return self.title



# ==================== সার্চ ট্র্যাকিং ====================

class SearchQuery(models.Model):
    query = models.CharField(max_length=200)
    count = models.PositiveIntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-count', '-last_searched']
    
    def __str__(self):
        return f"{self.query} ({self.count})"


# ==================== যোগাযোগ ====================

class ContactMessage(TimeStampedModel):
    """Contact form submissions"""
    name = models.CharField(max_length=100, verbose_name='নাম')
    email = models.EmailField(verbose_name='ইমেইল')
    phone = models.CharField(max_length=20, blank=True, verbose_name='ফোন নম্বর')
    subject = models.CharField(max_length=200, verbose_name='বিষয়')
    message = models.TextField(verbose_name='বার্তা')
    is_read = models.BooleanField(default=False, verbose_name='পড়া হয়েছে')
    replied = models.BooleanField(default=False, verbose_name='উত্তর দেওয়া হয়েছে')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'যোগাযোগ বার্তা'
        verbose_name_plural = 'যোগাযোগ বার্তা'
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


# ==================== ব্লগ ====================

class BlogPost(SEOModel):
    """Blog posts for content marketing and SEO"""
    title = models.CharField(max_length=200, verbose_name='শিরোনাম')
    slug = models.SlugField(unique=True, verbose_name='স্লাগ')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    featured_image = models.ImageField(upload_to='blog/', verbose_name='ফিচার ইমেজ')
    excerpt = models.TextField(max_length=300, blank=True, help_text='Short summary (300 chars)')
    content = models.TextField(verbose_name='কন্টেন্ট')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_posts')
    tags = models.CharField(max_length=255, blank=True, help_text='Comma separated tags')
    is_published = models.BooleanField(default=False, verbose_name='প্রকাশিত')
    published_at = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'ব্লগ পোস্ট'
        verbose_name_plural = 'ব্লগ পোস্ট সমূহ'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/blog/{self.slug}/"
    
    def get_meta_title(self):
        return self.meta_title or f"{self.title} | আমার ফ্রেশ বিডি ব্লগ"
    
    def get_meta_description(self):
        return self.meta_description or self.excerpt or self.content[:160]
    
    def get_og_image_url(self):
        if self.og_image:
            return self.og_image.url
        elif self.featured_image:
            return self.featured_image.url
        return None



# ==================== FAQ ====================

class FAQ(TimeStampedModel):
    """Frequently Asked Questions with Schema.org support"""
    question = models.CharField(max_length=300, verbose_name='প্রশ্ন')
    answer = models.TextField(verbose_name='উত্তর')
    category = models.CharField(max_length=100, blank=True, help_text='FAQ Category')
    is_active = models.BooleanField(default=True)
    serial = models.PositiveIntegerField(default=0, help_text='Display order')
    
    class Meta:
        ordering = ['serial', '-created_at']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
    
    def __str__(self):
        return self.question
    
    @staticmethod
    def get_faq_schema():
        faqs = FAQ.objects.filter(is_active=True)
        if not faqs.exists():
            return None
        
        faq_list = []
        for faq in faqs:
            faq_list.append({
                "@type": "Question",
                "name": faq.question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq.answer
                }
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_list
        }


# ==================== Sitemap Configuration ====================

class SitemapConfig(models.Model):
    """Configuration for XML Sitemap generation"""
    include_products = models.BooleanField(default=True)
    include_categories = models.BooleanField(default=True)
    include_shops = models.BooleanField(default=True)
    include_mohollas = models.BooleanField(default=True)
    include_blog_posts = models.BooleanField(default=True)
    products_priority = models.DecimalField(max_digits=2, decimal_places=1, default=0.8, help_text='0.0 to 1.0')
    categories_priority = models.DecimalField(max_digits=2, decimal_places=1, default=0.7, help_text='0.0 to 1.0')
    shops_priority = models.DecimalField(max_digits=2, decimal_places=1, default=0.6, help_text='0.0 to 1.0')
    products_changefreq = models.CharField(max_length=20, default='daily', choices=[
        ('always', 'Always'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('never', 'Never')
    ])
    
    class Meta:
        verbose_name = 'Sitemap Configuration'
        verbose_name_plural = 'Sitemap Configuration'
    
    def __str__(self):
        return "Sitemap Settings"
    
    def save(self, *args, **kwargs):
        if not self.pk and SitemapConfig.objects.exists():
            existing = SitemapConfig.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)



# ==================== STORE SETTINGS ====================

class StoreSettings(TimeStampedModel):
    # Basic Information
    store_name = models.CharField(max_length=200, default='🌿 আমার ফ্রেশ বিডি', verbose_name='স্টোরের নাম')
    logo = models.ImageField(upload_to='store/', null=True, blank=True, verbose_name='লোগো')
    logo_dark = models.ImageField(upload_to='store/', null=True, blank=True, verbose_name='ডার্ক মোড লোগো')
    favicon = models.ImageField(upload_to='store/', null=True, blank=True, verbose_name='ফ্যাভিকন')
    contact_email = models.EmailField(default='nabihaenterprise453@gmail.com', verbose_name='যোগাযোগ ইমেইল')
    contact_phone = models.CharField(max_length=20, default='01337-343737', verbose_name='যোগাযোগ নম্বর')
    address = models.TextField(default='Bosila, Mohammadpur, Dhaka', blank=True, verbose_name='ঠিকানা')
    store_description = models.TextField(default='আমার ফ্রেশ বিডি - আপনার বিশ্বস্ত প্রিমিয়াম মানের বাদাম এবং শুকনো খাবারের উৎস।', blank=True, verbose_name='স্টোর বিবরণ')
    
    # Social Media
    facebook_url = models.URLField(blank=True, verbose_name='ফেসবুক লিংক')
    twitter_url = models.URLField(blank=True, verbose_name='টুইটার লিংক')
    instagram_url = models.URLField(blank=True, verbose_name='ইনস্টাগ্রাম লিংক')
    linkedin_url = models.URLField(blank=True, verbose_name='লিংকডইন লিংক')
    youtube_url = models.URLField(blank=True, verbose_name='ইউটিউব লিংক')
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name='হোয়াটসঅ্যাপ নম্বর')
    
    # Store Configuration
    currency = models.CharField(max_length=10, default='BDT', verbose_name='কারেন্সি')
    currency_symbol = models.CharField(max_length=5, default='৳', verbose_name='কারেন্সি সিম্বল')
    maintenance_mode = models.BooleanField(default=False, verbose_name='মেইনটেনেন্স মোড')
    delivery_charge_inside_dhaka = models.DecimalField(max_digits=10, decimal_places=2, default=60, verbose_name='ঢাকার ভিতরে ডেলিভারি চার্জ')
    delivery_charge_outside_dhaka = models.DecimalField(max_digits=10, decimal_places=2, default=130, verbose_name='ঢাকার বাইরে ডেলিভারি চার্জ')
    free_delivery_minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1000, verbose_name='ফ্রি ডেলিভারির ন্যূনতম অর্ডার')
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=200, verbose_name='ন্যূনতম অর্ডার অ্যামাউন্ট')
    
    # Store Policies
    shipping_policy = models.TextField(blank=True, verbose_name='শিপিং পলিসি')
    return_policy = models.TextField(blank=True, verbose_name='রিটার্ন পলিসি')
    privacy_policy = models.TextField(blank=True, verbose_name='প্রাইভেসি পলিসি')
    terms_conditions = models.TextField(blank=True, verbose_name='টার্মস এন্ড কন্ডিশনস')
    about_us = models.TextField(blank=True, verbose_name='আমাদের সম্পর্কে')
    refund_policy = models.TextField(blank=True, verbose_name='রিফান্ড পলিসি')
    
    # SEO Meta Tags
    meta_title = models.CharField(max_length=200, default='আমার ফ্রেশ বিডি - Premium Quality Nuts & Dry Foods', blank=True, verbose_name='মেটা টাইটেল')
    meta_description = models.TextField(default='আমার ফ্রেশ বিডি - আপনার বিশ্বস্ত প্রিমিয়াম মানের বাদাম এবং শুকনো খাবারের উৎস।', blank=True, verbose_name='মেটা ডেস্ক্রিপশন')
    meta_keywords = models.TextField(default='আমার ফ্রেশ বিডি, বাদাম, শুকনো খাবার', blank=True, verbose_name='মেটা কিওয়ার্ডস')
    
    # Open Graph Tags
    og_title = models.CharField(max_length=200, blank=True, verbose_name='ওপেন গ্রাফ টাইটেল')
    og_description = models.TextField(blank=True, verbose_name='ওপেন গ্রাফ ডেস্ক্রিপশন')
    og_image = models.ImageField(upload_to='seo/store/', null=True, blank=True, verbose_name='ওপেন গ্রাফ ইমেজ')
    og_type = models.CharField(max_length=50, default='website', blank=True, verbose_name='ওপেন গ্রাফ টাইপ')
    og_site_name = models.CharField(max_length=100, blank=True, verbose_name='ওপেন গ্রাফ সাইট নাম')
    
    # Twitter Card Tags
    twitter_card = models.CharField(max_length=50, default='summary_large_image', blank=True, verbose_name='টুইটার কার্ড টাইপ')
    twitter_title = models.CharField(max_length=200, blank=True, verbose_name='টুইটার টাইটেল')
    twitter_description = models.TextField(blank=True, verbose_name='টুইটার ডেস্ক্রিপশন')
    twitter_image = models.ImageField(upload_to='seo/twitter/', null=True, blank=True, verbose_name='টুইটার ইমেজ')
    twitter_site = models.CharField(max_length=100, blank=True, verbose_name='টুইটার সাইট')
    twitter_creator = models.CharField(max_length=100, blank=True, verbose_name='টুইটার ক্রিয়েটর')
    
    # Canonical & Robots
    canonical_url = models.URLField(blank=True, verbose_name='ক্যানোনিকাল URL')
    robots_index = models.BooleanField(default=True, verbose_name='রোবটস ইন্ডেক্স')
    robots_follow = models.BooleanField(default=True, verbose_name='রোবটস ফলো')
    robots_advanced = models.TextField(blank=True, verbose_name='এডভান্সড রোবটস ডাইরেক্টিভ')
    
    # Facebook Pixel
    facebook_pixel_id = models.CharField(max_length=50, blank=True, verbose_name='ফেসবুক পিক্সেল ID')
    facebook_pixel_enabled = models.BooleanField(default=False, verbose_name='ফেসবুক পিক্সেল সক্রিয়')
    facebook_pixel_debug = models.BooleanField(default=False, verbose_name='ফেসবুক পিক্সেল ডিবাগ মোড')
    facebook_app_id = models.CharField(max_length=100, blank=True, verbose_name='ফেসবুক অ্যাপ ID')
    facebook_page_url = models.URLField(blank=True, verbose_name='ফেসবুক পেজ URL')
    
    # Google Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True, verbose_name='গুগল অ্যানালিটিক্স ID')
    google_analytics_enabled = models.BooleanField(default=False, verbose_name='গুগল অ্যানালিটিক্স সক্রিয়')
    google_analytics_4_id = models.CharField(max_length=50, blank=True, verbose_name='গুগল অ্যানালিটিক্স 4 ID')
    
    # Google Tag Manager
    google_tag_manager_id = models.CharField(max_length=50, blank=True, verbose_name='গুগল ট্যাগ ম্যানেজার ID')
    google_tag_manager_enabled = models.BooleanField(default=False, verbose_name='গুগল ট্যাগ ম্যানেজার সক্রিয়')
    
    # Site Verification
    google_site_verification = models.CharField(max_length=100, blank=True, verbose_name='গুগল সাইট ভেরিফিকেশন')
    bing_site_verification = models.CharField(max_length=100, blank=True, verbose_name='বিং সাইট ভেরিফিকেশন')
    yandex_verification = models.CharField(max_length=100, blank=True, verbose_name='ইয়ানডেক্স ভেরিফিকেশন')
    baidu_verification = models.CharField(max_length=100, blank=True, verbose_name='বাইডু ভেরিফিকেশন')
    
    # Structured Data
    structured_data_organization = models.TextField(blank=True, verbose_name='স্ট্রাকচার্ড ডাটা (অর্গানাইজেশন)')
    structured_data_website = models.TextField(blank=True, verbose_name='স্ট্রাকচার্ড ডাটা (ওয়েবসাইট)')
    structured_data_breadcrumb = models.TextField(blank=True, verbose_name='স্ট্রাকচার্ড ডাটা (ব্রেডক্রাম্ব)')
    
    # Performance & Technical SEO
    enable_compression = models.BooleanField(default=True, verbose_name='কম্প্রেশন সক্রিয়')
    enable_caching = models.BooleanField(default=True, verbose_name='ক্যাশিং সক্রিয়')
    enable_sitemap = models.BooleanField(default=True, verbose_name='সাইটম্যাপ সক্রিয়')
    enable_robots_txt = models.BooleanField(default=True, verbose_name='রোবটস.টেক্সট সক্রিয়')
    enable_schema_markup = models.BooleanField(default=True, verbose_name='স্কিমা মার্কআপ সক্রিয়')
    
    # Social Media Meta
    social_media_title = models.CharField(max_length=200, blank=True, verbose_name='সোশ্যাল মিডিয়া টাইটেল')
    social_media_description = models.TextField(blank=True, verbose_name='সোশ্যাল মিডিয়া ডেস্ক্রিপশন')
    
    # Advanced SEO Settings
    seo_author = models.CharField(max_length=100, blank=True, verbose_name='এসইও অথর')
    seo_geo_region = models.CharField(max_length=100, default='BD-DH', verbose_name='জিও রিজিয়ন')
    seo_geo_placename = models.CharField(max_length=100, default='Dhaka', verbose_name='জিও প্লেসনেম')
    seo_geo_position = models.CharField(max_length=100, blank=True, verbose_name='জিও পজিশন')
    seo_icbm = models.CharField(max_length=100, blank=True, verbose_name='ICBM কোঅর্ডিনেট')
    
    class Meta:
        verbose_name = "Store Settings"
        verbose_name_plural = "Store Settings"
    
    def __str__(self):
        return self.store_name
    
    def save(self, *args, **kwargs):
        if not self.pk and StoreSettings.objects.exists():
            existing = StoreSettings.objects.first()
            self.pk = existing.pk
        if not self.og_site_name:
            self.og_site_name = self.store_name
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def get_meta_title(self):
        return self.meta_title or f"{self.store_name} - Premium Quality Products"
    
    def get_meta_description(self):
        return self.meta_description or self.store_description
    
    def get_og_title(self):
        return self.og_title or self.get_meta_title()
    
    def get_og_description(self):
        return self.og_description or self.get_meta_description()
    
    def get_og_image_url(self):
        if self.og_image:
            return self.og_image.url
        elif self.logo:
            return self.logo.url
        return None
    
    def get_twitter_title(self):
        return self.twitter_title or self.get_meta_title()
    
    def get_twitter_description(self):
        return self.twitter_description or self.get_meta_description()
    
    def get_twitter_image_url(self):
        if self.twitter_image:
            return self.twitter_image.url
        elif self.og_image:
            return self.og_image.url
        elif self.logo:
            return self.logo.url
        return None
    
    def get_canonical_url(self):
        """Get canonical URL for the store"""
        return self.canonical_url or ""
    
    def get_robots_meta(self):
        parts = []
        if self.robots_index:
            parts.append('index')
        else:
            parts.append('noindex')
        
        if self.robots_follow:
            parts.append('follow')
        else:
            parts.append('nofollow')
        
        if self.robots_advanced:
            parts.append(self.robots_advanced)
        
        return ', '.join(parts)
    
    def get_organization_schema(self):
        if self.structured_data_organization:
            return self.structured_data_organization
        
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": self.store_name,
            "url": self.canonical_url or "",
            "logo": self.get_og_image_url() or "",
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": self.contact_phone,
                "contactType": "customer service",
                "email": self.contact_email
            }
        }
    
    def get_website_schema(self):
        if self.structured_data_website:
            return self.structured_data_website
        
        return {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": self.store_name,
            "url": self.canonical_url or ""
        }


# ==================== সিগনাল ====================

@receiver(pre_save, sender=Order)
def set_order_as_unviewed(sender, instance, **kwargs):
    """Ensure new orders are marked as unviewed"""
    if not instance.pk:
        instance.is_viewed = False
