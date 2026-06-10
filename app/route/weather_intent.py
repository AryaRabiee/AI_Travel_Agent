import requests
from llm.log import logger
from state.memory import offline_weather
import os

weather_token = os.getenv("WEATHER_TOKEN")

def get_weather_data(city):

    try:
        resonse = requests.get(f'https://one-api.ir/weather/?token={weather_token}&action=current&city={city}')
        data = resonse.json()
        return data['result']['weather'][0]['description']
    
    except Exception as e:
        logger.error("ERROR %s" , e)
        return offline_weather.get(
            city,
            "متاسفانه فعلا اطلاعات آب و هوا برای این شهر در دسترس نیست"
        )
