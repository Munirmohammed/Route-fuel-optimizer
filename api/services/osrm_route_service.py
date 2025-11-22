import requests
from django.core.cache import cache
import polyline


class OSRMRouteService:
    BASE_URL = "http://router.project-osrm.org/route/v1/driving"
    
    def get_route(self, start_location, end_location):
        cache_key = f"route_{start_location.replace(' ', '_').replace(',', '')}_{end_location.replace(' ', '_').replace(',', '')}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        start_coords = self._geocode_location(start_location)
        end_coords = self._geocode_location(end_location)
        
        url = f"{self.BASE_URL}/{start_coords['lng']},{start_coords['lat']};{end_coords['lng']},{end_coords['lat']}"
        
        params = {
            'overview': 'full',
            'geometries': 'polyline'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        route_data = self._parse_route(data)
        
        cache.set(cache_key, route_data, 3600)
        return route_data
    
    def _geocode_location(self, location):
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="fuel_optimizer", timeout=15)
        result = geolocator.geocode(location + ", USA", timeout=15)
        if not result:
            raise ValueError(f"Could not geocode location: {location}")
        return {'lat': result.latitude, 'lng': result.longitude}
    
    def _parse_route(self, data):
        if data['code'] != 'Ok':
            raise ValueError(f"Routing failed: {data.get('message', 'Unknown error')}")
        
        route = data['routes'][0]
        geometry = route['geometry']
        
        coords = polyline.decode(geometry)
        
        distance_meters = route['distance']
        duration_seconds = route['duration']
        
        return {
            'coordinates': coords,
            'distance_miles': distance_meters * 0.000621371,
            'duration_hours': duration_seconds / 3600,
            'polyline': geometry
        }
