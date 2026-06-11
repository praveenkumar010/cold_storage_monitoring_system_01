import requests

def fetch_external_data():
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=18.52&longitude=73.85&current_weather=true"
        )
        data = response.json()

        temp = data["current_weather"]["temperature"]

        return {
            "temperature": temp,
            "humidity": 70  
        }

    except Exception as e:
        print("Error fetching API:", e)
        return None