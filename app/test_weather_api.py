import requests

TOKEN = "615965:683b4619809f4"


def get_weather_data_test(city):

    try:
        resonse = requests.get(f'https://one-api.ir/weather/?token={TOKEN}&action=current&city={city}')
        data = resonse.json()
        return data['result']['weather'][0]['description']
    
    except Exception as e:
        print("Error:", e)


print(get_weather_data_test('tehran'))