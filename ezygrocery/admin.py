from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import (
    Moholla, Shop, Category, MasterProduct, ShopProduct, MasterProductReview,
    Cart, CartItem, Customer, Rider, Order, OrderItem, RefundRequest,
    ShopSalesReport, RiderCashDeposit, RiderEarning, DeliveryZone, DistanceSlab, SurgePolicy,
    Coupon, Promotion, HeroSlider, SearchQuery, SpecialOffer, StoreSettings, 
    ContactMessage, BlogPost, FAQ, SitemapConfig
)

# ==================== FORM CLASSES WITH ENHANCED TEXTAREA ====================

# ProductAdminForm removed - using MasterProduct instead

class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'
        widgets = {
            'content': forms.Textarea(attrs={'rows': 15, 'cols': 80}),
            'excerpt': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
        }

class StoreSettingsAdminForm(forms.ModelForm):
    class Meta:
        model = StoreSettings
        fields = '__all__'
        widgets = {
            'store_description': forms.Textarea(attrs={'rows': 6, 'cols': 80}),
            'shipping_policy': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
            'return_policy': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
            'privacy_policy': forms.Textarea(attrs={'rows': 15, 'cols': 80}),
            'terms_conditions': forms.Textarea(attrs={'rows': 15, 'cols': 80}),
            'about_us': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
            'refund_policy': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
        }

class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'cols': 80}),
        }

class ShopAdminForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 8, 'cols': 80}),
        }

class PromotionAdminForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'cols': 80}),
        }

class HeroSliderAdminForm(forms.ModelForm):
    class Meta:
        model = HeroSlider
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
        }

class SpecialOfferAdminForm(forms.ModelForm):
    class Meta:
        model = SpecialOffer
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
        }

class FAQAdminForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = '__all__'
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 8, 'cols': 80}),
        }

class MohollaAdminForm(forms.ModelForm):
    class Meta:
        model = Moholla
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
        }

# ==================== INLINE ADMIN CLASSES ====================

