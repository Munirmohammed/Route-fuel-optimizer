# Fuel Optimizer API

Django REST API that calculates optimal fuel stops for road trips within the USA based on fuel prices and vehicle range.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=fuel_optimizer_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

3. Create database:
```bash
psql -U postgres -c "CREATE DATABASE fuel_optimizer_db;"
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Import fuel data:
```bash
python manage.py import_fuel_data
```

6. Geocode stations (takes ~2 hours):
```bash
python manage.py geocode_stations
```

7. Run server:
```bash
python manage.py runserver
```

## API Endpoint

**POST** `/api/route-optimizer/`

### Request:
```json
{
  "start_location": "New York, NY",
  "end_location": "Los Angeles, CA"
}
```

### Response:
```json
{
  "route": {
    "total_distance_miles": 2789.5,
    "total_duration_hours": 41.2,
    "start_location": "New York, NY",
    "end_location": "Los Angeles, CA"
  },
  "fuel_stops": [
    {
      "stop_number": 1,
      "station_name": "PILOT TRAVEL CENTER #24",
      "city": "Monroe",
      "state": "MI",
      "fuel_price_per_gallon": 3.25,
      "fuel_cost": 146.21
    }
  ],
  "summary": {
    "total_fuel_stops": 6,
    "total_gallons_needed": 278.95,
    "total_fuel_cost": 965.50
  },
  "map_html": "<html>...</html>",
  "performance": {
    "external_api_calls": 1,
    "response_time_seconds": 2.3
  }
}
```

## Features

- Optimizes fuel stops based on cost
- 500-mile max range, 10 MPG vehicle
- Interactive map visualization
- Fast response time (< 5 seconds)
- Caching for improved performance
