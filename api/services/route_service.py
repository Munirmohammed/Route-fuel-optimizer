import requests
from django.core.cache import cache
import polyline


class RouteService:
    BASE_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
    
    def __init__(self, api_key=None):
        self.api_key = api_key or "5b3ce3597851110001cf6248a1b2c8e8c8e04e5f8b0e8f8e8e8e8e8e"
    
    def get_route(self, start_location, end_location):
        cache_key = f"route_{start_location}_{end_location}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        start_coords = self._geocode_location(start_location)
        end_coords = self._geocode_location(end_location)
        
        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        
        body = {
            'coordinates': [
                [start_coords['lng'], start_coords['lat']],
                [end_coords['lng'], end_coords['lat']]
            ]
        }
        
        response = requests.post(self.BASE_URL, json=body, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        route_data = self._parse_route(data)
        
        cache.set(cache_key, route_data, 3600)
        return route_data
    
    def _geocode_location(self, location):
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="fuel_optimizer")
        result = geolocator.geocode(location + ", USA")
        if not result:
            raise ValueError(f"Could not geocode location: {location}")
        return {'lat': result.latitude, 'lng': result.longitude}
    
    def _parse_route(self, data):
        route = data['routes'][0]
        geometry = route['geometry']
        
        coords = polyline.decode(geometry)
        
        distance_meters = route['summary']['distance']
        duration_seconds = route['summary']['duration']
        
        return {
            'coordinates': coords,
            'distance_miles': distance_meters * 0.000621371,
            'duration_hours': duration_seconds / 3600,
            'polyline': geometry
        }
