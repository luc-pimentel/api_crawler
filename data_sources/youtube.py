from ._base import BaseSearchAPI, BaseRestfulAPI
from ..data_lake.logger import log_io_to_json
import youtubesearchpython as yts
from decouple import config


YOUTUBE_API_KEY = config('YOUTUBE_API_KEY', default = None)


class YoutubeAPI(BaseRestfulAPI, BaseSearchAPI):
    base_url: str = 'https://www.googleapis.com/youtube/v3/'
    api_key: str = YOUTUBE_API_KEY



    def get(self, endpoint, params=None, **kwargs):
        if params is None:
            params = {}
        params['key'] = self.api_key
        return super().get(endpoint, params=params, **kwargs)

        

    @log_io_to_json
    def search(self, query:str, results:int = 10, **kwargs):
        '''Search youtube videos'''
        return yts.VideosSearch(query, limit = results, **kwargs).result()
    

    @log_io_to_json
    def get_transcript(self, video_id: str) -> str:
        '''Get video transcript'''
        return yts.Transcript.get(video_id)
        
        
    

    @log_io_to_json
    def get_comments(self, video_id:str, max_results:int = 20, order = 'relevance', text_format = 'plainText', search_terms:str = None, **kwargs):
        '''Get comments from a given YouTube video. Comment replies not included'''

        if order not in ['relevance', 'time']:
            raise ValueError("Order must be either 'relevance' or 'time'")

        if text_format not in ['html', 'plainText']:
            raise ValueError("textFormat must be either 'html' or 'plainText'")

        params = {'videoId': video_id, 'part': 'snippet',
                  'maxResults': max_results, 'order':order,
                  'textFormat':text_format, 'searchTerms':search_terms,
                  **kwargs
                  }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self.get('commentThreads', params = params).json()
        
        return response



    @log_io_to_json
    def get_all_comments(self, video_id:str, **kwargs):
        '''Get all comments from a given YouTube video. Replies not included'''
        all_comments = []
        next_page_token = None

        while True:
            response = self.get_comments(video_id, max_results=100, pageToken=next_page_token, **kwargs)
            all_comments.extend(response.get('items', []))
            next_page_token = response.get('nextPageToken')
            
            if not next_page_token:
                break

        return all_comments
    

  #  @log_io_to_json
    def get_comment_replies(self, video_id: str):
        '''Retrieve replies from a given YouTube comment'''
        raise NotImplementedError('This method needs to be implemented')
        comments = yts.Comments(video_id)

        while comments.hasMoreComments:
            comments.getNextComments()
            
        return comments.comments["result"]
    

    def get_all_comment_replies(self, video_id: str):
        '''Retrieve all replies from a given YouTube comment'''
        raise NotImplementedError('This method needs to be implemented')
        comments = yts.Comments(video_id)

        while comments.hasMoreComments:
            comments.getNextComments()
            
        return comments.comments["result"]