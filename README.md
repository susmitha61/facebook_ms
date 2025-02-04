
# Facebook Insights Microservice

A Flask-based microservice for analyzing and tracking Facebook page performance metrics in real-time.

## Features

- Scrape and analyze Facebook page data
- Track page metrics including followers, likes, and engagement
- Monitor post performance and interaction statistics
- Cache frequently accessed data for improved performance
- RESTful API endpoints for data retrieval
- Responsive web interface with Bootstrap

## Tech Stack

- Python 3.11
- Flask
- MongoDB
- BeautifulSoup4
- Flask-Caching
- Bootstrap 5

## API Endpoints

- `GET /api/page/<username>`: Get page details and metrics
- `GET /api/pages`: List pages with filtering options
- `GET /api/page/<username>/posts`: Get posts for a specific page

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up MongoDB connection in `config.py`
4. Run the application:
```bash
python main.py
```

## Environment Variables

- `MONGODB_URI`: MongoDB connection string
- `SECRET_KEY`: Flask secret key
- `LOG_LEVEL`: Logging level (default: DEBUG)

## Project Structure

```
├── main.py           # Application entry point
├── config.py         # Configuration settings
├── models.py         # Database models
├── routes.py         # API routes
├── scraper.py        # Facebook page scraper
├── utils.py          # Utility functions
├── static/           # Static assets
└── templates/        # HTML templates
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
