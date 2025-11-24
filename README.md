# EzyGrocery - কাছের দোকান

A comprehensive Django-based local grocery delivery platform connecting customers with nearby shops in Bangladesh.

## Features

### 🏪 Multi-Shop Management
- Shop registration and verification system
- Location-based shop discovery (Moholla/area-wise)
- Shop performance tracking and analytics
- Commission-based revenue model

### 📦 Product Management
- Master product catalog system
- Shop-specific product inventory
- Product reviews and ratings
- Category-based organization
- SKU and barcode support

### 🛒 Order & Cart System
- Session-based and user-based cart
- Multi-status order tracking (pending, processing, shipped, delivered, cancelled)
- Order management for shops
- Refund request handling

### 🚴 Delivery Management
- Rider registration with verification (NID, driving license)
- Dynamic delivery fee calculation
- Distance-based pricing slabs
- Surge pricing policies
- Rider earnings and cash deposit tracking

### 👥 User Management
- Customer profiles with location
- Shop owner accounts
- Rider accounts
- Role-based access control

### 🎯 Marketing & Promotions
- Coupon system (percentage/fixed discount)
- Hero sliders for homepage
- Special offers and promotions
- SEO optimization for all major models

### 📊 Analytics & Reports
- Shop sales reports
- Order tracking and analytics
- Search query tracking
- Rider performance metrics

### 🌐 Content Management
- Blog posts with SEO
- FAQ management
- Contact form submissions
- Sitemap configuration

## Tech Stack

- **Framework**: Django 5.2.6
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Admin Panel**: Django Unfold (modern UI)
- **Media Storage**: Local filesystem / Cloud storage ready
- **Caching**: Redis support
- **Language**: Bengali (bn-bd) with English support

## Installation

### Prerequisites
- Python 3.10+
- pip
- virtualenv (recommended)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ezygrocery
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Collect static files:
```bash
python manage.py collectstatic
```

7. Run development server:
```bash
python manage.py runserver
```

8. Access the application:
- Frontend: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## Project Structure

```
ezygrocery/
├── config/                 # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI config
├── ezygrocery/            # Main application
│   ├── models.py          # Database models
│   ├── admin.py           # Admin configuration
│   ├── views.py           # View logic
│   ├── context_processors.py  # Template context
│   ├── migrations/        # Database migrations
│   ├── static/            # Static files
│   └── templates/         # HTML templates
├── static/                # Global static files
├── staticfiles/           # Collected static files
├── media/                 # User uploads
├── templates/             # Global templates
├── logs/                  # Application logs
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## Key Models

- **Moholla**: Geographic areas/neighborhoods
- **Shop**: Store information and management
- **MasterProduct**: Central product catalog
- **ShopProduct**: Shop-specific product inventory
- **Order**: Customer orders
- **Customer**: Customer profiles
- **Rider**: Delivery personnel
- **Coupon**: Discount codes
- **Category**: Product categories

## Configuration

### Environment Variables
Create a `.env` file for production:
```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Admin Panel
The project uses Django Unfold for a modern admin interface with:
- Custom sidebar navigation
- Bengali language support
- Organized sections for different modules
- Custom styling and branding

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Import Demo Data
```bash
python demoimport_complete.py
```

## Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up PostgreSQL database
- [ ] Configure static file serving (WhiteNoise included)
- [ ] Set up media file storage
- [ ] Configure email backend
- [ ] Enable HTTPS settings
- [ ] Set up logging
- [ ] Configure Redis for caching
- [ ] Set up backup strategy

### Security Settings
The project includes production-ready security settings:
- HTTPS redirect
- Secure cookies
- XSS protection
- Content type sniffing protection
- HSTS headers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license here]

## Support

For support, email [your-email] or create an issue in the repository.

## Acknowledgments

- Django Unfold for the admin interface
- Django community for excellent documentation
