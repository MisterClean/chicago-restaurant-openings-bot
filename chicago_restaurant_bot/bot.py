import time
import logging
from datetime import datetime
from typing import Dict, Any
from .config import Config
from .models.restaurant import Restaurant
from .services.bluesky_service import BlueskyService
from .services.chicago_data_service import ChicagoDataService
from .utils.time_utils import TimestampManager
from .utils.logging_config import setup_logging

try:
    import prometheus_client as prom
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False


class ChicagoRestaurantBot:
    """Bot that posts new Chicago restaurant openings to Bluesky."""
    
    def __init__(self, config: Config):
        """
        Initialize the bot with configuration.
        
        Args:
            config: Config object containing app settings
        """
        self.config = config
        
        # Set up logging
        setup_logging(
            level=config.get_log_level(),
            log_file=config.log_file
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.bluesky = BlueskyService(config)
        self.chicago_data = ChicagoDataService(
            config.chicago_data_token
        )
        self.timestamp_mgr = TimestampManager(
            config.timestamp_file
        )
        
        # Set up metrics if enabled
        self.metrics = self._setup_metrics() if (
            config.features.enable_metrics and METRICS_AVAILABLE
        ) else None
        
    def _setup_metrics(self) -> Dict[str, Any]:
        """Set up Prometheus metrics."""
        metrics = {
            'restaurants_found': prom.Counter(
                'restaurants_found_total',
                'Total number of new restaurants found'
            ),
            'posts_succeeded': prom.Counter(
                'posts_succeeded_total',
                'Total number of successful posts'
            ),
            'posts_failed': prom.Counter(
                'posts_failed_total',
                'Total number of failed posts'
            ),
            'processing_time': prom.Histogram(
                'processing_time_seconds',
                'Time spent processing restaurants'
            )
        }
        
        # Start metrics server
        prom.start_http_server(
            self.config.monitoring.get('metrics_port', 9090)
        )
        
        return metrics
        
    def process_new_restaurants(self) -> int:
        """
        Fetch and post new restaurants.
        
        Returns:
            Number of restaurants processed
        """
        # Get last check time
        last_check = self.timestamp_mgr.load_timestamp()
        
        # Start timing if metrics enabled
        start_time = time.time()
        
        try:
            # Fetch new restaurants
            restaurants = self.chicago_data.get_new_restaurants(last_check)
            
            if self.metrics:
                self.metrics['restaurants_found'].inc(len(restaurants))
            
            # Post each restaurant
            successful_posts = 0
            for restaurant in restaurants:
                if self.bluesky.post_restaurant(restaurant):
                    successful_posts += 1
                    if self.metrics:
                        self.metrics['posts_succeeded'].inc()
                elif self.metrics:
                    self.metrics['posts_failed'].inc()
            
            # Update timestamp after successful processing
            self.timestamp_mgr.save_timestamp(datetime.now())
            
            # Record processing time if metrics enabled
            if self.metrics:
                self.metrics['processing_time'].observe(
                    time.time() - start_time
                )
            
            return successful_posts
            
        except Exception as e:
            self.logger.error(f"Error processing restaurants: {e}")
            if self.metrics:
                self.metrics['posts_failed'].inc()
            return 0
    
    def run(self):
        """Run the bot continuously."""
        self.logger.info(
            f"Starting Chicago Restaurant Bot "
            f"(checking every {self.config.check_interval_minutes} minutes)"
        )
        
        if self.metrics:
            self.logger.info(
                f"Metrics server running on port "
                f"{self.config.monitoring.get('metrics_port', 9090)}"
            )
        
        while True:
            try:
                # Process new restaurants
                processed = self.process_new_restaurants()
                
                self.logger.info(
                    f"Processed {processed} new restaurants. "
                    f"Sleeping for {self.config.check_interval_minutes} minutes."
                )
                
                # Sleep until next check
                time.sleep(self.config.check_interval_minutes * 60)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                # Sleep for 5 minutes before retrying on error
                time.sleep(300)


def main():
    """Entry point for the bot."""
    try:
        # Load configuration from environment and YAML
        config = Config.from_env()
        
        # Initialize and run bot
        bot = ChicagoRestaurantBot(config)
        bot.run()
        
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    main()