class CartItemInline(TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price', 'product_name']
    fields = ['shop_product', 'product_name', 'quantity', 'total_price']
    
    def product_name(self, obj):
        return obj.shop_product.master_product.name if obj.shop_product else "-"
    product_name.short_description = 'পণ্যের নাম'
    
    def total_price(self, obj):
        return f"৳{obj.total_price}"
    total_price.short_description = 'মোট মূল্য'

class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal', 'product_name']
    fields = ['shop_product', 'product_name', 'quantity', 'price', 'subtotal']
    
    def product_name(self, obj):
        return obj.shop_product.master_product.name if obj.shop_product else "-"
    product_name.short_description = 'পণ্যের নাম'
    
    def subtotal(self, obj):
        return f"৳{obj.subtotal}"
    subtotal.short_description = 'সাবটোটাল'

# ProductInline and ProductReviewInline removed - using ShopProduct and MasterProductReview instead

# ==================== MAIN ADMIN CLASSES ====================

@admin.register(Moholla)
class MohollaAdmin(ModelAdmin):
    form = MohollaAdminForm
    list_display = ['name', 'area_code', 'is_active', 'shop_count', 'serial']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'area_code', 'description']
    list_editable = ['serial', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('name', 'slug', 'area_code', 'serial'),
                ('is_active',),
                ('image',),
                ('description',),
            ),
            'classes': ['tab'],
        }),
        (_('SEO & Meta'), {
            'fields': (
                ('meta_title', 'og_title'),
                ('meta_description', 'og_description'),
                ('meta_keywords',),
                ('og_type', 'og_image', 'canonical_url'),
                ('robots_index', 'robots_follow'),
            ),
            'classes': ['tab'],
        }),
        (_('Timestamps'), {
            'fields': (
                ('created_at',),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description='দোকান সংখ্যা')
    def shop_count(self, obj):
        return obj.shops.count()

@admin.register(Shop)
class ShopAdmin(ModelAdmin):
    form = ShopAdminForm
    list_display = ['name', 'moholla', 'owner', 'is_active', 'is_verified', 'total_products', 'total_orders']
    list_filter = ['moholla', 'is_active', 'is_verified', 'created_at']
    search_fields = ['name', 'address', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at', 'total_sales_display']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('name', 'slug', 'owner', 'serial'),
                ('moholla', 'phone', 'email'),
                ('is_active', 'is_verified'),
                ('logo', 'banner'),
                ('address', 'description'),
            ),
            'classes': ['tab'],
        }),
        (_('Business & SEO'), {
            'fields': (
                ('business_type', 'price_range'),
                ('opening_hours',),
                ('meta_title', 'og_title'),
                ('meta_description', 'og_description'),
                ('meta_keywords',),
                ('og_type', 'canonical_url'),
                ('robots_index', 'robots_follow'),
            ),
            'classes': ['tab'],
        }),
        (_('Statistics & Timestamps'), {
            'fields': (
                ('total_sales_display',),
                ('created_at', 'updated_at'),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description='পণ্য সংখ্যা')
    def total_products(self, obj):
        return obj.shop_products.filter(is_active=True).count()
    
    @display(description='অর্ডার সংখ্যা')
    def total_orders(self, obj):
        return obj.orders.count()
    
    @display(description='মোট বিক্রয়')
    def total_sales_display(self, obj):
        return f"৳{obj.total_sales()}"

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    form = CategoryAdminForm
    list_display = ['name', 'serial', 'is_active', 'product_count', 'seo_status']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'meta_title', 'meta_description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['serial', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('name', 'slug', 'serial', 'is_active'),
                ('image',),
                ('description',),
            ),
            'classes': ['tab'],
        }),
        (_('SEO & Meta'), {
            'fields': (
                ('meta_title', 'og_title'),
                ('meta_description', 'og_description'),
                ('meta_keywords',),
                ('og_type', 'canonical_url'),
                ('robots_index', 'robots_follow'),
            ),
            'classes': ['tab'],
        }),
        (_('Timestamps'), {
            'fields': (
                ('created_at', 'updated_at'),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description='পণ্য সংখ্যা')
    def product_count(self, obj):
        return obj.master_products.filter(is_active=True).count()
    
    @display(description='SEO স্ট্যাটাস')
    def seo_status(self, obj):
        if obj.meta_title and obj.meta_description:
            return '✅ সম্পূর্ণ'
        elif obj.meta_title or obj.meta_description:
            return '⚠️ আংশিক'
        return '❌ প্রয়োজন'

# ProductAdmin removed - using MasterProductAdmin and ShopProductAdmin instead

@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ['user_or_session', 'total_items', 'total_price_display', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'total_price_display', 'total_items']
    inlines = [CartItemInline]
    
    fieldsets = (
        ('Cart Information', {
            'fields': (
                ('user', 'session_key'),
                ('total_items', 'total_price_display'),
                ('created_at', 'updated_at'),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description='User/Session')
    def user_or_session(self, obj):
        if obj.user:
            return f"User: {obj.user.username}"
        return f"Session: {obj.session_key}"
    
    @display(description='Total Price')
    def total_price_display(self, obj):
        return f"৳{obj.total_price}"
    
    @display(description='Items Count')
    def total_items(self, obj):
        return obj.total_items

@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ['user', 'moholla', 'phone', 'total_orders', 'created_at']
    list_filter = ['moholla', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'address']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': (
                ('user', 'moholla', 'phone'),
                ('date_of_birth',),
                ('avatar',),
                ('address',),
                ('created_at',),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description='Total Orders')
    def total_orders(self, obj):
        return obj.total_orders()

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [
        'order_number', 'shop', 'customer_info', 'total_amount_display', 
        'status', 'is_viewed_badge', 'created_at'
    ]
    list_filter = ['shop', 'status', 'is_viewed', 'delivery_location', 'created_at']
    search_fields = ['order_number', 'full_name', 'email', 'phone']
    readonly_fields = [
        'order_number', 'created_at', 'updated_at', 
        'total_amount_display', 'customer_info_display'
    ]
    list_editable = ['status']
    inlines = [OrderItemInline]
    actions = ['mark_as_viewed', 'mark_as_processing', 'mark_as_delivered']
    
    fieldsets = (
        ('Order Information', {
            'fields': (
                ('order_number', 'user', 'shop'),
                ('status', 'is_viewed'),
            ),
            'classes': ['tab'],
        }),
        ('Customer Details', {
            'fields': (
                ('full_name', 'email', 'phone'),
                ('delivery_location',),
                ('address', 'special_instructions'),
            ),
            'classes': ['tab'],
        }),
        ('Payment & Delivery', {
            'fields': (
                ('total_amount_display', 'delivery_charge'),
                ('created_at', 'updated_at'),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description='Customer')
    def customer_info(self, obj):
        return f"{obj.full_name} - {obj.phone}"
    
    @display(description='Customer Details')
    def customer_info_display(self, obj):
        return f"Name: {obj.full_name}\nEmail: {obj.email}\nPhone: {obj.phone}\nAddress: {obj.address}"
    
    @display(description='Total Amount')
    def total_amount_display(self, obj):
        return f"৳{obj.total_amount}"
    
    @display(description='Status')
    def is_viewed_badge(self, obj):
        if obj.is_viewed:
            return '✅ Viewed'
        return '🆕 New'
    
    @admin.action(description='Mark selected orders as viewed')
    def mark_as_viewed(self, request, queryset):
        updated = queryset.update(is_viewed=True)
        self.message_user(request, f'{updated} orders marked as viewed.')
    
    @admin.action(description='Mark selected orders as processing')
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    
    @admin.action(description='Mark selected orders as delivered')
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')

@admin.register(ShopSalesReport)
class ShopSalesReportAdmin(ModelAdmin):
    list_display = ['shop', 'date', 'total_orders', 'total_sales', 'total_items_sold']
    list_filter = ['shop', 'date']
    
    fieldsets = (
        ('Report Information', {
            'fields': (
                ('shop', 'date'),
                ('total_orders', 'total_sales', 'total_items_sold'),
            ),
            'classes': ['tab'],
        }),
    )

@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = [
        'code', 'discount_type', 'discount_value', 'minimum_amount',
        'is_valid', 'used_count', 'is_active'
    ]
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['code']
    list_editable = ['is_active']
    readonly_fields = ['used_count', 'validity_status']
    
    fieldsets = (
        ('Coupon Details', {
            'fields': (
                ('code', 'discount_type', 'is_active'),
                ('discount_value', 'minimum_amount', 'maximum_discount'),
                ('valid_from', 'valid_to', 'validity_status'),
                ('usage_limit', 'used_count'),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description='Valid', boolean=True)
    def is_valid(self, obj):
        return obj.is_valid()
    
    @display(description='Status')
    def validity_status(self, obj):
        now = timezone.now()
        if obj.valid_from <= now <= obj.valid_to:
            return '✅ Active'
        elif now < obj.valid_from:
            return '⏳ Upcoming'
        else:
            return '❌ Expired'

@admin.register(Promotion)
class PromotionAdmin(ModelAdmin):
    form = PromotionAdminForm
    list_display = [
        'title', 'image_preview', 'is_active', 'is_valid', 
        'start_date', 'end_date', 'serial'
    ]
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    list_editable = ['serial', 'is_active']
    readonly_fields = ['validity_status']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('title', 'link_url'),
                ('is_active', 'serial'),
                ('start_date', 'end_date', 'validity_status'),
                ('image',),
                ('description',),
            ),
            'classes': ['tab'],
        }),
        ('SEO Meta Tags', {
            'fields': (
                ('meta_title',),
                ('meta_description',),
                ('meta_keywords',),
            ),
            'classes': ['tab'],
        }),
        ('Open Graph Tags', {
            'fields': (
                ('og_title', 'og_type'),
                ('og_image',),
                ('og_description',),
            ),
            'classes': ['tab'],
        }),
        ('Twitter Card Tags', {
            'fields': (
                ('twitter_card', 'twitter_title'),
                ('twitter_image',),
                ('twitter_description',),
            ),
            'classes': ['tab'],
        }),
        ('Robots & Canonical', {
            'fields': (
                ('canonical_url',),
                ('robots_index', 'robots_follow'),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description='Image')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    
    @display(description='Valid', boolean=True)
    def is_valid(self, obj):
        return obj.is_valid()
    
    @display(description='Status')
    def validity_status(self, obj):
        now = timezone.now()
        if obj.is_valid():
            return '✅ Active'
        elif now < obj.start_date:
            return '⏳ Upcoming'
        else:
            return '❌ Expired'

@admin.register(HeroSlider)
class HeroSliderAdmin(ModelAdmin):
    form = HeroSliderAdminForm
    list_display = [
        'title', 'image_preview', 'is_active', 'serial', 
        'button_text', 'button_link'
    ]
    list_filter = ['is_active']
    search_fields = ['title', 'subtitle']
    list_editable = ['serial', 'is_active']
    
    fieldsets = (
        ('Slider Content', {
            'fields': (
                ('title', 'subtitle'),
                ('button_text', 'button_link'),
                ('is_active', 'serial'),
                ('image',),
                ('description',),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description='Image')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="40" style="object-fit: cover;" />', obj.image.url)
        return "-"

@admin.register(SpecialOffer)
class SpecialOfferAdmin(ModelAdmin):
    form = SpecialOfferAdminForm
    list_display = [
        'title', 'discount_percentage', 'is_active', 
        'serial', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle']
    list_editable = ['discount_percentage', 'serial', 'is_active']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Offer Details', {
            'fields': (
                ('title', 'subtitle'),
                ('discount_percentage', 'background_color'),
                ('button_text', 'button_link'),
                ('is_active', 'serial'),
                ('description',),
                ('created_at',),
            ),
            'classes': ['tab'],
        }),
    )

@admin.register(SearchQuery)
class SearchQueryAdmin(ModelAdmin):
    list_display = ['query', 'count', 'last_searched']
    list_filter = ['last_searched']
    search_fields = ['query']
    readonly_fields = ['count', 'last_searched']
    
    fieldsets = (
        ('Search Information', {
            'fields': (
                ('query', 'count', 'last_searched'),
            ),
            'classes': ['tab'],
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = [
        'name', 'email', 'subject', 'is_read', 
        'replied', 'created_at'
    ]
    list_filter = ['is_read', 'replied', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'message_info']
    list_editable = ['is_read', 'replied']
    actions = ['mark_as_read', 'mark_as_replied']
    
    fieldsets = (
        ('Contact Information', {
            'fields': (
                ('name', 'email', 'phone'),
                ('subject',),
                ('message_info',),
                ('is_read', 'replied'),
                ('created_at',),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description='Message Details')
    def message_info(self, obj):
        return format_html(
            '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px; margin: 10px 0;">'
            '<strong>Message:</strong><br>{}'
            '</div>'
            '<div><strong>Received:</strong> {}</div>',
            obj.message, obj.created_at.strftime("%Y-%m-%d %I:%M %p")
        )
    
    @admin.action(description='Mark selected messages as read')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages marked as read.')
    
    @admin.action(description='Mark selected messages as replied')
    def mark_as_replied(self, request, queryset):
        updated = queryset.update(replied=True)
        self.message_user(request, f'{updated} messages marked as replied.')

@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    form = BlogPostAdminForm
    list_display = ['title', 'author', 'is_published', 'published_at', 'view_count']
    list_filter = ['is_published', 'category', 'published_at', 'created_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'view_count']
    
    fieldsets = (
        ('Blog Content', {
            'fields': (
                ('title', 'slug'),
                ('author', 'category', 'tags'),
                ('is_published', 'published_at', 'view_count'),
                ('featured_image',),
                ('excerpt',),
                ('content',),
            ),
            'classes': ['tab'],
        }),
        ('SEO Meta Tags', {
            'fields': (
                ('meta_title',),
                ('meta_description',),
                ('meta_keywords',),
            ),
            'classes': ['tab'],
        }),
        ('Open Graph Tags', {
            'fields': (
                ('og_title', 'og_type'),
                ('og_image',),
                ('og_description',),
            ),
            'classes': ['tab'],
        }),
        ('Twitter Card Tags', {
            'fields': (
                ('twitter_card', 'twitter_title'),
                ('twitter_image',),
                ('twitter_description',),
            ),
            'classes': ['tab'],
        }),
        ('Robots & Canonical', {
            'fields': (
                ('canonical_url',),
                ('robots_index', 'robots_follow'),
                ('created_at', 'updated_at'),
            ),
            'classes': ['tab'],
        }),
    )

@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    form = FAQAdminForm
    list_display = ['question', 'category', 'is_active', 'serial']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['serial', 'is_active']
    
    fieldsets = (
        ('FAQ Content', {
            'fields': (
                ('category', 'is_active', 'serial'),
                ('question',),
                ('answer',),
                ('created_at',),
            ),
            'classes': ['tab'],
        }),
    )

# ProductReviewAdmin removed - using MasterProductReviewAdmin instead

@admin.register(SitemapConfig)
class SitemapConfigAdmin(ModelAdmin):
    list_display = ['__str__']
    
    fieldsets = (
        ('Sitemap Configuration', {
            'fields': (
                ('include_products', 'include_categories', 'include_shops'),
                ('include_mohollas', 'include_blog_posts'),
                ('products_priority', 'categories_priority', 'shops_priority'),
                ('products_changefreq',),
            ),
            'classes': ['tab'],
        }),
    )
    
    def has_add_permission(self, request):
        return not SitemapConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(StoreSettings)
class StoreSettingsAdmin(ModelAdmin):
    form = StoreSettingsAdminForm
    list_display = ['store_name', 'contact_phone', 'contact_email', 'updated_at']
    readonly_fields = ['created_at', 'updated_at', 'seo_status', 'tracking_status']
    
    fieldsets = (
        ('Store Basic Information', {
            'fields': (
                ('store_name', 'contact_email', 'contact_phone'),
                ('logo', 'logo_dark', 'favicon'),
                ('address', 'store_description'),
            ),
            'classes': ['tab'],
        }),
        ('Social Media', {
            'fields': (
                ('facebook_url', 'twitter_url', 'instagram_url'),
                ('linkedin_url', 'youtube_url', 'whatsapp_number'),
            ),
            'classes': ['tab'],
        }),
        ('Store Configuration', {
            'fields': (
                ('currency', 'currency_symbol', 'maintenance_mode'),
                ('delivery_charge_inside_dhaka', 'delivery_charge_outside_dhaka'),
                ('free_delivery_minimum_amount', 'minimum_order_amount'),
            ),
            'classes': ['tab'],
        }),
        ('Store Policies', {
            'fields': (
                ('shipping_policy',),
                ('return_policy',),
                ('privacy_policy',),
                ('terms_conditions',),
                ('about_us',),
                ('refund_policy',),
            ),
            'classes': ['tab'],
        }),
        ('SEO Meta Tags', {
            'fields': (
                ('meta_title',),
                ('meta_description',),
                ('meta_keywords',),
                ('canonical_url', 'robots_advanced'),
                ('robots_index', 'robots_follow'),
            ),
            'classes': ['tab'],
        }),
        ('Open Graph Tags', {
            'fields': (
                ('og_title', 'og_type', 'og_site_name'),
                ('social_media_title',),
                ('og_description', 'social_media_description'),
                ('og_image',),
            ),
            'classes': ['tab'],
        }),
        ('Twitter Card Tags', {
            'fields': (
                ('twitter_card', 'twitter_site', 'twitter_creator'),
                ('twitter_title',),
                ('twitter_description',),
                ('twitter_image',),
            ),
            'classes': ['tab'],
        }),
        ('Facebook Pixel & Analytics', {
            'fields': (
                ('facebook_pixel_id', 'facebook_app_id'),
                ('facebook_pixel_enabled', 'facebook_pixel_debug'),
                ('facebook_page_url',),
            ),
            'classes': ['tab'],
        }),
        ('Google Analytics & GTM', {
            'fields': (
                ('google_analytics_id', 'google_analytics_4_id'),
                ('google_analytics_enabled',),
                ('google_tag_manager_id',),
                ('google_tag_manager_enabled',),
            ),
            'classes': ['tab'],
        }),
        ('Site Verification', {
            'fields': (
                ('google_site_verification', 'bing_site_verification'),
                ('yandex_verification', 'baidu_verification'),
            ),
            'classes': ['tab'],
        }),
        ('Structured Data', {
            'fields': (
                ('structured_data_organization', 'structured_data_website', 'structured_data_breadcrumb'),
            ),
            'classes': ['tab'],
        }),
        ('Performance & Technical SEO', {
            'fields': (
                ('enable_compression', 'enable_caching', 'enable_sitemap'),
                ('enable_robots_txt', 'enable_schema_markup'),
            ),
            'classes': ['tab'],
        }),
        ('Advanced SEO', {
            'fields': (
                ('seo_author', 'seo_geo_region'),
                ('seo_geo_placename',),
                ('seo_geo_position', 'seo_icbm'),
            ),
            'classes': ['tab'],
        }),
        ('Status Overview', {
            'fields': (
                ('seo_status', 'tracking_status'),
                ('created_at', 'updated_at'),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description='SEO Status')
    def seo_status(self, obj):
        status = []
        if obj.meta_title:
            status.append('✅ Meta Title')
        else:
            status.append('❌ Meta Title')
        
        if obj.meta_description:
            status.append('✅ Meta Description')
        else:
            status.append('❌ Meta Description')
        
        if obj.meta_keywords:
            status.append('✅ Meta Keywords')
        else:
            status.append('⚠️ Meta Keywords')
        
        return format_html('<br>'.join(status))
    
    @display(description='Tracking Status')
    def tracking_status(self, obj):
        status = []
        if obj.facebook_pixel_enabled and obj.facebook_pixel_id:
            status.append('✅ Facebook Pixel')
        else:
            status.append('❌ Facebook Pixel')
        
        if obj.google_analytics_enabled and obj.google_analytics_id:
            status.append('✅ Google Analytics')
        else:
            status.append('❌ Google Analytics')
        
        return format_html('<br>'.join(status))
    
    def has_add_permission(self, request):
        return not StoreSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


# ==================== নতুন Master Product System Admin ====================

# Forms
class MasterProductAdminForm(forms.ModelForm):
    class Meta:
        model = MasterProduct
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 8}),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'features': forms.Textarea(attrs={'rows': 6}),
        }

class ShopProductAdminForm(forms.ModelForm):
    class Meta:
        model = ShopProduct
        fields = '__all__'
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class BulkAddProductsForm(forms.Form):
    shop = forms.ModelChoiceField(
        queryset=Shop.objects.filter(is_active=True),
        label="দোকান নির্বাচন করুন"
    )
    products = forms.ModelMultipleChoiceField(
        queryset=MasterProduct.objects.filter(is_active=True),
        label="পণ্য নির্বাচন করুন (একাধিক)",
        help_text="Ctrl/Cmd চেপে একাধিক পণ্য নির্বাচন করুন"
    )
    cost_price = forms.DecimalField(label="ক্রয় মূল্য", required=False)
    selling_price = forms.DecimalField(label="বিক্রয় মূল্য", required=False)
    stock = forms.IntegerField(label="স্টক", initial=10)
    use_mrp = forms.BooleanField(label="MRP ব্যবহার করুন", initial=True, required=False)

# Inlines
class MasterProductReviewInline(TabularInline):
    model = MasterProductReview
    extra = 0
    readonly_fields = ['user', 'rating', 'created_at']
    fields = ['user', 'rating', 'title', 'is_approved', 'created_at']

# Master Product Admin
@admin.register(MasterProduct)
class MasterProductAdmin(ModelAdmin):
    form = MasterProductAdminForm
    list_display = ['display_image', 'name', 'sku', 'category', 'brand', 'mrp', 'total_shops', 'price_range', 'is_active']
    list_filter = ['category', 'brand', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'barcode', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MasterProductReviewInline]
    
    fieldsets = (
        ('মূল তথ্য', {
            'fields': (
                ('name', 'slug', 'sku'),
                ('barcode', 'category', 'is_active'),
                ('brand', 'model_number', 'mrp'),
                ('image', 'image_2', 'image_3'),
                ('short_description',),
                ('description',),
            ),
            'classes': ['tab'],
        }),
        ('পণ্যের বিবরণ', {
            'fields': (
                ('weight', 'dimensions'),
                ('gtin', 'mpn'),
                ('features',),
            ),
            'classes': ['tab'],
        }),
        ('SEO সেটিংস', {
            'fields': (
                ('meta_title', 'og_title'),
                ('meta_description', 'og_description'),
                ('meta_keywords',),
                ('og_image', 'canonical_url'),
                ('robots_index', 'robots_follow'),
                ('created_at', 'updated_at'),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description="ছবি")
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;" />', obj.image.url)
        return "No image"
    
    @display(description="দোকান সংখ্যা")
    def total_shops(self, obj):
        count = obj.total_shops_selling()
        return format_html('<span style="font-weight: bold; color: #10b981;">{}</span>', count)
    
    @display(description="মূল্য পরিসীমা")
    def price_range(self, obj):
        lowest = obj.lowest_price()
        highest = obj.highest_price()
        if lowest and highest:
            if lowest == highest:
                return format_html('<span style="font-weight: bold;">৳{}</span>', lowest)
            return format_html('<span style="color: #10b981;">৳{}</span> - <span style="color: #ef4444;">৳{}</span>', lowest, highest)
        return "N/A"

# Shop Product Admin
@admin.register(ShopProduct)
class ShopProductAdmin(ModelAdmin):
    form = ShopProductAdminForm
    list_display = ['display_image', 'product_name', 'shop_name', 'sku_display', 'stock_status', 'price_display', 'profit_display', 'is_active']
    list_filter = ['shop', 'master_product__category', 'is_active', 'is_featured', 'created_at']
    search_fields = ['master_product__name', 'master_product__sku', 'shop_sku', 'shop__name']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('দোকান ও পণ্য', {
            'fields': (
                ('shop', 'master_product'),
                ('shop_sku', 'is_active', 'is_featured'),
                ('cost_price', 'selling_price', 'discount_price'),
                ('stock', 'low_stock_alert'),
                ('location_in_shop',),
                ('notes',),
                ('created_at', 'updated_at'),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description="ছবি")
    def display_image(self, obj):
        if obj.master_product.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />', obj.master_product.image.url)
        return "No image"
    
    @display(description="পণ্যের নাম")
    def product_name(self, obj):
        return obj.master_product.name
    
    @display(description="দোকান")
    def shop_name(self, obj):
        return obj.shop.name
    
    @display(description="SKU")
    def sku_display(self, obj):
        if obj.shop_sku:
            return format_html('<strong>Master:</strong> {}<br><strong>Shop:</strong> {}', obj.master_product.sku, obj.shop_sku)
        return obj.master_product.sku
    
    @display(description="স্টক")
    def stock_status(self, obj):
        if obj.is_out_of_stock:
            return format_html('<span style="color: #ef4444; font-weight: bold;">স্টক শেষ</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color: #f59e0b; font-weight: bold;">{} (কম)</span>', obj.stock)
        else:
            return format_html('<span style="color: #10b981; font-weight: bold;">{}</span>', obj.stock)
    
    @display(description="মূল্য")
    def price_display(self, obj):
        if obj.is_on_sale:
            return format_html(
                '<span style="color: #ef4444; font-weight: bold;">৳{}</span><br>'
                '<span style="color: #6b7280; text-decoration: line-through; font-size: 11px;">৳{}</span>',
                obj.discount_price, obj.selling_price
            )
        return format_html('<span style="font-weight: bold;">৳{}</span>', obj.selling_price)
    
    @display(description="লাভ")
    def profit_display(self, obj):
        profit = obj.profit_margin
        if profit > 0:
            return format_html('<span style="color: #10b981; font-weight: bold;">৳{}</span>', f'{profit:.2f}')
        elif profit < 0:
            return format_html('<span style="color: #ef4444; font-weight: bold;">৳{}</span>', f'{profit:.2f}')
        return format_html('<span>৳0.00</span>')
    
    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        custom_urls = [
            path('bulk-add/', self.admin_site.admin_view(self.bulk_add_products), name='ezygrocery_shopproduct_bulk_add'),
        ]
        return custom_urls + urls
    
    def bulk_add_products(self, request):
        from django.shortcuts import render, redirect
        from django.contrib import messages
        
        if request.method == 'POST':
            form = BulkAddProductsForm(request.POST)
            if form.is_valid():
                shop = form.cleaned_data['shop']
                products = form.cleaned_data['products']
                cost_price = form.cleaned_data.get('cost_price')
                selling_price = form.cleaned_data.get('selling_price')
                stock = form.cleaned_data['stock']
                use_mrp = form.cleaned_data['use_mrp']
                
                added_count = 0
                skipped_count = 0
                
                for product in products:
                    if ShopProduct.objects.filter(shop=shop, master_product=product).exists():
                        skipped_count += 1
                        continue
                    
                    if use_mrp:
                        final_selling_price = product.mrp
                        final_cost_price = cost_price or (product.mrp * 0.7)
                    else:
                        final_selling_price = selling_price or product.mrp
                        final_cost_price = cost_price or (final_selling_price * 0.7)
                    
                    ShopProduct.objects.create(
                        shop=shop,
                        master_product=product,
                        cost_price=final_cost_price,
                        selling_price=final_selling_price,
                        stock=stock,
                        is_active=True
                    )
                    added_count += 1
                
                messages.success(request, f'✅ {added_count}টি পণ্য সফলভাবে যোগ হয়েছে! {skipped_count}টি পণ্য ইতিমধ্যে ছিল।')
                return redirect('admin:ezygrocery_shopproduct_changelist')
        else:
            form = BulkAddProductsForm()
        
        context = {
            'form': form,
            'title': 'দোকানে একসাথে পণ্য যোগ করুন',
            'opts': self.model._meta,
        }
        return render(request, 'admin/bulk_add_products.html', context)

# Master Product Review Admin
@admin.register(MasterProductReview)
class MasterProductReviewAdmin(ModelAdmin):
    list_display = ['product_name', 'user', 'shop_name', 'rating', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified_purchase', 'created_at']
    search_fields = ['master_product__name', 'user__username', 'title', 'comment']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('রিভিউ বিবরণ', {
            'fields': (
                ('master_product', 'user', 'shop'),
                ('rating', 'title'),
                ('is_approved', 'is_verified_purchase'),
                ('comment',),
                ('created_at',),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description="পণ্য")
    def product_name(self, obj):
        return obj.master_product.name
    
    @display(description="দোকান")
    def shop_name(self, obj):
        return obj.shop.name if obj.shop else "N/A"


# ==================== CART ITEM ADMIN ====================
@admin.register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = ['cart', 'product_name', 'quantity', 'total_price_display']
    list_filter = ['cart__user']
    search_fields = ['shop_product__master_product__name', 'cart__user__username']
    readonly_fields = ['total_price_display']
    
    fieldsets = (
        ('Cart Item Details', {
            'fields': (
                ('cart', 'shop_product', 'quantity', 'total_price_display'),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description="Product")
    def product_name(self, obj):
        return obj.shop_product.master_product.name
    
    @display(description="Total Price")
    def total_price_display(self, obj):
        return f"৳{obj.total_price}"


# ==================== RIDER ADMIN ====================
@admin.register(Rider)
class RiderAdmin(ModelAdmin):
    list_display = ['user', 'nid', 'phone', 'is_active', 'rating', 'total_deliveries', 'on_time_rate']
    list_filter = ['is_active', 'police_verification', 'created_at']
    search_fields = ['user__username', 'nid', 'phone', 'driving_license']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('user', 'phone'),
                ('nid', 'driving_license', 'bike_registration'),
                ('police_verification', 'is_active'),
                ('rating', 'total_deliveries', 'on_time_rate'),
                ('created_at', 'updated_at'),
            ),
            'classes': ['tab'],
        }),
    )


# ==================== ORDER ITEM ADMIN ====================
@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'price', 'subtotal_display']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__order_number', 'shop_product__master_product__name']
    readonly_fields = ['subtotal_display']
    
    fieldsets = (
        ('Order Item Details', {
            'fields': (
                ('order', 'shop_product', 'quantity', 'price'),
                ('subtotal_display',),
            ),
            'classes': ['tab'],
        }),
    )
    
    @display(description="Product")
    def product_name(self, obj):
        return obj.shop_product.master_product.name
    
    @display(description="Subtotal")
    def subtotal_display(self, obj):
        return f"৳{obj.subtotal}"


# ==================== REFUND REQUEST ADMIN ====================
@admin.register(RefundRequest)
class RefundRequestAdmin(ModelAdmin):
    list_display = ['order', 'requested_by', 'reason', 'amount', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'reason', 'created_at']
    search_fields = ['order__order_number', 'requested_by__username']
    list_editable = ['is_approved']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Refund Details', {
            'fields': (
                ('order', 'requested_by', 'reason'),
                ('amount', 'is_approved', 'processed_at'),
                ('created_at', 'updated_at'),
            ),
            'classes': ['tab'],
        }),
    )


# ==================== RIDER CASH DEPOSIT ADMIN ====================
@admin.register(RiderCashDeposit)
class RiderCashDepositAdmin(ModelAdmin):
    list_display = ['rider', 'date', 'total_collected', 'deposited_amount', 'discrepancy', 'verified']
    list_filter = ['verified', 'date', 'created_at']
    search_fields = ['rider__user__username']
    list_editable = ['verified']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Deposit Details', {
            'fields': (
                ('rider', 'date', 'deposited_at'),
                ('total_collected', 'deposited_amount', 'discrepancy'),
                ('verified',),
                ('created_at', 'updated_at'),
            ),
            'classes': ['tab'],
        }),
    )


# ==================== RIDER EARNING ADMIN ====================
@admin.register(RiderEarning)
class RiderEarningAdmin(ModelAdmin):
    list_display = ['rider', 'order', 'base_payout', 'distance_bonus', 'surge_bonus', 'incentive', 'total', 'date']
    list_filter = ['date']
    search_fields = ['rider__user__username', 'order__order_number']
    
    fieldsets = (
        ('Earning Details', {
            'fields': (
                ('rider', 'order', 'date'),
                ('base_payout', 'distance_bonus', 'surge_bonus'),
                ('incentive', 'total'),
            ),
            'classes': ['tab'],
        }),
    )


# ==================== DELIVERY ZONE ADMIN ====================
@admin.register(DeliveryZone)
class DeliveryZoneAdmin(ModelAdmin):
    list_display = ['name', 'base_fare']
    search_fields = ['name']
    
    fieldsets = (
        ('Zone Details', {
            'fields': (
                ('name', 'base_fare'),
            ),
            'classes': ['tab'],
        }),
    )


# ==================== DISTANCE SLAB ADMIN ====================
@admin.register(DistanceSlab)
class DistanceSlabAdmin(ModelAdmin):
    list_display = ['min_distance', 'max_distance', 'additional_charge']
    
    fieldsets = (
        ('Distance Slab', {
            'fields': (
                ('min_distance', 'max_distance', 'additional_charge'),
            ),
            'classes': ['tab'],
        }),
    )


# ==================== SURGE POLICY ADMIN ====================
@admin.register(SurgePolicy)
class SurgePolicyAdmin(ModelAdmin):
    list_display = ['surge_type', 'min_amount', 'max_amount', 'is_active']
    list_filter = ['surge_type', 'is_active']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Surge Policy', {
            'fields': (
                ('surge_type', 'is_active'),
                ('min_amount', 'max_amount'),
            ),
            'classes': ['tab'],
        }),
    )