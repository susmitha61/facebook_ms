import os

class Config:
    # MongoDB configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongomock://localhost:27017/facebook_insights')
    MONGODB_CONNECT_TIMEOUT = 5000  # milliseconds
    MONGODB_SERVER_SELECTION_TIMEOUT = 5000  # milliseconds
    MONGODB_MAX_RETRIES = 3
    MONGODB_RETRY_DELAY = 2  # seconds
    MONGODB_CONNECT_OPTIONS = {
        "connectTimeoutMS": MONGODB_CONNECT_TIMEOUT,
        "serverSelectionTimeoutMS": MONGODB_SERVER_SELECTION_TIMEOUT,
        "retryWrites": True,
        "retryReads": True,
        "maxPoolSize": 50,
        "minPoolSize": 10,
        "maxIdleTimeMS": 10000,
        "waitQueueTimeoutMS": 5000
    }

    # Cache configuration
    CACHE_TYPE = "SimpleCache"  # Using simple cache for development
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_THRESHOLD = 1000  # Maximum number of items the cache will store

    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

    # Scraping configuration
    MAX_POSTS_PER_PAGE = 40
    MAX_COMMENTS_PER_POST = 100
    MAX_FOLLOWERS_PER_PAGE = 1000

    # Rate limiting
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = "memory://"

    # Default pagination settings
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100