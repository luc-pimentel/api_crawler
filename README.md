# API Crawler

[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/Luc_AI_Insights)
[![Medium](https://img.shields.io/badge/Medium-black?style=flat-square&logo=medium)](https://medium.com/@luc-ai-insights)


The goal of this repo is to simplify the process of scraping the web and creating your own data lakes.

Fetch and store data from the web and use it to feed your own AI models, vectorstores, and databases.

## Features

- **Data Retrieval**: Retrieve data from different sources, such as comments, posts, videos, and channels, using the provided API methods.
- **Data Storage**: Store retrieved raw data in JSON format. Use it later to build your own vectorstores, finetune your models, and etc.

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/your-repo/api-crawler.git
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Configure the API credentials by creating a `.env` file and adding the necessary credentials for the APIs you want to use.

4. Import the desired API module and start retrieving data:

```python
from api.reddit import RedditAPI

reddit_api = RedditAPI()
posts = reddit_api.get_posts(subreddit='python', limit=10)
```

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.
