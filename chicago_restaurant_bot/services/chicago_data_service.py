import requests
from datetime import datetime
from typing import List, Optional
import logging
from ..models.restaurant import Restaurant


class ChicagoDataService:
    """Service for interacting with the Chicago Data Portal API."""
    
    def __init__(self, app_token: Optional[str] = None):
        self.base_url = "https://data.cityofchicago.org/resource/"
        self.app_token = app_token
        self.logger = logging.getLogger(__name__)

    def _build_headers(self) -> dict:
        """Build request headers including app token if available."""
        headers = {
            'Accept': 'application/json'
        }
        if self.app_token:
            headers["X-App-Token"] = self.app_token
        return headers

    def get_new_restaurants(self, since: datetime) -> List[Restaurant]:
        """
        Fetch newly licensed restaurants from Chicago Data Portal.
        
        Args:
            since: datetime to fetch restaurants after
            
        Returns:
            List of Restaurant objects
        """
        endpoint = "xqx5-8hwx.json"  # Business licenses endpoint
        
        # Use the correct column names from the API
        params = {
            "$select": "legal_name,address,zip_code,license_description,business_activity,square_footage,application_type,application_created_date,ward",
            "$where": f"license_description like '%RETAIL FOOD%' AND application_type='ISSUE' AND application_created_date > '{since.strftime('%Y-%m-%d')}'",
            "$order": "application_created_date DESC",
            "$limit": "10"  # Limit to 10 results for testing
        }
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self._build_headers(),
                params=params
            )
            
            # Log the actual URL being requested
            self.logger.info(f"Requesting URL: {response.url}")
            
            response.raise_for_status()
            data = response.json()
            
            # Log the number of results
            self.logger.info(f"Found {len(data)} results")
            
            return [
                Restaurant(
                    name=r.get('legal_name'),  # Changed from business_name to legal_name
                    address=r.get('address'),
                    zip_code=r.get('zip_code'),
                    license_description=r.get('license_description'),
                    business_activity=r.get('business_activity'),
                    square_footage=r.get('square_footage'),
                    application_date=datetime.fromisoformat(r.get('application_created_date')),
                    ward=r.get('ward')
                )
                for r in data
            ]
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching data from Chicago Data Portal: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                self.logger.error(f"Response content: {e.response.text}")
            return []
