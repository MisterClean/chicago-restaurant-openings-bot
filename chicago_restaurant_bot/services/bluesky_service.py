import logging
import time
from typing import Optional
from atproto import Client
from ..models.restaurant import Restaurant
from ..config import Config


class BlueskyService:
    """Service for interacting with the Bluesky social network."""
    
    def __init__(self, config: Config):
        """
        Initialize Bluesky service.
        
        Args:
            config: Config object containing credentials and settings
        """
        self.config = config
        self.client = Client()
        self.logger = logging.getLogger(__name__)
        self._login(config.bluesky_handle, config.bluesky_password)
        
        # Get throttling config
        features = config.features
        throttling = self.config.yaml_config.get('features', {}).get('throttling', {})
        self.throttling_enabled = throttling.get('enabled', True)
        self.min_delay = throttling.get('min_delay_between_posts', 2)
        
        # Get error handling config
        error_handling = self.config.yaml_config.get('features', {}).get('error_handling', {})
        self.auto_retry = features.auto_retry
        self.retry_delay = error_handling.get('retry_delay', 300)
        self.max_retries = error_handling.get('max_retries', 3)
        
        self.last_post_time = 0

    def _login(self, handle: str, password: str) -> None:
        """
        Login to Bluesky.
        
        Args:
            handle: Bluesky handle
            password: Bluesky password
        """
        try:
            self.client.login(handle, password)
            self.logger.info(f"Successfully logged in as {handle}")
        except Exception as e:
            self.logger.error(f"Failed to login to Bluesky: {e}")
            raise

    def _enforce_rate_limit(self):
        """Enforce minimum delay between posts if throttling is enabled."""
        if self.throttling_enabled:
            elapsed = time.time() - self.last_post_time
            if elapsed < self.min_delay:
                sleep_time = self.min_delay - elapsed
                self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

    def post_restaurant(self, restaurant: Restaurant) -> bool:
        """
        Post a restaurant announcement to Bluesky.
        
        Args:
            restaurant: Restaurant object to post about
            
        Returns:
            bool indicating if post was successful
        """
        # Check filters first
        if not restaurant.passes_filters(self.config.filters):
            self.logger.info(
                f"Skipping {restaurant.name} - did not pass filters"
            )
            return False
            
        retries = 0
        while retries <= self.max_retries:
            try:
                # Enforce rate limiting
                self._enforce_rate_limit()
                
                # Format and post announcement
                announcement = restaurant.format_announcement(self.config)
                self.client.send_post(text=announcement)
                
                # Update last post time
                self.last_post_time = time.time()
                
                self.logger.info(
                    f"Successfully posted announcement for {restaurant.name}"
                )
                return True
                
            except Exception as e:
                retries += 1
                self.logger.error(
                    f"Failed to post to Bluesky (attempt {retries}/{self.max_retries}): {e}"
                )
                
                # If auto retry is enabled and we haven't exceeded max retries
                if self.auto_retry and retries <= self.max_retries:
                    self.logger.info(
                        f"Retrying in {self.retry_delay} seconds..."
                    )
                    time.sleep(self.retry_delay)
                else:
                    break
                    
        return False
