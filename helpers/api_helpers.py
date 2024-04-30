import os
import requests
from dotenv import load_dotenv

load_dotenv()

ZIPCODE_API_KEY = os.getenv("ZIPCODE_API_KEY")
BASE_URL = f'https://www.zipcodeapi.com/rest/{ZIPCODE_API_KEY}/radius.json/'

def get_zips_in_radius(zip_code, num_miles):
    '''
    Takes a zip code(integer) and num miles(integer)
    Returns a list of all zip codes in radius of num_miles from zip_code
    '''
    try:
        api_query = f'{zip_code}/{num_miles}/miles?minimal'
        api_url = BASE_URL + api_query
        response = requests.get(api_url)

        if response.status_code != 200:
            print("Failed to fetch data: ", response.status_code)
            return []

        json_data = response.json()

        # Will return list of zip codes, if it can't find key of zip_codes, will return []
        zip_codes = json_data.get('zip_codes', [])
        return zip_codes

    except requests.RequestException as e:
        # Handles exceptions that are thrown by the requests library
        print("An error occurred during the API request:", str(e))
        return []

    except ValueError as e:
        # Handles JSON decoding errors
        print("JSON decode error:", str(e))
        return []

    except Exception as e:
        # An unexpected exception case, should ideally be logged and handled accordingly
        print("An unexpected error occurred:", str(e))
        return []

