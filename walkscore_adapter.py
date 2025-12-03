
from pydantic import BaseModel
from .request import HTTPRequest
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


def parse_walkscore(data: dict) -> WalkScoreData:
        try:
            return WalkScoreData.model_validate(data)
        except ValidationError as e:
            print(f"Could not parse WalkScoreResponse: {e}")
            raise

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

    with HTTPRequest() as request:
        response = request.get( WALKSCORE_API_ENPOINT + '?' + query_params)
        walkscore_response = parse_walkscore(response['data'])
        return walkscore_response
    
def get_walkscore(
    lat: float,
    lon: float,
    api_key: str
) -> int : 
    walkscore_data = get_walkscore_data(lat, lon, api_key)
    return walkscore_data.walkscore

if __name__ == "__main__":

    walkscore = get_walkscore(33.78603788916061, -84.34652698910072, '40b48aa9dd8220062069e30f5233481b')
    print(walkscore)

