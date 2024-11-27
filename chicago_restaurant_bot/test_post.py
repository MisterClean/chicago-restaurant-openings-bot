from datetime import datetime, timedelta
from .models.restaurant import Restaurant
from .services.chicago_data_service import ChicagoDataService
from .config import Config
import yaml
import os
from dotenv import load_dotenv


def create_sample_restaurant() -> Restaurant:
    """Create a sample restaurant with example data."""
    return Restaurant(
        name="Chicago Deep Dish Paradise",
        address="123 W Madison St",
        zip_code="60601",
        license_description="RETAIL FOOD ESTABLISHMENT",
        business_activity="Restaurant with bar and outdoor patio",
        square_footage="2,500",
        application_date=datetime.now(),
        ward="42"
    )

def preview_restaurant(restaurant: Restaurant, config: Config):
    """Display a preview for a single restaurant."""
    print("\nRestaurant Details:")
    print("-" * 50)
    print(f"Name: {restaurant.name}")
    print(f"Address: {restaurant.address}")
    print(f"ZIP: {restaurant.zip_code}")
    print(f"License: {restaurant.license_description}")
    print(f"Activity: {restaurant.business_activity}")
    print(f"Size: {restaurant.square_footage} sq ft")
    print(f"Ward: {restaurant.ward}")
    print(f"Application Date: {restaurant.application_date}")
    print("\nFormatted Post Preview:")
    print("-" * 50)
    
    # Show formatted announcement
    announcement = restaurant.format_announcement(config)
    print(announcement)
    
    # Show character count (useful for platform limits)
    print("\nCharacter Count:", len(announcement))
    
    # Show if post would pass filters
    if restaurant.passes_filters(config.filters):
        print("Status: Would be posted ✅")
    else:
        print("Status: Would be filtered out ❌")
    print("-" * 50)

def main():
    """
    Test the post formatting with real restaurant data from the API.
    Loads actual config but doesn't post to Bluesky.
    """
    # Load environment variables
    load_dotenv()
    
    print("\n=== Chicago Restaurant Bot Post Preview ===\n")
    
    try:
        # Load config
        config = Config.from_env()
        
        # Initialize Chicago Data Service
        chicago_data = ChicagoDataService(config.chicago_data_token)
        
        # Get restaurants from the last 7 days
        last_week = datetime.now() - timedelta(days=7)
        print(f"Fetching restaurants since {last_week.date()}")
        
        restaurants = chicago_data.get_new_restaurants(last_week)
        
        if not restaurants:
            print("\nNo new restaurants found in the last 7 days.")
            print("\nShowing sample restaurant instead:")
            restaurants = [create_sample_restaurant()]
        else:
            print(f"\nFound {len(restaurants)} new restaurants!")
            
        # Preview each restaurant
        for i, restaurant in enumerate(restaurants, 1):
            print(f"\n=== Restaurant {i}/{len(restaurants)} ===")
            preview_restaurant(restaurant, config)
            
        # Summary
        would_post = sum(1 for r in restaurants if r.passes_filters(config.filters))
        print(f"\nSummary: {would_post}/{len(restaurants)} restaurants would be posted")
            
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTip: Make sure you have a valid config.yaml file and proper environment variables set.")
        return

if __name__ == "__main__":
    main()
