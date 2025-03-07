# Tengo

![Tengo Logo](https://tengo.thisisemmanuel.pro/static/customer/assets/images/svg/logo.svg)

Tengo is a feature-rich delivery web application that connects users with restaurants, allowing them to explore menus, place orders, and receive real-time updates on the status of their orders. The application integrates secure payment methods and utilizes GeoDjango for location-based services.

## Features

- **User Authentication**: Secure registration, login, and logout functionality.
- **Restaurant Search**: Find restaurants by name or browse their menus.
- **Cart Management**: Add, update, and remove items from your cart with real-time updates.
- **Multiple Orders**: Create and manage orders from multiple restaurants in one session.
- **Secure Payment**: Integrated Rave (Flutterwave) for both saved cards and new payments.
- **Real-time Updates**: Live order status updates via WebSockets for users and restaurants.
- **GeoDjango Location Services**: Integrated for precise location tracking and delivery services.(work in progress)
- **Admin Dashboard**: Dedicated dashboard for restaurants to manage menus and orders.

## Tech Stack

### Backend
- Django 5.x
- Django Channels (WebSockets)
- Django REST Framework
- PostgreSQL with PostGIS
- GeoDjango

### Frontend
- Bootstrap 5
- jQuery

### Other
- Rave (Flutterwave) Payment Gateway
- Docker (optional)
- Nginx

## Getting Started

### Prerequisites

Ensure you have the following installed:
- Python 3.x
- PostgreSQL with PostGIS extension
- Virtualenv
- Redis
- Docker (optional)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/tengo.git
   cd tengo
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up PostgreSQL with PostGIS**
   ```sql
   CREATE DATABASE tengo_db;
   CREATE USER tengo_user WITH PASSWORD 'your_password';
   ALTER ROLE tengo_user SET client_encoding TO 'utf8';
   ALTER ROLE tengo_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE tengo_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE tengo_db TO tengo_user;
   \c tengo_db
   CREATE EXTENSION postgis;
   ```

5. **Set Up Environment Variables**
   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   DATABASE_URL=postgres://tengo_user:your_password@localhost/tengo_db
   PUBLIC_KEY=your_rave_public_key
   SECRET_KEY=your_rave_secret_key
   ```

6. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a Superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

9. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

### Running WebSockets Server

To run the WebSocket server using Daphne:
```bash
daphne -b 0.0.0.0 -p 8001 tengo.asgi:application
```

## Usage

1. Register or log in as a user.
2. Search for restaurants or menu items.
3. Add items to your cart from different restaurants.
4. Proceed to checkout, select a delivery address, and choose a payment method.
5. Complete payment via Rave (Flutterwave) and receive live order updates.
6. Restaurants can view and manage orders via their restaurant dashboard.

## API Endpoints

- `/add_to_cart/` — Add items to the cart.
- `/checkout/` — Checkout and confirm payment.
- `/ws/restaurant/{restaurant_id}/` — WebSocket connection for live order updates.

## Deployment

### Docker (Optional)

1. Build the Docker image:
   ```bash
   docker-compose up --build
   ```

2. Run the application:
   ```bash
   docker-compose up
   ```

### Nginx Setup

Nginx is used for reverse proxying and handling static files in production:
- Configure Nginx to proxy requests to the Django server and serve static files.
- Set up SSL for `wss://` WebSocket connections.

## Troubleshooting

### WebSocket Issues
- Ensure you're using `wss://` in production for secure WebSockets.
- Check that the WebSocket server is running on the correct port.

### Database Migration Issues
- Ensure the PostGIS extension is enabled on your PostgreSQL database.
- Verify all migrations have been applied.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

For more information, please contact [begati16@gmail.com](mailto:begati16@email.com)
