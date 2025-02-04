import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
import re

class FacebookScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _get_soup(self, url):
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logging.error(f"Error fetching URL {url}: {str(e)}")
            return None

    def _extract_number(self, text):
        """Extract number from text like '1.2K' or '1.2M'"""
        if not text:
            return 0
        text = text.strip().upper()
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        try:
            if text[-1] in multipliers:
                number = float(text[:-1]) * multipliers[text[-1]]
            else:
                number = float(text.replace(',', ''))
            return int(number)
        except (ValueError, IndexError):
            return 0

    def scrape_page(self, username):
        url = f"https://www.facebook.com/{username}"
        soup = self._get_soup(url)
        if not soup:
            return None

        # Extract basic page information
        page_data = {
            'username': username,
            'url': url,
            'scraped_at': datetime.utcnow(),
            'name': self._extract_page_name(soup),
            'profile_pic': self._extract_profile_pic(soup),
            'email': self._extract_email(soup),
            'website': self._extract_website(soup),
            'category': self._extract_category(soup),
            'follower_count': self._extract_follower_count(soup),
            'likes_count': self._extract_likes_count(soup),
            'creation_date': self._extract_creation_date(soup),
            'about': self._extract_about(soup),
            'posts': self._extract_posts(soup, limit=30)
        }

        # Add followers/following if available
        followers = self._extract_followers(soup)
        if followers:
            page_data['followers'] = followers

        return page_data

    def _extract_page_name(self, soup):
        name_element = soup.find('h1', {'class': re.compile(r'.*page-name.*')})
        if not name_element:
            name_element = soup.find('h1')
        return name_element.text.strip() if name_element else None

    def _extract_profile_pic(self, soup):
        img = soup.find('img', {'class': re.compile(r'.*profile.*pic.*')})
        if img:
            return img.get('src')
        return None

    def _extract_email(self, soup):
        email_element = soup.find('a', {'href': re.compile(r'mailto:.*')})
        if email_element:
            href = email_element.get('href', '')
            return href.replace('mailto:', '')
        return None

    def _extract_website(self, soup):
        website_element = soup.find('a', {'href': re.compile(r'https?://(?!.*facebook\.com).*')})
        if website_element:
            return website_element.get('href')
        return None

    def _extract_category(self, soup):
        category_element = soup.find('div', {'class': re.compile(r'.*category.*')})
        return category_element.text.strip() if category_element else None

    def _extract_follower_count(self, soup):
        followers_element = soup.find(string=re.compile(r'.*followers.*', re.I))
        if followers_element:
            return self._extract_number(followers_element.parent.text)
        return 0

    def _extract_likes_count(self, soup):
        likes_element = soup.find(string=re.compile(r'.*people like this.*', re.I))
        if likes_element:
            return self._extract_number(likes_element.parent.text)
        return 0

    def _extract_creation_date(self, soup):
        date_element = soup.find(string=re.compile(r'.*Page created.*', re.I))
        if date_element:
            try:
                date_text = date_element.parent.text
                date_match = re.search(r'(\w+ \d+,? \d{4})', date_text)
                if date_match:
                    return datetime.strptime(date_match.group(1), '%B %d, %Y')
            except Exception as e:
                logging.error(f"Error parsing creation date: {e}")
        return None

    def _extract_about(self, soup):
        about_element = soup.find('div', {'class': re.compile(r'.*about.*')})
        return about_element.text.strip() if about_element else None

    def _extract_posts(self, soup, limit=30):
        posts = []
        post_elements = soup.find_all('div', {'class': re.compile(r'.*feed.*story.*')}, limit=limit)

        for post in post_elements:
            post_data = {
                'content': self._extract_post_content(post),
                'created_at': self._extract_post_date(post),
                'likes_count': self._extract_post_likes(post),
                'comments': self._extract_post_comments(post),
                'shares_count': self._extract_post_shares(post),
                'media_urls': self._extract_post_media(post)
            }
            posts.append(post_data)

        return posts

    def _extract_post_content(self, post):
        content_element = post.find('div', {'class': re.compile(r'.*post-content.*')})
        return content_element.text.strip() if content_element else None

    def _extract_post_date(self, post):
        date_element = post.find('abbr')
        if date_element and date_element.get('title'):
            try:
                return datetime.strptime(date_element['title'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
        return datetime.utcnow()

    def _extract_post_likes(self, post):
        likes_element = post.find('span', {'class': re.compile(r'.*like.*count.*')})
        return self._extract_number(likes_element.text) if likes_element else 0

    def _extract_post_comments(self, post):
        comments = []
        comment_elements = post.find_all('div', {'class': re.compile(r'.*comment.*')})

        for comment in comment_elements:
            comment_data = {
                'content': comment.text.strip(),
                'created_at': datetime.utcnow(),  # Facebook might hide actual dates
                'author': self._extract_comment_author(comment)
            }
            comments.append(comment_data)

        return comments

    def _extract_comment_author(self, comment):
        author_element = comment.find('a', {'class': re.compile(r'.*author.*')})
        if author_element:
            return {
                'name': author_element.text.strip(),
                'profile_url': author_element.get('href')
            }
        return None

    def _extract_post_shares(self, post):
        shares_element = post.find('span', {'class': re.compile(r'.*share.*count.*')})
        return self._extract_number(shares_element.text) if shares_element else 0

    def _extract_post_media(self, post):
        media_urls = []
        media_elements = post.find_all(['img', 'video'])

        for media in media_elements:
            if media.name == 'img':
                url = media.get('src')
            else:  # video
                url = media.get('src') or media.get('data-url')

            if url:
                media_urls.append(url)

        return media_urls

    def _extract_followers(self, soup):
        followers = []
        follower_elements = soup.find_all('div', {'class': re.compile(r'.*follower.*item.*')})

        for follower in follower_elements:
            follower_data = {
                'name': self._extract_follower_name(follower),
                'profile_pic': self._extract_follower_pic(follower),
                'profile_url': self._extract_follower_url(follower),
                'created_at': datetime.utcnow()
            }
            followers.append(follower_data)

        return followers

    def _extract_follower_name(self, follower):
        name_element = follower.find('a', {'class': re.compile(r'.*name.*')})
        return name_element.text.strip() if name_element else None

    def _extract_follower_pic(self, follower):
        img = follower.find('img')
        return img.get('src') if img else None

    def _extract_follower_url(self, follower):
        link = follower.find('a')
        return link.get('href') if link else None