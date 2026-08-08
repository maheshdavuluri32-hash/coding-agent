print("Enter your location (city, country): ")
location = input()
weather_api_url = f"http://wttr.in/{location}?format=3"
import requests
response = requests.get(weather_api_url)
if response.status_code == 200:
    print(response.text)