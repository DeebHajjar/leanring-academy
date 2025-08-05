# Learning Academy 🎓

A comprehensive online learning platform built with Django, featuring course management, blog system, payment integration, and multi-language support. This project serves as a graduation project for the Python Web Development course at Hsoub Academy.

## 🌟 Features

### 📚 Course Management
- **Course Creation & Management**: Instructors can create and manage courses with detailed descriptions
- **Lesson System**: Structured lessons with video content and progress tracking
- **Comments system**: You can add a comment to each lesson and the instructors will answer you
- **Course evaluation**: Only those registered in the course can add a five-star rating
- **Student Enrollment**: Seamless course enrollment with progress monitoring
- **Instructor Profiles**: Dedicated profiles for course instructors
- **Search & Filter**: Advanced and organized search and filtering for courses

### 📝 Blog System
- **Article Publishing**: Role-based article publishing (instructors and admins only)
- **Comment System**: Interactive commenting with support for both registered and guest users
- **Content Management**: Rich text editor for article creation
- **Category & Tags**: Organized content with categories and tags
- **Search Functionality**: Advanced search and filtering capabilities

### 💳 Payment Integration
- **Stripe Integration**: Secure payment processing with Stripe
- **Course Purchases**: Direct course purchase functionality
- **Order Management**: Complete order tracking and history
- **Webhook Support**: Real-time payment status updates

### 👥 User Management
- **Custom User Model**: Extended user profiles with additional fields
- **Authentication System**: Secure login/logout with session management
- **Social Authentication**: Google OAuth integration
- **Profile Management**: User profile customization with avatar upload
- **Role-based Permissions**: Different access levels for students, instructors, and admins

### 🌍 Internationalization
- **Multi-language Support**: English and Arabic language support
- **RTL Support**: Right-to-left text direction for Arabic content
- **Dynamic Language Switching**: Real-time language switching

### ☁️ Cloud Integration
- **AWS S3 Storage**: Media files stored on Amazon S3
- **Static File Management**: Optimized static file serving
- **Database Support**: PostgreSQL for production, SQLite for development

## 🛠️ Technology Stack

### Backend
- **Django 5.2.4**: Modern Python web framework
- **Python 3.11+**: Latest Python features and performance
- **PostgreSQL**: Production database
- **SQLite**: Development database

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **HTML5 & CSS3**: Modern web standards
- **JavaScript**: Interactive user experience
- **Font Awesome**: Icon library

### Third-party Services
- **Stripe**: Payment processing
- **AWS S3**: Cloud storage
- **Google OAuth**: Social authentication

### Development Tools
- **Django Allauth**: Authentication system
- **Django Crispy Forms**: Form rendering
- **Django Modeltranslation**: Content translation
- **Pillow**: Image processing
- **Gunicorn**: WSGI server for production

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/learning-academy.git
   cd learning-academy
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   
   # AWS S3 Configuration
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_STORAGE_BUCKET_NAME=your-bucket-name
   AWS_S3_REGION_NAME=us-east-1
   
   # Stripe Configuration
   STRIPE_PUBLIC_KEY=pk_test_your-stripe-public-key
   STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
   STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
   
   # Google OAuth
   GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
   GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

   Visit `http://localhost:8000` to view the application.

## 📁 Project Structure

```
learning-academy/
├── accounts/              # User management and authentication
├── blog/                  # Blog system with articles and comments
├── core/                  # Core functionality and middleware
├── courses/               # Course management system
├── payments/              # Payment processing with Stripe
├── project/               # Django project settings
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
│   ├── account/           # Authentication templates
│   ├── blog/              # Blog templates
│   ├── courses/           # Course templates
│   ├── payments/          # Payment templates
│   └── partials/          # Reusable template components
├── locale/                # Translation files
├── requirements.txt       # Python dependencies
├── manage.py              # Django management script
└── README.md              # Project documentation
```

## 🔧 Configuration

### AWS S3 Setup
1. Create an AWS S3 bucket
2. Configure bucket policy for public read access
3. Set up CORS configuration
4. Add AWS credentials to environment variables

### Stripe Setup
1. Create a Stripe account
2. Get API keys from Stripe dashboard
3. Set up webhook endpoints
4. Configure webhook secrets

### Google OAuth Setup
1. Create a Google Cloud project
2. Enable Google+ API
3. Create OAuth 2.0 credentials
4. Add authorized redirect URIs

## 🎨 Features Overview

### For Students
- Browse and search courses
- Enroll in courses with secure payment
- Track learning progress
- Read blog articles and leave comments
- Manage profile and preferences

### For Instructors
- Create and manage courses
- Upload course materials and videos
- Write and publish blog articles
- View student enrollment statistics
- Manage course content

### For Administrators
- Full system administration
- User management
- Content moderation
- Payment oversight
- System analytics

## 🔒 Security Features

- **CSRF Protection**: Cross-site request forgery protection
- **XSS Prevention**: Cross-site scripting protection
- **Secure Sessions**: Encrypted session management
- **HTTPS Enforcement**: SSL/TLS encryption in production
- **Input Validation**: Comprehensive form validation
- **Authentication Security**: Secure password handling

## 🌐 Internationalization

The platform supports multiple languages:
- **English**: Default language
- **Arabic**: Full RTL support with proper text direction

Language switching is available in the navigation bar, and the interface adapts automatically to the selected language.

## 📱 Responsive Design

The platform is fully responsive and works seamlessly across:
- **Desktop**: Full-featured experience
- **Tablet**: Optimized touch interface
- **Mobile**: Mobile-first responsive design

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📄 License

This project is created as a graduation project for Hsoub Academy's Python Web Development course. All rights reserved.

## 🤝 Contributing

This is a graduation project, but feedback and suggestions are welcome. Please feel free to:
- Report bugs
- Suggest new features
- Improve documentation

## 📞 Support

For questions or support regarding this project, please contact:
- **Developer**: Deeb Hajjar
- **Email**: deebhajjar04@gmail.com
- **LinkedIn**: www.linkedin.com/in/deeb-hajjar-297729325

## 🙏 Acknowledgments

- **Hsoub Academy**: To provide excellent courses for learning programming
- **Django Community**: For the amazing framework and documentation
- **Open Source Contributors**: For the various packages used in this project

---

**Built with ❤️ using Django and modern web technologies**
