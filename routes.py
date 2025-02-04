from flask import Blueprint, jsonify, request
from models import Page, Post
from scraper import FacebookScraper
from flask_caching import Cache
from config import Config
import logging

api = Blueprint('api', __name__)
cache = None

def init_cache(app):
    global cache
    cache = Cache(app)
    return cache

@api.route('/api/page/<username>')
def get_page(username):
    if cache:
        # Only use cache if it's properly initialized
        cached_result = cache.get(f'page_{username}')
        if cached_result:
            return jsonify(cached_result)

    try:
        page = Page.find_by_username(username)

        if not page:
            # Try to scrape the page
            scraper = FacebookScraper()
            page_data = scraper.scrape_page(username)

            if page_data:
                page_id = Page.create(page_data)
                if 'posts' in page_data:
                    Post.create_many(page_data['posts'])
                page = Page.find_by_username(username)
            else:
                return jsonify({'error': 'Page not found'}), 404

        if cache:
            cache.set(f'page_{username}', page, timeout=300)
        return jsonify(page)
    except Exception as e:
        logging.error(f"Error getting page {username}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/api/pages')
def get_pages():
    try:
        name = request.args.get('name')
        category = request.args.get('category')
        min_followers = request.args.get('min_followers', type=int)
        max_followers = request.args.get('max_followers', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pages = Page.find_by_filters(
            name=name,
            category=category,
            min_followers=min_followers,
            max_followers=max_followers,
            page=page,
            per_page=per_page
        )

        return jsonify({'pages': list(pages)})
    except Exception as e:
        logging.error(f"Error getting pages: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/api/page/<username>/posts')
def get_page_posts(username):
    try:
        page = Page.find_by_username(username)
        if not page:
            return jsonify({'error': 'Page not found'}), 404

        limit = request.args.get('limit', 15, type=int)
        posts = Post.find_by_page(page['_id'], limit=limit)

        return jsonify({'posts': list(posts)})
    except Exception as e:
        logging.error(f"Error getting posts for page {username}: {e}")
        return jsonify({'error': 'Internal server error'}), 500