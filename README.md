# 🏋️‍♂️ Fitness Studio Booking API

A comprehensive Django REST API for managing fitness studio class bookings. This application allows clients to view upcoming fitness classes, book spots, and manage their bookings through both REST API endpoints and a web interface.

## 📋 Features

- **View Classes**: Get all upcoming fitness classes with availability
- **Book Classes**: Reserve spots in available classes with validation
- **View Bookings**: Retrieve all bookings for a specific email address
- **Web Interface**: User-friendly HTML interface for all operations
- **Timezone Support**: IST timezone management for all class schedules
- **Race Condition Protection**: Database-level locking for concurrent bookings
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Input Validation**: Robust validation for all user inputs

## 🛠️ Tech Stack

- **Backend**: Django 5.2.3 with Django REST Framework
- **Database**: SQLite (in-memory for development)
- **Timezone**: Asia/Kolkata (IST)
- **Python**: 3.8+

## 📁 Project Structure

```
fitness_booking/
├── fitness_booking/
│   ├── settings.py          # Django settings with logging config
│   ├── urls.py             # Project URL configuration
│   ├── wsgi.py             # WSGI application
│   └── asgi.py             # ASGI application
├── studio/
│   ├── models.py           # FitnessClass and Booking models
│   ├── serializers.py      # API serializers with validation
│   ├── views.py            # API and template views
│   ├── urls.py             # App URL patterns
│   ├── admin.py            # Django admin configuration
│   ├── signals.py          # Database signals for slot management
│   ├── tests.py            # Unit tests
│   └── management/
│       └── commands/
│           └── seed_data.py # Sample data seeding command
├── templates/
│   ├── main.html           # Base template
│   ├── home.html           # Classes listing page
│   ├── book.html           # Booking form page
│   ├── viewbook.html       # View bookings page
│   ├── nav.html            # Navigation component
│   └── footer.html         # Footer with API info
├── static/
│   └── main.css            # Styling
└── requirements.txt        # Python dependencies
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd fitness_booking
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv myenv
   
   # On Windows
   myenv\Scripts\activate
   
   # On macOS/Linux
   source myenv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install django djangorestframework pytz
   ```

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Load Sample Data**
   ```bash
   python manage.py seed_data
   ```

6. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://127.0.0.1:8000/`

## 📊 Sample Data

The application comes with pre-seeded sample data including:

- **6 Fitness Classes** across 3 types (YOGA, ZUMBA, HIIT)
- **Different Instructors**: Priya Sharma, Rahul Gupta, Anjali Verma, etc.
- **Varied Schedules**: Classes scheduled over the next 5 days
- **Different Capacities**: 12-25 slots per class

### Sample Classes:
- YOGA with Priya Sharma - 15 slots
- ZUMBA with Rahul Gupta - 20 slots  
- HIIT with Anjali Verma - 12 slots
- And more...

## 🔌 API Endpoints

### Base URL: `http://127.0.0.1:8000/`

### 1. Get All Classes
**GET** `/classes/`

Returns all upcoming fitness classes.

**Response Format:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "name": "YOGA",
            "instructor": "Priya Sharma",
            "datetime": "2025-06-27T09:00:00Z",
            "local_datetime": "2025-06-27 14:30:00 IST",
            "total_slots": 15,
            "available_slots": 15,
            "is_available": true
        }
    ],
    "count": 6
}
```

### 2. Book a Class
**POST** `/book/`

Book a spot in a fitness class.

**Request Body:**
```json
{
    "class_id": 1,
    "client_name": "John Doe",
    "client_email": "john@example.com"
}
```

**Response Format:**
```json
{
    "status": "success",
    "message": "Booking created successfully",
    "data": {
        "id": 1,
        "fitness_class": {
            "id": 1,
            "name": "YOGA",
            "instructor": "Priya Sharma"
        },
        "client_name": "John Doe",
        "client_email": "john@example.com",
        "booked_at": "2025-06-26T15:30:00Z",
        "local_booked_time": "2025-06-26 21:00:00 IST",
        "is_cancelled": false
    }
}
```

### 3. Get User Bookings
**GET** `/bookings/?email=user@example.com`

Retrieve all bookings for a specific email address.

**Response Format:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "fitness_class": {
                "id": 1,
                "name": "YOGA",
                "instructor": "Priya Sharma"
            },
            "client_name": "John Doe",
            "client_email": "john@example.com",
            "booked_at": "2025-06-26T15:30:00Z",
            "local_booked_time": "2025-06-26 21:00:00 IST",
            "is_cancelled": false
        }
    ],
    "count": 1
}
```

