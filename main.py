import os
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

BaseURL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherApplicationError(Exception):
    "Base Error class for all errors in this weather application"


class InvalidUserInputError(WeatherApplicationError):
    "Base Error class for all errors related to user input"


class NetworkError(WeatherApplicationError):
    "Errors related to API or the user's network"


class InvalidAPIKeyError(WeatherApplicationError):
    "Invalid API key under .env"


class InvalidCityCodeError(InvalidUserInputError):
    "Provided City code is invalid"


class UnexpectedResponseError(WeatherApplicationError):
    "The application returned an error we could not understand"


@dataclass
class WeatherReport:
    city: str
    temp_c: float
    feels_like_c: float
    condition: str
    description: str


def LoadAPIKey() -> str:
    load_dotenv()
    api_key = os.environ.get("OWM_API_KEY")
    if api_key is None:
        raise InvalidAPIKeyError
    else:
        print(f"Key loaded, length: {len(api_key)}, starts with {api_key[:3]}...")
    return api_key


def FetchWeatherReport(
    TargetCity: str, APIKey, *, client: httpx.Client | None = None
) -> WeatherReport:
    owns_client = client is None  # Check whether this function created a
    client = client or httpx.Client(timeout=10.0)
    try:
        response = client.get(
            BaseURL,
            params={"q": TargetCity, "units": "metric", "appid": APIKey},
        )
    except httpx.RequestError as exc:
        raise NetworkError("Could not reach the weather API") from exc
    finally:
        if owns_client:
            client.close()
    if response.status_code == 200:
        try:
            data = response.json()
            return WeatherReport(
                city=TargetCity,
                temp_c=data["main"]["temp"],
                feels_like_c=data["main"]["feels_like"],
                condition=data["weather"][0]["main"],
                description=data["weather"][0]["description"],
            )
        except (ValueError, KeyError, IndexError) as exc:
            raise UnexpectedResponseError(
                "Weather API returned a response we couldn't understand"
            ) from exc

    elif response.status_code == 401:
        raise InvalidAPIKeyError

    elif response.status_code == 404:
        raise InvalidCityCodeError(f"No city found for {TargetCity}")
    else:
        raise UnexpectedResponseError(
            f"Weather API returned an unexpected response: {response.status_code}"
        )


def FormatOutputResponse(report: WeatherReport) -> str:
    return (
        f"The temperature in {report.city} is {report.temp_c}\u00b0C "
        f"and feels like {report.feels_like_c}\u00b0C. "
        f"The weather is {report.condition} with {report.description}."
    )


def run(APIKey: str) -> None:
    with httpx.Client(timeout=10.0) as client:
        while True:
            TargetCity = input("Which city's weather should we get?:")
            if not TargetCity:
                continue

            try:
                Report = FetchWeatherReport(TargetCity, APIKey, client=client)
            except NetworkError:
                print("There was something wrong with your network!")
            except InvalidCityCodeError:
                print(f"Your input city code({TargetCity}) was invalid!")
            except InvalidAPIKeyError:
                print("Your API Key was invalid!")
            except UnexpectedResponseError as exc:
                print(f"There was an unexpected error: {exc}")
            else:
                print(FormatOutputResponse(Report))

            UserResponse = (
                input("Do you want to query another city? (y/n)").strip().lower()
            )

            if UserResponse != "y":
                break


def main() -> None:
    run(LoadAPIKey())


if __name__ == "__main__":
    main()
