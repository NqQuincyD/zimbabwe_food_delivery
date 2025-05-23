# Zimbabwe Food Delivery

A comprehensive food delivery platform built with Django, specifically designed for restaurants in Zimbabwe. The platform connects customers with local restaurants and provides a seamless delivery experience.

## Features

- **User Management**
  - Customer, Restaurant Owner, and Delivery Driver roles
  - Profile management
  - Address management
  - Authentication and authorization

- **Restaurant Management**
  - Restaurant profile creation and management
  - Menu management
  - Order management
  - Business hours settings

- **Ordering System**
  - Shopping cart functionality
  - Real-time order tracking
  - Order history
  - Multiple delivery addresses

- **Delivery System**
  - Driver availability management
  - Order assignment
  - Delivery tracking
  - Delivery history

- **Payment Integration**
  - Secure payment processing
  - Multiple payment methods
  - Order total calculation
  - Tax and delivery fee handling

- **Review System**
  - Restaurant ratings and reviews
  - Driver ratings
  - Order feedback

## Technology Stack

- Python 3.8+
- Django 4.2+
- Bootstrap 5.2
- SQLite (Development) / PostgreSQL (Production)
- JavaScript/jQuery
- HTML5/CSS3

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/zimbabwe_food_delivery.git
cd zimbabwe_food_delivery
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Environment Variables

Create a `.env` file in the root directory and add the following variables:
```
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

## Project Structure

```
zimbabwe_food_delivery/
├── accounts/          # User management app
├── delivery/          # Delivery management app
├── orders/           # Order processing app
├── payments/         # Payment processing app
├── restaurants/      # Restaurant management app
├── reviews/          # Review system app
├── static/           # Static files
├── templates/        # HTML templates
├── media/           # User-uploaded files
└── food_delivery/    # Main project settings
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please email contact@zimfood.co.zw or create an issue in the GitHub repository.

## Authors

- Your Name - Initial work

## Acknowledgments

- Thanks to all contributors who have helped with the project
- Special thanks to the Zimbabwe restaurant community for their support 