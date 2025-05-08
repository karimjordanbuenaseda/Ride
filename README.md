# Ride API

A RESTful API built with Django REST Framework for managing ride information, including users, rides, and ride events.

## Features

- Complete RESTful API with CRUD operations for rides, users, and ride events
- JWT Authentication with admin role-based permissions
- Support for filtering rides by status and rider email
- Support for sorting rides by pickup distance to a given GPS position
- Distance-based sorting using Haversine formula

### Running the Application

1. Clone the repository
   ```bash
   git clone https://github.com/karimjordanbuenaseda/Ride.git
   cd ride-management-api
   ```

2. Start the Docker containers
   ```bash
   docker-compose up -d
   ```

3. Check the logs
   ```bash
   docker-compose logs -f app
   ```

4. Access the API at `http://localhost:8080/api/`

## Initializing Sample Data

The application includes a Django management command `init_data` to initialize the database with sample data. This is useful for development and testing purposes.

### Usage

```bash
# Initialize all data (users, rides, ride events)
python manage.py init_data

# Clean existing data before initializing new data
python manage.py init_data --clean

# Full clean and re-initialize
python manage.py init_data --full

# Only recreate rides and ride events (preserving users)
python manage.py init_data --rides
```

# What the Command Does
The init_data command performs the following functions:

1. User Creation: Creates sample users with different roles:

- 1 admin user
- 5 drivers
- 10 riders
2. Ride Creation: Creates 30 sample rides with:

- Random statuses ('pending', 'en-route', 'pickup', 'dropoff', 'completed', 'cancelled')
- Random pickup and dropoff coordinates
- Random pickup times within +/- 3 days from current time
- Assigned to random drivers and riders
3. Ride Event Creation: Creates 2-5 events for each ride with descriptions such as:

- "Ride requested"
- "Driver assigned"
- "Driver en-route to pickup"
- "Driver arrived at pickup location"
- "Ride started"
- "Approaching destination"
- "Ride completed"

### Stopping the Application

```bash
docker-compose down
```

To remove volumes (this will delete all data):
```bash
docker-compose down -v
```

## Table Structure

### User Table
- Custom User model extending Django's AbstractUser
- `role`: User role ('admin', 'driver', or 'rider')
- Standard Django user fields (username, email, password, etc.)

### Ride Table
- `id_ride`: INT (Primary key)
- `status`: VARCHAR (Ride status: 'pending', 'en-route', 'pickup', 'dropoff', 'completed', 'cancelled')
- `id_rider`: INT (Foreign key referencing User)
- `id_driver`: INT (Foreign key referencing User)
- `pickup_latitude`: FLOAT
- `pickup_longitude`: FLOAT
- `dropoff_latitude`: FLOAT
- `dropoff_longitude`: FLOAT
- `pickup_time`: DATETIME

### RideEvent Table
- `id_ride_event`: INT (Primary key)
- `id_ride`: INT (Foreign key referencing Ride)
- `description`: VARCHAR
- `created_at`: DATETIME

## JWT Authentication

This API uses JSON Web Token (JWT) authentication for secure access. JWT provides a stateless authentication mechanism that doesn't require storing session information on the server.

### JWT Endpoints

- `POST /api/token/` - Obtain JWT token pair (access and refresh tokens)
- `POST /api/token/refresh/` - Refresh access token
- `POST /api/token/verify/` - Verify token validity
- `POST /api/register/` - Register a new user and receive tokens

### How to Use JWT Authentication

1. **User Registration**: 
   ```bash
   curl -X POST http://localhost:8080/api/register/ \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser", "email":"test@example.com", "password":"secure_password", "role":"admin"}'
   ```

