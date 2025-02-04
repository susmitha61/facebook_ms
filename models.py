from datetime import datetime
from pymongo import MongoClient, errors
from mongomock import MongoClient as MockMongoClient
from config import Config
import time
import logging
import re

def get_database():
    """Initialize MongoDB connection with retries"""
    last_error = None

    for attempt in range(Config.MONGODB_MAX_RETRIES):
        try:
            if Config.MONGODB_URI.startswith('mongomock://'):
                client = MockMongoClient()
                db = client.get_database('facebook_insights')
            else:
                client = MongoClient(
                    Config.MONGODB_URI,
                    **Config.MONGODB_CONNECT_OPTIONS
                )
                db = client.get_default_database()
                db.command('ping')
            logging.info("Successfully connected to MongoDB")
            return db
        except Exception as e:
            last_error = str(e)
            logging.warning(f"MongoDB connection attempt {attempt + 1} failed: {last_error}")
            if attempt < Config.MONGODB_MAX_RETRIES - 1:
                time.sleep(Config.MONGODB_RETRY_DELAY)
                continue

    logging.error(f"Failed to connect to MongoDB after {Config.MONGODB_MAX_RETRIES} attempts")
    return None

# Initialize database connection
db = None
try:
    db = get_database()
except Exception as e:
    logging.error(f"Failed to initialize database: {e}")

class Page:
    collection = db.pages if db else None

    @staticmethod
    def create_indexes():
        """Create indexes for the Page collection"""
        if not Page.collection:
            logging.error("Database not initialized, cannot create indexes")
            return False
        try:
            Page.collection.create_index("username", unique=True)
            Page.collection.create_index("follower_count")
            Page.collection.create_index("category")
            Page.collection.create_index("name")
            Page.collection.create_index([("name", "text")])  # Text index for search
            logging.info("Successfully created indexes for Page collection")
            return True
        except Exception as e:
            logging.error(f"Error creating indexes for Page collection: {e}")
            return False

    @staticmethod
    def create(data):
        """Create a new page"""
        if not Page.collection:
            raise Exception("Database not initialized")
        data.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        return Page.collection.insert_one(data).inserted_id

    @staticmethod
    def find_by_username(username):
        """Find a page by username"""
        if not Page.collection:
            raise Exception("Database not initialized")
        return Page.collection.find_one({"username": username})

    @staticmethod
    def find_by_filters(name=None, category=None, min_followers=None, max_followers=None, page=1, per_page=10):
        """Find pages using various filters"""
        if not Page.collection:
            raise Exception("Database not initialized")

        query = {}
        if name:
            if isinstance(Page.collection, MockMongoClient):
                # Mongomock doesn't support text search, fallback to regex
                query['name'] = {'$regex': name, '$options': 'i'}
            else:
                query['$text'] = {'$search': name}
        if category:
            query['category'] = category
        if min_followers is not None or max_followers is not None:
            query['follower_count'] = {}
            if min_followers is not None:
                query['follower_count']['$gte'] = min_followers
            if max_followers is not None:
                query['follower_count']['$lte'] = max_followers

        skip = (page - 1) * per_page
        return Page.collection.find(query).skip(skip).limit(per_page)

class Post:
    collection = db.posts if db else None

    @staticmethod
    def create_indexes():
        """Create indexes for the Post collection"""
        if not Post.collection:
            logging.error("Database not initialized, cannot create indexes")
            return False
        try:
            Post.collection.create_index([("page_id", 1), ("created_at", -1)])
            Post.collection.create_index("created_at")
            logging.info("Successfully created indexes for Post collection")
            return True
        except Exception as e:
            logging.error(f"Error creating indexes for Post collection: {e}")
            return False

    @staticmethod
    def create_many(posts):
        """Create multiple posts"""
        if not Post.collection:
            raise Exception("Database not initialized")
        if posts:
            for post in posts:
                post['created_at'] = post.get('created_at', datetime.utcnow())
            return Post.collection.insert_many(posts).inserted_ids
        return None

    @staticmethod
    def find_by_page(page_id, limit=15):
        """Find posts by page ID"""
        if not Post.collection:
            raise Exception("Database not initialized")
        return Post.collection.find({"page_id": page_id}).sort("created_at", -1).limit(limit)

class Comment:
    collection = db.comments if db else None

    @staticmethod
    def create_indexes():
        """Create indexes for the Comment collection"""
        if not Comment.collection:
            logging.error("Database not initialized, cannot create indexes")
            return False
        try:
            Comment.collection.create_index([("post_id", 1), ("created_at", -1)])
            logging.info("Successfully created indexes for Comment collection")
            return True
        except Exception as e:
            logging.error(f"Error creating indexes for Comment collection: {e}")
            return False

    @staticmethod
    def create_many(comments):
        """Create multiple comments"""
        if not Comment.collection:
            raise Exception("Database not initialized")
        if comments:
            for comment in comments:
                comment['created_at'] = comment.get('created_at', datetime.utcnow())
            return Comment.collection.insert_many(comments).inserted_ids
        return None

    @staticmethod
    def find_by_post(post_id, limit=50):
        """Find comments by post ID"""
        if not Comment.collection:
            raise Exception("Database not initialized")
        return Comment.collection.find({"post_id": post_id}).sort("created_at", -1).limit(limit)

class Follower:
    collection = db.followers if db else None

    @staticmethod
    def create_indexes():
        """Create indexes for the Follower collection"""
        if not Follower.collection:
            logging.error("Database not initialized, cannot create indexes")
            return False
        try:
            Follower.collection.create_index([("page_id", 1), ("follower_id", 1)], unique=True)
            logging.info("Successfully created indexes for Follower collection")
            return True
        except Exception as e:
            logging.error(f"Error creating indexes for Follower collection: {e}")
            return False

    @staticmethod
    def create_many(followers):
        """Create multiple followers"""
        if not Follower.collection:
            raise Exception("Database not initialized")
        if followers:
            for follower in followers:
                follower['created_at'] = follower.get('created_at', datetime.utcnow())
            return Follower.collection.insert_many(followers).inserted_ids
        return None

    @staticmethod
    def find_by_page(page_id, limit=100):
        """Find followers by page ID"""
        if not Follower.collection:
            raise Exception("Database not initialized")
        return Follower.collection.find({"page_id": page_id}).sort("created_at", -1).limit(limit)