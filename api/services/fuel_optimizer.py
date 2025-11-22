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
            num_stops = 1
        
        segment_distance = distance_miles / num_stops
        fuel_stops = []
        used_station_ids = set()
        used_station_keys = set()
        
        for i in range(num_stops):
            target_distance = (i + 1) * segment_distance
            progress = target_distance / distance_miles
            coord_index = int(progress * (len(route_coords) - 1))
            target_coord = route_coords[min(coord_index, len(route_coords) - 1)]
            
            station = self._find_cheapest_station_near(target_coord, route_coords, used_station_ids)
            
            if not station:
                station = self._find_any_station_near(target_coord, used_station_ids, route_coords)
            
            if station:
                station_key = (station.opis_truckstop_id, station.city.strip(), station.state)
                if station_key in used_station_keys:
                    continue
                
                used_station_ids.add(station.id)
                used_station_keys.add(station_key)
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
    
    def _find_cheapest_station_near(self, target_coord, route_coords, used_stations=None):
        if used_stations is None:
            used_stations = set()
        
        lat, lng = target_coord
        
        for search_radius in [0.5, 1.0, 2.0, 3.0, 5.0]:
            stations_query = FuelStation.objects.filter(
                latitude__range=(lat - search_radius, lat + search_radius),
                longitude__range=(lng - search_radius, lng + search_radius)
            ).order_by('retail_price')
            
            if used_stations:
                stations_query = stations_query.exclude(id__in=used_stations)
            
            stations = list(stations_query[:300])
            
            if not stations:
                continue
            
            self._ensure_stations_geocoded(stations)
            
            geocoded_stations = [s for s in stations if s.geocoded]
            
            stations_with_distance = []
            for station in geocoded_stations:
                min_dist = self._min_distance_to_route(station, route_coords)
                if min_dist < 50:
                    stations_with_distance.append((station, min_dist))
            
            if stations_with_distance:
                stations_with_distance.sort(key=lambda x: (x[0].retail_price, x[1]))
                return stations_with_distance[0][0]
        
        return None
    
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
    
    def _find_any_station_near(self, target_coord, used_stations, route_coords):
        lat, lng = target_coord
        
        for search_radius in [1.0, 2.0, 3.0, 5.0]:
            stations_query = FuelStation.objects.filter(
                latitude__range=(lat - search_radius, lat + search_radius),
                longitude__range=(lng - search_radius, lng + search_radius)
            ).order_by('retail_price')
            
            if used_stations:
                stations_query = stations_query.exclude(id__in=used_stations)
            
            stations = list(stations_query[:200])
            
            if not stations:
                continue
            
            self._ensure_stations_geocoded(stations)
            
            geocoded_stations = [s for s in stations if s.geocoded]
            
            for station in geocoded_stations:
                dist = self._min_distance_to_route(station, route_coords)
                if dist < 100:
                    return station
        
        return None
    
    def _min_distance_to_route(self, station, route_coords):
        min_distance = float('inf')
        
        for coord in route_coords[::3]:
            distance = self._haversine_distance(
                station.latitude, station.longitude,
                coord[0], coord[1]
            )
            min_distance = min(min_distance, distance)
            
            if min_distance < 3:
                return min_distance
        
        return min_distance
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 3959
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
