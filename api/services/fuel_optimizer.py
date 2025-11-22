import math
import time
from api.models import FuelStation
from geopy.geocoders import Nominatim


class FuelOptimizer:
    MAX_RANGE_MILES = 500
    MPG = 10
    BUFFER_MILES = 50
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="fuel_optimizer_app")
        self.geocoded_cities = {}
    
    def optimize_fuel_stops(self, route_coords, distance_miles):
        num_stops = math.ceil(distance_miles / (self.MAX_RANGE_MILES - self.BUFFER_MILES))
        
        if num_stops == 0:
            return []
        
        segment_distance = distance_miles / num_stops
        fuel_stops = []
        
        for i in range(num_stops):
            target_distance = (i + 1) * segment_distance
            progress = target_distance / distance_miles
            coord_index = int(progress * (len(route_coords) - 1))
            target_coord = route_coords[min(coord_index, len(route_coords) - 1)]
            
            station = self._find_cheapest_station_near(target_coord, route_coords)
            
            if station:
                gallons_needed = segment_distance / self.MPG
                fuel_cost = float(station.retail_price) * gallons_needed
                
                fuel_stops.append({
                    'stop_number': i + 1,
                    'opis_truckstop_id': station.opis_truckstop_id,
                    'station_name': station.name,
                    'address': station.address,
                    'city': station.city,
                    'state': station.state,
                    'coordinates': {
                        'lat': station.latitude,
                        'lng': station.longitude
                    },
                    'distance_from_start_miles': round(target_distance, 2),
                    'fuel_price_per_gallon': float(station.retail_price),
                    'gallons_needed': round(gallons_needed, 2),
                    'fuel_cost': round(fuel_cost, 2)
                })
        
        return fuel_stops
    
    def _find_cheapest_station_near(self, target_coord, route_coords):
        lat, lng = target_coord
        radius = 1.0
        
        stations_query = FuelStation.objects.filter(
            latitude__range=(lat - radius, lat + radius),
            longitude__range=(lng - radius, lng + radius)
        ).order_by('retail_price')
        
        if not stations_query.exists():
            stations_query = FuelStation.objects.all().order_by('retail_price')
        
        stations = list(stations_query[:100])
        
        self._ensure_stations_geocoded(stations)
        
        geocoded_stations = [s for s in stations if s.geocoded]
        
        valid_stations = []
        for station in geocoded_stations:
            if self._is_near_route(station, route_coords):
                valid_stations.append(station)
        
        return valid_stations[0] if valid_stations else (geocoded_stations[0] if geocoded_stations else None)
    
    def _ensure_stations_geocoded(self, stations):
        cities_to_geocode = set()
        
        for station in stations:
            if not station.geocoded:
                city_key = f"{station.city}, {station.state}"
                cities_to_geocode.add((station.city, station.state, city_key))
        
        for city, state, city_key in cities_to_geocode:
            if city_key in self.geocoded_cities:
                lat, lng = self.geocoded_cities[city_key]
            else:
                try:
                    location = self.geolocator.geocode(f"{city}, {state}, USA", timeout=10)
                    if location:
                        lat, lng = location.latitude, location.longitude
                        self.geocoded_cities[city_key] = (lat, lng)
                        
                        FuelStation.objects.filter(
                            city=city, 
                            state=state, 
                            geocoded=False
                        ).update(
                            latitude=lat,
                            longitude=lng,
                            geocoded=True
                        )
                        
                        time.sleep(1.1)
                except:
                    pass
    
    def _is_near_route(self, station, route_coords, max_distance_miles=15):
        min_distance = float('inf')
        
        for coord in route_coords[::10]:
            distance = self._haversine_distance(
                station.latitude, station.longitude,
                coord[0], coord[1]
            )
            min_distance = min(min_distance, distance)
            
            if min_distance < max_distance_miles:
                return True
        
        return min_distance < max_distance_miles
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 3959
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
