import json
import requests

response = requests.get('https://maps.googleapis.com/maps/api/directions/json?origin=40.7528,-73.9765&destination=40.750779,-73.993519&key=APIKEY&mode=bicycling')
json_data = json.loads(response.text)


with open('directions.json', 'w') as fp:
    json.dump(json_data, fp)
