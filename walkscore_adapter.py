
import requests
import re
from pydantic import BaseModel, Field, ValidationError
from urllib.parse import urlencode

WALKSCORE_API_ENPOINT = 'https://api.walkscore.com/score'

class TransitData(BaseModel):
    description: str
    summary: str
    score: int = Field(ge=0, le=100) 


class BikeData(BaseModel):
    description: str
    score: int = Field(ge=0, le=100)


class WalkScoreData(BaseModel):
    status: int
    walkscore: int = Field(ge=0, le=100)
    description: str
    updated: str
    logo_url: str
    more_info_icon: str
    more_info_link: str
    ws_link: str
    help_link: str
    snapped_lat: float
    snapped_lon: float
    transit: TransitData | None = None
    bike: BikeData | None = None
    
    class Config:
        # Allow extra fields that aren't defined
        extra = 'allow'

def fetch_data(url: str):
    
    # Make a GET request
    response = requests.get(url)

    # Check the status code
    if response.status_code == 200:
        # Access the response content (e.g., JSON)
        data = response.json()
        return data

    else:
        raise Exception('API request failed. Status code: ' + str(response.status_code))

def parse_walkscore(data: dict) -> WalkScoreData:
        try:
            return WalkScoreData.model_validate(data)
        except ValidationError as e:
            print(f"Could not parse WalkScoreResponse: {e}")
            raise e

def get_walkscore_data(
    lat: float,
    lon: float,
    api_key: str
) -> WalkScoreData : 

    params = {
        'lon': str(lon),
        'lat': str(lat),
        'format': 'json',
        'transit': 1,
        'bike': 1,
        'wsapikey': api_key
    }

    query_params = urlencode(params)

    response = fetch_data( WALKSCORE_API_ENPOINT + '?' + query_params)
    walkscore_response = parse_walkscore(response)
    return walkscore_response

def get_walkscore(
    lat: float,
    lon: float,
    api_key: str
) -> int : 
    walkscore_data = get_walkscore_data(lat, lon, api_key)
    return walkscore_data.walkscore


def get_file_name_and_path (target_file: str, no_extension = False):
    file_path_elements = re.split(r'[//\\]', target_file)
    out_name = file_path_elements.pop(-1)
    out_path = '/'.join(file_path_elements) 

    if no_extension: 
        out_name = out_name.split('.')[0]

    return [out_name, out_path]

if __name__ == "__main__":

    name, path = get_file_name_and_path('C:test\\ga_tech.shp')
    print(name)
