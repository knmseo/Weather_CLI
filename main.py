import os

import httpx
from dotenv import load_dotenv


def main():
    load_dotenv()
    api_key = os.environ.get("OWM_API_KEY")
    if api_key is None:
        print("Key not found. check your .env folder and variable name")
    else:
        print(f"Key loaded, length: {len(api_key)}, starts with {api_key[:3]}...")

    ProgramRunning = True
    while ProgramRunning:
        TargetCity = input("Which city's weather should we get?:")

        try:
            response = httpx.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": TargetCity, "units": "metric", "appid": api_key},
            )
        except httpx.RequestError:
            print("There is a problem with your network!")
            continue
        else:
            if response.status_code == 200:
                data = response.json()
            elif response.status_code == 401:
                print("Bad API Key!")
                continue
            elif response.status_code == 404:
                print("Invalid city name!")
                continue
            else:
                print("Error")
                continue

        print(
            f"The temperature in {TargetCity} is {data['main']['temp']} and feels like {data['main']['feels_like']}. The weather is {data['weather'][0]['main']} with {data['weather'][0]['description']} "
        )
        UserResponse = input("Do you want to query another city? (y/n)")
        if UserResponse == "y":
            ProgramRunning = True
        else:
            ProgramRunning = False


if __name__ == "__main__":
    main()
