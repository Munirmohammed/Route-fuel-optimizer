import time
from django.core.management.base import BaseCommand
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from api.models import FuelStation


class Command(BaseCommand):
    help = 'Geocode fuel stations'

    def handle(self, *args, **options):
        geolocator = Nominatim(user_agent="fuel_optimizer_app")
        stations = FuelStation.objects.filter(geocoded=False)
        total = stations.count()
        
        self.stdout.write(f'Geocoding {total} stations...')
        
        success = 0
        failed = 0
        
        for i, station in enumerate(stations, 1):
            try:
                location = None
                
                address = f"{station.city}, {station.state}, USA"
                location = geolocator.geocode(address, timeout=10)
                
                if location:
                    station.latitude = location.latitude
                    station.longitude = location.longitude
                    station.geocoded = True
                    station.save()
                    success += 1
                else:
                    failed += 1
                
                if i % 50 == 0:
                    self.stdout.write(f'Progress: {i}/{total} ({success} success, {failed} failed)')
                
                time.sleep(1.1)
                
            except (GeocoderTimedOut, GeocoderServiceError):
                failed += 1
                time.sleep(2)
            except Exception:
                failed += 1
        
        self.stdout.write(self.style.SUCCESS(f'Done! {success} geocoded, {failed} failed'))
