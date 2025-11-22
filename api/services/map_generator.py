import folium
import polyline as polyline_lib
import os
from django.conf import settings
from decouple import config
import uuid


class MapGenerator:
    
    def generate_map(self, route_data, fuel_stops, start_location, end_location):
        if not route_data['coordinates']:
            return None
        
        center_lat = sum(c[0] for c in route_data['coordinates']) / len(route_data['coordinates'])
        center_lng = sum(c[1] for c in route_data['coordinates']) / len(route_data['coordinates'])
        
        m = folium.Map(location=[center_lat, center_lng], zoom_start=6)
        
        folium.PolyLine(
            route_data['coordinates'],
            color='blue',
            weight=4,
            opacity=0.7
        ).add_to(m)
        
        if route_data['coordinates']:
            start_coord = route_data['coordinates'][0]
            folium.Marker(
                start_coord,
                popup=f"Start: {start_location}",
                icon=folium.Icon(color='green', icon='play')
            ).add_to(m)
            
            end_coord = route_data['coordinates'][-1]
            folium.Marker(
                end_coord,
                popup=f"End: {end_location}",
                icon=folium.Icon(color='red', icon='stop')
            ).add_to(m)
        
        for stop in fuel_stops:
            coords = stop['coordinates']
            popup_text = f"""
                <b>{stop['station_name']}</b><br>
                {stop['city']}, {stop['state']}<br>
                Price: ${stop['fuel_price_per_gallon']}/gal<br>
                Cost: ${stop['fuel_cost']}
            """
            
            folium.Marker(
                [coords['lat'], coords['lng']],
                popup=popup_text,
                icon=folium.Icon(color='orange', icon='gas-pump', prefix='fa')
            ).add_to(m)
        
        maps_dir = os.path.join(settings.BASE_DIR, 'static', 'maps')
        os.makedirs(maps_dir, exist_ok=True)
        
        map_filename = f"route_{uuid.uuid4().hex[:8]}.html"
        map_path = os.path.join(maps_dir, map_filename)
        m.save(map_path)
        
        base_url = config('BASE_URL', default='http://127.0.0.1:8000')
        return f"{base_url}/static/maps/{map_filename}"
