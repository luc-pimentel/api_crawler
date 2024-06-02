import praw
import requests
from decouple import config
from ._base import BaseAPI
from ..data_lake.logger import log_io_to_json

REDDIT_CLIENT_ID = config('REDDIT_CLIENT_ID', default=None)
REDDIT_CLIENT_SECRET = config('REDDIT_CLIENT_SECRET', default=None)
REDDIT_USER_AGENT = config('REDDIT_USER_AGENT', default=None)



class RedditAPI(BaseAPI):
    def __init__(self):

        missing_vars = [var for var, value in {
            'REDDIT_CLIENT_ID': REDDIT_CLIENT_ID,
            'REDDIT_CLIENT_SECRET': REDDIT_CLIENT_SECRET,
            'REDDIT_USER_AGENT': REDDIT_USER_AGENT
        }.items() if value is None]

        if missing_vars:
            raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}. Please add them to proceed.")
    
        
        self.client = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                                  client_secret=REDDIT_CLIENT_SECRET,
                                  user_agent=REDDIT_USER_AGENT)
        

    @log_io_to_json
    def get_top_posts(self, subreddit_name: str, limit: int = 10, time_filter: str = 'week'):
        """
        Retrieves the top posts from a given subreddit.

        Args:
            subreddit_name (str): The name of the subreddit.
            limit (int, optional): The maximum number of posts to retrieve. Defaults to 10.
            time_filter (str, optional): The time filter for the top posts. Possible values are
                'hour', 'day', 'week', 'month', 'year', and 'all'. Defaults to 'day'.

        Returns:
            list: A list of top submissions from the subreddit.
        """
        subreddit = self.client.subreddit(subreddit_name)
        top_posts = subreddit.top(limit=limit, time_filter=time_filter)
        return list(top_posts)
    

    @log_io_to_json
    def get_submission_title(self, submission):
        """
        Retrieves the title of a submission.

        Args:
            submission (praw.models.Submission): The submission object.

        Returns:
            str: The title of the submission.
        """
        return submission.title


    @log_io_to_json
    def get_submission_content(self, submission):
        """
        Retrieves the content (selftext) of a submission.

        Args:
            submission (praw.models.Submission): The submission object.

        Returns:
            str: The content (selftext) of the submission.
        """
        return submission.selftext


    @log_io_to_json
    def get_top_comments(self, submission, limit=10):
        """
        Retrieves the top comments of a submission.

        Args:
            submission (praw.models.Submission): The submission object.
            limit (int, optional): The maximum number of top comments to retrieve. Defaults to 10.

        Returns:
            list: A list of top comment objects.
        """
        submission.comments.replace_more(limit=0)  # Replace MoreComments objects with comments
        top_comments = submission.comments[:limit]  # Get the top comments
        return top_comments
    

    @log_io_to_json
    def get_comment_content(self, comment):
        return comment.body