2. **Obtaining Tokens**:
    ![Token](https://github.com/karimjordanbuenaseda/Ride/blob/main/screenshots/token.jpg "Token")
   ```bash
   curl -X POST http://localhost:8080/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser", "password":"secure_password"}'
   ```
   Response will include access and refresh tokens:
   ```json
   {
     "refresh": "eyJ0eXAiOiJKV...long token here...",
     "access": "eyJ0eXAiOiJKV...long token here..."
   }
   ```

3. **Using the Access Token**:
   ![Ride Listing](https://github.com/karimjordanbuenaseda/Ride/blob/main/screenshots/ride_list.jpg "Ride Listing")
   ```bash
   curl -X GET http://localhost:8080/api/rides/ \
     -H "Authorization: Bearer eyJ0eXAiOiJKV...long token here..."

4. **Refreshing the Access Token**:
   ```bash
   curl -X POST http://localhost:8080/api/token/refresh/ \
     -H "Content-Type: application/json" \
     -d '{"refresh":"eyJ0eXAiOiJKV...long refresh token here..."}'
   ```

5. **Verifying Token Validity**:
   ```bash
   curl -X POST http://localhost:8080/api/token/verify/ \
     -H "Content-Type: application/json" \
     -d '{"token":"eyJ0eXAiOiJKV...long token here..."}'

### JWT Settings

The token settings can be configured in settings.py:

- Access token lifetime: 30 minutes - 'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
- Refresh token lifetime: 1 day - 'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
- Algorithm: HS256 - 'ALGORITHM': 'HS256',


## API Endpoints

### Authentication (JWT)
- `POST /api/token/` - Obtain JWT token pair
- `POST /api/token/refresh/` - Refresh access token
- `POST /api/token/verify/` - Verify token validity
- `POST /api/register/` - Register a new user and get tokens

### Rides
- `GET /api/rides/` - List all rides (with pagination)

### Filtering
The Ride List API supports filtering by:
- `status` - Filter rides by status
- `rider_email` - Filter rides by rider email

Example: `/api/rides/?status=en-route&rider_email=user@example.com`

### Sorting
The API supports sorting by:
- `pickup_time` - Sort rides by pickup time
- Distance to pickup - Sort by distance from a given GPS position

Example for sorting by pickup time: `/api/rides/?ordering=pickup_time` or `/api/rides/?ordering=-pickup_time` (descending)

Example for sorting by distance: `/api/rides/?latitude=37.7749&longitude=-122.4194`

## Pagination

The API uses page-based pagination with these parameters:
- `page`: The current page number
- `page_size`: Number of items per page (default: 10, max: 100)

Example: `/api/rides/?page=2&page_size=20`

## SQL Report Query for Trips > 1 Hour

The following SQL query returns the count of trips that took more than 1 hour from pickup to dropoff, grouped by month and driver:

```sql
WITH pickup_events AS (
    SELECT 
        r.id_ride,
        re.created_at AS pickup_time,
        CONCAT(u.first_name, ' ', LEFT(u.last_name, 1), '.') AS driver_name,
        TO_CHAR(re.created_at, 'YYYY-MM') AS month
    FROM 
        ride r
        JOIN user u ON r.id_driver = u.id_user
        JOIN ride_event re ON r.id_ride = re.id_ride
    WHERE 
        re.description = 'Status changed to pickup'
),
dropoff_events AS (
    SELECT 
        r.id_ride,
        re.created_at AS dropoff_time
    FROM 
        ride r
        JOIN ride_event re ON r.id_ride = re.id_ride
    WHERE 
        re.description = 'Status changed to dropoff'
),
trips_with_duration AS (
    SELECT 
        p.id_ride,
        p.driver_name,
        p.month,
        p.pickup_time,
        d.dropoff_time,
        EXTRACT(EPOCH FROM (d.dropoff_time - p.pickup_time))/3600 AS duration_hours
    FROM 
        pickup_events p
        JOIN dropoff_events d ON p.id_ride = d.id_ride
)
SELECT 
    month,
    driver_name AS "Driver",
    COUNT(*) AS "Count of Trips > 1 hr"
FROM 
    trips_with_duration
WHERE 
    duration_hours > 1
GROUP BY 
    month, driver_name
ORDER BY 
    month, driver_name;
```

This query:
1. First creates a CTE (Common Table Expression) for pickup events
2. Creates a second CTE for dropoff events 
3. Joins them to calculate the duration of each trip
4. Filters for trips longer than 1 hour
5. Groups by month and driver name
6. Returns the count of such trips


## DB Queries Count
![DB Queries](https://github.com/karimjordanbuenaseda/Ride/blob/main/screenshots/db_queries.jpg "DB Queries")

## License

This project is licensed under the MIT License - see the LICENSE file for details.