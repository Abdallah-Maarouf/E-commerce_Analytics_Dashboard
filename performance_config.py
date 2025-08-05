# Dashboard Performance Configuration

# Data Loading Settings
CHUNK_SIZE = 10000
MAX_MEMORY_USAGE = 500  # MB
CACHE_ENABLED = True

# UI Settings
LAZY_LOADING = True
CHART_ANIMATION = False  # Disable for better performance
MAX_CHART_POINTS = 1000

# Streamlit Settings
STREAMLIT_CONFIG = {
    'server.maxUploadSize': 200,
    'server.maxMessageSize': 200,
    'client.caching': True,
    'client.displayEnabled': True
}
