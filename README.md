# Chicago Restaurant Bot

A Python bot that posts new restaurant openings in Chicago to Bluesky social network. The bot monitors the Chicago Data Portal for new retail food license applications and automatically posts announcements about new restaurants.

## Features

- Monitors Chicago Data Portal for new restaurant licenses
- Posts formatted announcements to Bluesky
- Configurable check intervals
- Robust error handling and logging
- Rate limit aware posting
- Dynamic configuration via YAML
- Optional metrics monitoring
- Configurable feature flags
- Customizable post templates
- Flexible filtering options
- Test mode with real data preview

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd chicago-restaurant-openings
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The bot supports both environment variables and YAML configuration:

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Required
BLUESKY_HANDLE=your.handle.bsky.social
BLUESKY_PASSWORD=your_password

# Optional
CHICAGO_DATA_TOKEN=your_data_portal_token
CHECK_INTERVAL_MINUTES=60
TIMESTAMP_FILE=last_check.txt
LOG_FILE=bot.log
CONFIG_PATH=config.yaml  # Custom path to YAML config
```

### YAML Configuration

The `config.yaml` file provides dynamic configuration for various features. Here's what you can configure:

#### Feature Flags
```yaml
features:
  announcement:
    include_ward: true
    include_square_footage: true
    include_business_activity: true
  formatting:
    use_emojis: true
    add_hashtags: true
  throttling:
    enabled: true
    min_delay_between_posts: 2
  error_handling:
    auto_retry: true
    retry_delay: 300
    max_retries: 3
```

#### Post Templates
```yaml
post_template:
  header: "🆕 New Restaurant Alert!"
  name_prefix: "🍽️"
  address_prefix: "📍"
  activity_prefix: "🍳"
  square_footage_prefix: "📐"
  ward_prefix: "📍"
```

#### Hashtags
```yaml
hashtags:
  default:
    - ChicagoFood
    - ChicagoRestaurants
    - NewInChicago
  additional: []  # Add custom hashtags
```

#### Filtering
```yaml
filters:
  excluded_license_types: []  # License types to ignore
  included_wards: []         # Only include these wards (empty = all)
  included_zip_codes: []     # Only include these zip codes (empty = all)
```

#### Monitoring
```yaml
monitoring:
  log_level: "INFO"        # DEBUG, INFO, WARNING, ERROR, CRITICAL
  enable_metrics: false    # Enable Prometheus metrics
  metrics_port: 9090      # Port for metrics server
```

## Usage

### Running the Bot

Run the bot in production mode:

```bash
python -m chicago_restaurant_bot.bot
```

The bot will:
1. Load configuration from environment variables and YAML
2. Check the Chicago Data Portal for new restaurant licenses
3. Filter results based on configured rules
4. Post announcements to Bluesky using configured templates
5. Sleep for the configured interval
6. Repeat

### Testing with Real Data

To preview posts using real restaurant data without posting to Bluesky:

```bash
python -m chicago_restaurant_bot.test_post
```

This will:
1. Fetch real restaurant data from the Chicago Data Portal (last 7 days)
2. For each restaurant found:
   - Display the raw restaurant details
   - Show a preview of how the post would be formatted
   - Show the character count
   - Indicate if the post would pass your configured filters
3. Provide a summary of how many restaurants would be posted

If no new restaurants are found, it will show a sample restaurant instead.

This is useful for:
- Testing your API connection
- Verifying data fetching
- Testing your post template configuration
- Checking filter rules
- Ensuring posts fit within character limits
- Previewing the actual announcements before going live

## Metrics

If metrics are enabled (`enable_metrics: true`), the bot exposes Prometheus metrics at `http://localhost:9090`:

- `restaurants_found_total`: Total number of new restaurants found
- `posts_succeeded_total`: Total number of successful posts
- `posts_failed_total`: Total number of failed posts
- `processing_time_seconds`: Time spent processing restaurants

## Project Structure

```
chicago_restaurant_bot/
├── models/
│   └── restaurant.py     # Restaurant data model
├── services/
│   ├── bluesky_service.py    # Bluesky API interaction
│   └── chicago_data_service.py    # Chicago Data Portal API
├── utils/
│   ├── logging_config.py    # Logging configuration
│   └── time_utils.py        # Timestamp management
├── bot.py          # Main bot logic
├── config.py       # Configuration management
└── test_post.py    # Real data testing utility
```

## Error Handling

The bot includes comprehensive error handling:
- Configurable automatic retries
- Customizable retry delays and limits
- Detailed logging with configurable levels
- Rate limiting and throttling protection
- Metrics tracking for monitoring (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
