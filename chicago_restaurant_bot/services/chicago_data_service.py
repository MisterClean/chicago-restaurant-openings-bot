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
        headers = {}
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
        
        query = f"""
            SELECT 
                business_name, 
                address,
                zip_code,
                license_description,
                business_activity,
                square_footage,
                application_type,
                application_created_date,
                ward
            WHERE 
                license_description LIKE '%RETAIL FOOD%'
                AND application_type = 'ISSUE'
                AND application_created_date > '{since.isoformat()}'
            ORDER BY application_created_date DESC
        """
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self._build_headers(),
                params={"$query": query}
            )
            response.raise_for_status()
            
            return [
                Restaurant(
                    name=r.get('business_name'),
                    address=r.get('address'),
                    zip_code=r.get('zip_code'),
                    license_description=r.get('license_description'),
                    business_activity=r.get('business_activity'),
                    square_footage=r.get('square_footage'),
                    application_date=datetime.fromisoformat(r.get('application_created_date')),
                    ward=r.get('ward')
                )
                for r in response.json()
            ]
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching data from Chicago Data Portal: {e}")
            return []
