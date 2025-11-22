import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RouteOptimizerRequestSerializer
from .services.osrm_route_service import OSRMRouteService
from .services.fuel_optimizer import FuelOptimizer
from .services.map_generator import MapGenerator


class RouteOptimizerView(APIView):
    
    def post(self, request):
        start_time = time.time()
        
        serializer = RouteOptimizerRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        start_location = serializer.validated_data['start_location']
        end_location = serializer.validated_data['end_location']
        
        try:
            route_service = OSRMRouteService()
            route_data = route_service.get_route(start_location, end_location)
            
            optimizer = FuelOptimizer()
            fuel_stops = optimizer.optimize_fuel_stops(
                route_data['coordinates'],
                route_data['distance_miles']
            )
            
            total_fuel_cost = sum(stop['fuel_cost'] for stop in fuel_stops)
            total_gallons = sum(stop['gallons_needed'] for stop in fuel_stops)
            avg_price = total_fuel_cost / total_gallons if total_gallons > 0 else 0
            
            map_gen = MapGenerator()
            map_html = map_gen.generate_map(route_data, fuel_stops, start_location, end_location)
            
            response_time = time.time() - start_time
            
            response_data = {
                'route': {
                    'total_distance_miles': round(route_data['distance_miles'], 2),
                    'total_duration_hours': round(route_data['duration_hours'], 2),
                    'start_location': start_location,
                    'end_location': end_location
                },
                'fuel_stops': fuel_stops,
                'summary': {
                    'total_fuel_stops': len(fuel_stops),
                    'total_gallons_needed': round(total_gallons, 2),
                    'total_fuel_cost': round(total_fuel_cost, 2),
                    'average_price_per_gallon': round(avg_price, 2)
                },
                'map_html': map_html,
                'performance': {
                    'external_api_calls': 1,
                    'response_time_seconds': round(response_time, 2)
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
