import requests
from typing import Optional, Dict, Any
import json

class HTTPRequest:
    """A wrapper class for making HTTP requests with error handling and context manager support."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
    
    def make_request(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request and parse the response.
        
        Args:
            url: The URL to request
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            headers: Optional headers dictionary
            params: Optional URL parameters
            data: Optional form data
            json_data: Optional JSON data
            timeout: Optional timeout override
            
        Returns:
            Dictionary containing:
                - success: Boolean indicating if request succeeded
                - status_code: HTTP status code
                - data: Parsed response data (if JSON) or text
                - error: Error message (if failed)
        """
        result = {
            'success': False,
            'status_code': None,
            'data': None,
            'error': None
        }
        
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=timeout or self.timeout
            )
            
            # Store status code
            result['status_code'] = response.status_code
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                result['data'] = response.json()
            except json.JSONDecodeError:
                # If not JSON, return text
                result['data'] = response.text
            
            result['success'] = True
            
        except requests.exceptions.Timeout:
            result['error'] = f'Request timed out after {timeout or self.timeout} seconds'
            
        except requests.exceptions.ConnectionError:
            result['error'] = 'Failed to connect to the server'
            
        except requests.exceptions.HTTPError as e:
            result['error'] = f'HTTP error occurred: {e}'
            try:
                result['data'] = response.json() # type: ignore
            except:
                result['data'] = response.text # type: ignore
                
        except requests.exceptions.RequestException as e:
            result['error'] = f'Request failed: {str(e)}'
            
        except Exception as e:
            result['error'] = f'Unexpected error: {str(e)}'
        
        return result
    
    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        return self.make_request(url, method='GET', **kwargs)
    
    def post(self, url: str, **kwargs) -> Dict[str, Any]:
        return self.make_request(url, method='POST', **kwargs)
    
    def put(self, url: str, **kwargs) -> Dict[str, Any]:
        return self.make_request(url, method='PUT', **kwargs)
    
    def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        return self.make_request(url, method='DELETE', **kwargs)
    
    def close(self):
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False  # Don't suppress exceptions