## 🧪 Sample cURL Requests

### Get All Classes
```bash
curl -X GET "http://127.0.0.1:8000/classes/" \
  -H "Accept: application/json"
```

### Book a Class
```bash
curl -X POST "http://127.0.0.1:8000/book/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -d '{
    "class_id": 1,
    "client_name": "John Doe",
    "client_email": "john@example.com"
  }'
```

### Get User Bookings
```bash
curl -X GET "http://127.0.0.1:8000/bookings/?email=john@example.com" \
  -H "Accept: application/json"
```

## 📮 Postman Collection

### Import Settings:
- **Base URL**: `http://127.0.0.1:8000`
- **Content-Type**: `application/json`

### Requests to Create:

1. **GET Classes**
   - Method: GET
   - URL: `{{baseUrl}}/classes/`

2. **POST Book Class**
   - Method: POST
   - URL: `{{baseUrl}}/book/`
   - Body (JSON):
     ```json
     {
       "class_id": 1,
       "client_name": "Test User",
       "client_email": "test@example.com"
     }
     ```

3. **GET User Bookings**
   - Method: GET
   - URL: `{{baseUrl}}/bookings/?email=test@example.com`

## 🌐 Web Interface

Access the web interface at `http://127.0.0.1:8000/`:

- **Home Page**: View all upcoming classes in a table format
- **Book Class**: Interactive form to book classes
- **View Bookings**: Search and view bookings by email

## ⚡ Key Features

### Timezone Management
- All classes are stored and managed in IST (Asia/Kolkata)
- Automatic timezone conversion for display
- Past class detection based on current IST time

### Race Condition Protection
- Database-level row locking using `select_for_update()`
- Atomic transactions for booking operations
- Prevents overbooking in high-concurrency scenarios

### Input Validation
- Name validation (letters, spaces, dots only)
- Email format validation
- Class availability validation
- Duplicate booking prevention

### Error Handling
- Comprehensive error responses with appropriate HTTP status codes
- Detailed logging for debugging
- User-friendly error messages

## 🧪 Testing

Run the test suite:
```bash
python manage.py test studio
```

### Test Coverage:
- Model validation and methods
- API endpoint functionality
- Booking logic and constraints
- Race condition scenarios

## 📝 Logging

Logs are written to `studio.log` in the project root. Log levels include:
- **INFO**: Successful operations
- **WARNING**: Validation errors and duplicate attempts
- **ERROR**: System errors and exceptions

## 🛡️ Security Features

- CSRF protection for web forms
- SQL injection prevention through Django ORM
- Input sanitization and validation
- Email validation
- Unique constraint enforcement

## 🔧 Configuration

### Django Settings (`settings.py`):
- **TIME_ZONE**: 'Asia/Kolkata'
- **DEBUG**: True (development)
- **Database**: SQLite
- **REST Framework**: JSON renderer, pagination

### Key Models:
- **FitnessClass**: Class information with availability tracking
- **Booking**: User bookings with email-based uniqueness

## 📈 Performance Considerations

- Database indexing on datetime fields
- Select related queries to prevent N+1 problems
- Atomic transactions for data consistency
- Efficient filtering for upcoming classes only

## 🚀 Deployment Considerations

For production deployment:
1. Set `DEBUG = False`
2. Configure proper database (PostgreSQL/MySQL)
3. Set up proper static file serving
4. Configure email backend for notifications
5. Set up proper logging infrastructure
6. Use environment variables for sensitive settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is created for educational/assignment purposes.

---

**🎯 Assignment Completion Status:**
- ✅ GET /classes endpoint
- ✅ POST /book endpoint  
- ✅ GET /bookings endpoint
- ✅ Input validation and error handling
- ✅ SQLite database integration
- ✅ IST timezone management
- ✅ Sample data and seed script
- ✅ Clean, modular code structure
- ✅ Comprehensive logging
- ✅ Unit tests
- ✅ Web interface (bonus)
- ✅ Race condition protection (bonus)
- ✅ Admin interface (bonus)