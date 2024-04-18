import os
import requests
from flask import render_template
from dotenv import load_dotenv
load_dotenv()
ZIPCODE_API_KEY = os.getenv("ZIPCODE_API_KEY")

api_req_url_1 = f'https://www.zipcodeapi.com/rest/{ZIPCODE_API_KEY}/radius.json/'

def get_zips_in_radius(zip_code, num_miles):
    '''
    Takes a zip code(integer) and num miles(integer)
    Returns a list of all zip codes in radius of num_miles from zip_code
    '''
    api_req_url_2 = f'{zip_code}/{num_miles}/miles?minimal'
    zip_code_api_url = api_req_url_1 + api_req_url_2
    response = requests.get(zip_code_api_url)

    if response.status_code != 200:
        return render_template('404.html', response=response)

    json_data = response.json()
    # Will return list of zip codes, if it can't find key of zip_codes, will return []
    zip_codes = json_data.get('zip_codes', [])

    return zip_codes
