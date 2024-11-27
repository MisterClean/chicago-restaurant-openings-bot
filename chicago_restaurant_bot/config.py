import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import yaml
import logging


@dataclass
class FeatureFlags:
    """Feature flags configuration."""
    include_ward: bool = True
    include_square_footage: bool = True
    include_business_activity: bool = True
    use_emojis: bool = True
    add_hashtags: bool = True
    auto_retry: bool = True
    enable_metrics: bool = False


@dataclass
class Config:
    """Application configuration."""
    # Required credentials
    bluesky_handle: str
    bluesky_password: str
    chicago_data_token: Optional[str]
    
    # Basic settings
    check_interval_minutes: int = 60
    timestamp_file: str = "last_check.txt"
    log_file: Optional[str] = None
    
    # Feature flags and dynamic config
    features: FeatureFlags = FeatureFlags()
    hashtags: List[str] = None
    post_template: Dict[str, str] = None
    filters: Dict[str, List[str]] = None
    monitoring: Dict[str, Any] = None
    
    @classmethod
    def load_yaml_config(cls, config_path: str = "config.yaml") -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.warning(f"Failed to load YAML config: {e}")
            return {}

    @classmethod
    def from_env(cls, config_path: str = "config.yaml") -> 'Config':
        """
        Create Config from environment variables and YAML config.
        Environment variables take precedence over YAML config.
        
        Required env vars:
            BLUESKY_HANDLE: Bluesky handle
            BLUESKY_PASSWORD: Bluesky password
            
        Optional env vars:
            CHICAGO_DATA_TOKEN: Chicago Data Portal API token
            CHECK_INTERVAL_MINUTES: Minutes between checks (default: 60)
            TIMESTAMP_FILE: Path to timestamp file (default: last_check.txt)
            LOG_FILE: Path to log file (default: None, logs to console only)
            CONFIG_PATH: Path to YAML config file (default: config.yaml)
            
        Returns:
            Config object
        """
        # Load YAML config first
        yaml_config = cls.load_yaml_config(
            os.getenv('CONFIG_PATH', config_path)
        )
        
        # Check required environment variables
        required_vars = {
            'BLUESKY_HANDLE': 'Bluesky handle',
            'BLUESKY_PASSWORD': 'Bluesky password',
        }
        
        missing_vars = [
            var for var in required_vars 
            if not os.getenv(var)
        ]
        
        if missing_vars:
            missing_desc = [
                f"{var} ({required_vars[var]})"
                for var in missing_vars
            ]
            raise ValueError(
                "Missing required environment variables: " +
                ", ".join(missing_desc)
            )
        
        # Create feature flags from YAML config
        features_config = yaml_config.get('features', {})
        features = FeatureFlags(
            include_ward=features_config.get('announcement', {}).get('include_ward', True),
            include_square_footage=features_config.get('announcement', {}).get('include_square_footage', True),
            include_business_activity=features_config.get('announcement', {}).get('include_business_activity', True),
            use_emojis=features_config.get('formatting', {}).get('use_emojis', True),
            add_hashtags=features_config.get('formatting', {}).get('add_hashtags', True),
            auto_retry=features_config.get('error_handling', {}).get('auto_retry', True),
            enable_metrics=yaml_config.get('monitoring', {}).get('enable_metrics', False)
        )
        
        # Create config object with environment variables taking precedence
        return cls(
            bluesky_handle=os.getenv('BLUESKY_HANDLE'),
            bluesky_password=os.getenv('BLUESKY_PASSWORD'),
            chicago_data_token=os.getenv('CHICAGO_DATA_TOKEN'),
            check_interval_minutes=int(
                os.getenv('CHECK_INTERVAL_MINUTES', '60')
            ),
            timestamp_file=os.getenv(
                'TIMESTAMP_FILE', 'last_check.txt'
            ),
            log_file=os.getenv('LOG_FILE'),
            features=features,
            hashtags=(
                yaml_config.get('hashtags', {}).get('default', []) +
                yaml_config.get('hashtags', {}).get('additional', [])
            ),
            post_template=yaml_config.get('post_template', {}),
            filters=yaml_config.get('filters', {}),
            monitoring=yaml_config.get('monitoring', {})
        )

    def get_log_level(self) -> int:
        """Get logging level from config."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        level_str = self.monitoring.get('log_level', 'INFO')
        return level_map.get(level_str.upper(), logging.INFO)
