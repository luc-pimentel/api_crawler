from ._base import BaseSearchAPI, BaseRestfulAPI
from ..data_lake.logger import log_io_to_json
import youtubesearchpython as yts
from ..exceptions import NoAPIKeyException
from decouple import config
from typing import Union
import os
import warnings



YOUTUBE_API_KEY = config('YOUTUBE_API_KEY', None)


class YoutubeAPI(BaseRestfulAPI, BaseSearchAPI):
    base_url: str = 'https://www.googleapis.com/youtube/v3/'
    api_error_message: str = "An API key is necessary for this method. Please visit the YouTube Data API v3 to obtain one: https://developers.google.com/youtube/v3/"

    def __init__(self, api_key: str = YOUTUBE_API_KEY):

        api_key = self._get_api_key(api_key, "YOUTUBE_API_KEY",
                                    action='warn',
                                    message="""No Youtube V3 API key provided. Some methods may not work.
Please set the YOUTUBE_API_KEY environment variable using os.environ['YOUTUBE_API_KEY'] or pass it to the object via the api_key parameter.""")
        
        self.api_key = api_key
        super().__init__()
        
    
    def _check_api_key(self):
        if self.api_key is None:
            raise NoAPIKeyException(self.api_error_message)


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
    def search_channel(self, query, limit=10, region=None, **kwargs):
        channels_search = yts.ChannelsSearch(query, limit=limit, region=region, **kwargs)
        return channels_search.result()



    @log_io_to_json
    def get_videos_from_channel(self, channel_id: str, n_videos: Union[int,str] = 'all'):

        if n_videos != 'all' and not isinstance(n_videos, int):
            raise ValueError("n_videos must be 'all' or an integer")

        playlist = yts.Playlist(yts.playlist_from_channel_id(channel_id))

        while playlist.hasMoreVideos:
            if n_videos != 'all' and len(playlist.videos) >= n_videos:
                break

            playlist.getNextVideos()

        return playlist.videos[:n_videos] if n_videos != 'all' else playlist.videos



    @log_io_to_json
    def get_transcript(self, video_id: str) -> str:
        '''Get video transcript'''
        return yts.Transcript.get(video_id)
        
        
    

    @log_io_to_json
    def get_comments(self, video_id:str, max_results:int = 20, include_replies:bool = True, order = 'relevance', text_format = 'plainText', search_terms:str = None, **kwargs):
        '''Get comments from a given YouTube video. Comment replies not included'''
        self._check_api_key()

        if order not in ['relevance', 'time']:
            raise ValueError("Order must be either 'relevance' or 'time'")

        if text_format not in ['html', 'plainText']:
            raise ValueError("textFormat must be either 'html' or 'plainText'")

        part = 'snippet, replies' if include_replies else 'snippet'


        params = {'videoId': video_id, 'part': part,
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
        self._check_api_key()
        

        all_comments = []
        next_page_token = None

        while True:
            response = self.get_comments(video_id, max_results=100, pageToken=next_page_token, **kwargs)
            all_comments.extend(response.get('items', []))
            next_page_token = response.get('nextPageToken')
            
            if not next_page_token:
                break

        return all_comments
    

    @log_io_to_json
    def get_comment_replies(self, comment_id:str, max_results:int = 20, **kwargs):
        self._check_api_key()

        params = {'parentId': comment_id, 'part': 'snippet',
                  'maxResults': max_results, **kwargs}

        comments_response = self.get('comments', params = params)
        
        return comments_response.json()
        

    @log_io_to_json
    def get_all_comment_replies(self, comment_id: str, **kwargs):
        '''Retrieve all replies from a given YouTube comment'''
        self._check_api_key()

        all_comments = []
        next_page_token = None

        while True:
            response = self.get_comment_replies(comment_id, max_results=100,
                                    pageToken=next_page_token, **kwargs)
        
            all_comments.extend(response.get('items', []))
            next_page_token = response.get('nextPageToken')
        
            if not next_page_token:
                break
                
        return all_comments