import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import FuelStation


class Command(BaseCommand):
    help = 'Import fuel station data from CSV'

    def handle(self, *args, **options):
        csv_path = settings.BASE_DIR / 'data' / 'fuel-prices-for-be-assessment.csv'
        
        self.stdout.write('Clearing existing data...')
        FuelStation.objects.all().delete()
        
        self.stdout.write('Loading CSV data...')
        stations_data = {}
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                opis_id = int(row['OPIS Truckstop ID'])
                price = float(row['Retail Price'])
                state = row['State'].strip()
                
                if len(state) > 2:
                    continue
                
                key = (opis_id, row['Truckstop Name'], row['City'])
                
                if key not in stations_data or price < stations_data[key]['price']:
                    stations_data[key] = {
                        'opis_truckstop_id': opis_id,
                        'name': row['Truckstop Name'],
                        'address': row['Address'],
                        'city': row['City'],
                        'state': state,
                        'rack_id': int(row['Rack ID']),
                        'retail_price': price,
                    }
        
        self.stdout.write(f'Creating {len(stations_data)} unique stations...')
        stations = [FuelStation(**data) for data in stations_data.values()]
        FuelStation.objects.bulk_create(stations, batch_size=500)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(stations)} fuel stations'))
