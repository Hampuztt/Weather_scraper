# Download the helper library from https://www.twilio.com/docs/python/install
from dataclasses import dataclass
from datetime import datetime, time
import os
from twilio.rest import Client

import requests
from bs4 import BeautifulSoup

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

WEATHER_URL = "https://weather.com/weather/hourbyhour/l/23a80cf6719e8f04ff119eb72e2e196bf3c66cbcc60d20b86cd29bb9f2309695"

html_ = {
    "uv_index": 'span[data-testid="UVIndexValue"].DetailsTable--value--2YD0-',
    "hour_summary": "a",
}


@dataclass
class WeatherData:
    date: datetime
    uv: str
    temperature_celsius: float
    weather: str

    def __str__(self):
        return (
            f"Weather Data:\n"
            f"Time: {self.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"UV: {self.uv}\n"
            f"Temperature: {self.temperature_celsius}°C\n"
            f"Weather: {self.weather}"
        )


def get_uv_index(url):
    todays_weather = []
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the webpage")
        exit()
    soup = BeautifulSoup(response.text, "html.parser")

    hour_summaries = soup.find_all("div", {"data-testid": "DetailsSummary"})
    uvs = soup.select('span[data-testid="UVIndexValue"].DetailsTable--value--2YD0-')
    for div, uv in zip(hour_summaries, uvs):
        daypart_name = div.find("h3", {"data-testid": "daypartName"}).text
        date_today = datetime.today().date()
        time_part = datetime.strptime(daypart_name, "%I %p").time()

        # Combine the date part and the time part into a single datetime object
        date = datetime.combine(date_today, time_part)
        temperature: str = (
            div.find("div", {"data-testid": "detailsTemperature"})
            .find("span", {"data-testid": "TemperatureValue"})
            .text
        )
        temperature_far = int(
            "".join([digit for digit in temperature if digit.isdigit()])
        )
        temperature_celsius = round((temperature_far - 32) * 5 / 9, 1)
        weather_condition = div.find("div", {"data-testid": "wxIcon"}).find("span").text

        weather = WeatherData(
            date=date,
            uv=uv.text,
            temperature_celsius=temperature_celsius,
            weather=weather_condition,
        )

        todays_weather.append(weather)
        print(weather)
        print()
        END_OF_DAY_TIME = time(22, 0)
        if time_part >= END_OF_DAY_TIME:
            print("stop looking divs")
            break

    #
    # uv_element = soup.select_one(
    #     'span[data-testid="UVIndexValue"].DetailsTable--value--2YD0-'
    # )
    # if uv_element:
    #     return uv_element.text.strip()
    return todays_weather


def sendMessage(to: str, msg: str):
    client = Client(account_sid, auth_token)
    message = client.messages.create(body=msg, from_="whatsapp:+14155238886", to=to)
    print(message.sid)


if __name__ == "__main__":
    uvs = get_uv_index(WEATHER_URL)
    print(uvs)
