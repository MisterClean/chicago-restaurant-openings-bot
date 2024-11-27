import os
from datetime import datetime
import logging


class TimestampManager:
    """Manages persistence of the last check timestamp."""
    
    def __init__(self, timestamp_file: str):
        """
        Initialize TimestampManager.
        
        Args:
            timestamp_file: Path to file for storing timestamp
        """
        self.timestamp_file = timestamp_file
        self.logger = logging.getLogger(__name__)
        
        # Create timestamp file if it doesn't exist
        if not os.path.exists(self.timestamp_file):
            self.save_timestamp(datetime.now())

    def load_timestamp(self) -> datetime:
        """
        Load the last check timestamp from file.
        
        Returns:
            datetime object of last check
        """
        try:
            with open(self.timestamp_file, "r") as f:
                timestamp_str = f.read().strip()
                return datetime.fromisoformat(timestamp_str)
        except Exception as e:
            self.logger.error(f"Error loading timestamp: {e}")
            # Return current time if there's an error
            return datetime.now()

    def save_timestamp(self, timestamp: datetime) -> None:
        """
        Save a timestamp to file.
        
        Args:
            timestamp: datetime to save
        """
        try:
            with open(self.timestamp_file, "w") as f:
                f.write(timestamp.isoformat())
        except Exception as e:
            self.logger.error(f"Error saving timestamp: {e}")
