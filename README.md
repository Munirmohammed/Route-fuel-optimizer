# Fuel Optimizer API

Django REST API that calculates optimal fuel stops for road trips within the USA based on fuel prices and vehicle range.

## Features

- Finds cost-effective fuel stops along any US route
- Uses real fuel price data from 6,900+ truck stops
- Generates interactive maps with route and fuel stops
- Fast response times (2-5 seconds)
- Calculates total trip cost based on 10 MPG
- Smart caching for repeated routes
- No API keys required - completely free to use

## Technology Stack

- **Backend:** Django 5.1.6, Django REST Framework
- **Database:** PostgreSQL with spatial indexes
- **Routing:** OSRM (Open Source Routing Machine) - free, no API key
- **Geocoding:** Nominatim (OpenStreetMap) - free, no API key
- **Maps:** Folium for interactive HTML maps
- **Caching:** Django cache framework

## Setup

### 1. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure environment variables in `.env`:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=fuel_optimizer_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
BASE_URL=http://127.0.0.1:8000
```

### 3. Create database:
```bash
psql -U postgres -c "CREATE DATABASE fuel_optimizer_db;"
```

### 4. Run migrations:
```bash
python manage.py migrate
```

### 5. Import fuel data:
```bash
python manage.py import_fuel_data
```

### 6. Run server:
```bash
python manage.py runserver
```

## Performance

- **First request:** 3-10 seconds (geocodes cities on-demand)
- **Cached requests:** 2-3 seconds (uses stored coordinates)
- **API calls:** Only 1 routing API call per unique route
- **Database:** 6,967 fuel stations with optimized indexes

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

## How It Works

1. **Route Calculation:** Uses OSRM to get the optimal driving route
2. **Fuel Stop Planning:** Divides route into 450-mile segments (500-mile range with safety buffer)
3. **Station Search:** Finds cheapest stations within 30-50 miles of the route
4. **Cost Calculation:** Computes fuel needed (distance ÷ 10 MPG) × price per gallon
5. **Map Generation:** Creates interactive map with route and fuel stops
6. **Smart Caching:** Stores routes and geocoded cities for fast repeated requests

## Project Structure

```
fuel_optimizer/
├── api/
│   ├── models.py                 # FuelStation model
│   ├── views.py                  # API endpoint
│   ├── serializers.py            # Request/response serializers
│   ├── services/
│   │   ├── osrm_route_service.py    # OSRM routing integration
│   │   ├── fuel_optimizer.py        # Fuel stop optimization algorithm
│   │   └── map_generator.py         # Folium map generation
│   └── management/commands/
│       └── import_fuel_data.py      # CSV import command
├── data/
│   └── fuel-prices-for-be-assessment.csv
├── static/maps/                  # Generated map files
└── requirements.txt
```

## Notes

- Stations are geocoded lazily (on first use) to avoid 2-hour setup time
- Geocoded coordinates are cached in the database permanently
- The algorithm prioritizes price over distance for cost optimization
- Duplicate stations are automatically filtered out
