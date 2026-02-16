import requests
import time
import json
import sys
import os

base_url = 'https://nominatim.openstreetmap.org/search'

cities = ["Mont Saint Michel", "St Malo", "Bayeux", "Le Havre", "Rouen", "Paris", 
          "Amiens", "Lille", "Strasbourg", "Chateau du Haut Koenigsbourg", "Colmar", 
          "Eguisheim", "Besancon", "Dijon", "Annecy", "Grenoble", "Lyon", 
          "Gorges du Verdon", "Bormes les Mimosas", "Cassis", "Marseille", 
          "Aix en Provence", "Avignon", "Uzes", "Nimes", "Aigues Mortes", 
          "Saintes Maries de la mer", "Collioure", "Carcassonne", "Ariege", 
          "Toulouse", "Montauban", "Biarritz", "Bayonne", "La Rochelle"]

coordinates = {}

headers = {
    'User-Agent': 'KayakProject/1.0 (emailfortheproject@gmail.com)'
}


for city in cities:
    try:
        params = {'q': f"{city}, France", 'format': 'json', 'limit': 1}
        
        response = requests.get(base_url, params=params, headers=headers)
        
        response.raise_for_status() 
        
        data = response.json()
        
        if data:  
            coordinates[city] = {
                'lat': float(data[0]['lat']),
                'lon': float(data[0]['lon'])
            }
            print(f"{city}: {coordinates[city]}")
        else:
            coordinates[city] = None
            print(f"No results for {city}")
            
    except Exception as e:
        print(f"Error fetching {city}: {e}", file=sys.stderr)
        coordinates[city] = None  
    
    time.sleep(1)


with open('coordinates.json', 'w') as f:
    json.dump(coordinates, f, indent=4)

print(f"\nCoordinates saved to coordinates.json in {os.getcwd()}")