from .base import BaseSearchAPI
from lake.logger import log_io_to_json
import youtubesearchpython as yts



class YoutubeAPI(BaseSearchAPI):
    def __init__(self):
        pass
        

    #@log_io_to_json
    def search(self, query:str, results:int = 10, **kwargs):
        '''Search youtube videos'''
        return yts.VideosSearch(query, limit = results, **kwargs).result()
    

    #@log_io_to_json
    def get_transcript(self, video_id: str) -> str:
        '''Get video transcript'''
        return yts.Transcript.get(video_id)
        
        
    

    #@log_io_to_json
    def get_comments(self, video_id:str):
        '''Get video comments (only the first 20 based on the python class)'''
        comments_response = yts.Comments.get(video_id)

        comments = [{'video':video_id, 'content':comment['content'],'votes':comment['votes']['simpleText'],
                     'published':comment['published']} for comment in comments_response['result']]

        return comments
    
#    @log_io_to_json
    def get_channels(self, channel_name: str):
        '''Search for channels on YouTube'''

        channels_search = yts.Channel(channel_name)
        return channels_search.result()
    

 #   @log_io_to_json
    def get_all_videos_from_channel(self, channel_id: str):
        '''Retrieve all videos from a given YouTube channel'''


        playlist = yts.Playlist(yts.playlist_from_channel_id(channel_id))

        while playlist.hasMoreVideos:
            playlist.getNextVideos()

        return playlist.videos
    

  #  @log_io_to_json
    def get_all_comments(self, video_id: str):
        '''Retrieve all comments from a given YouTube video'''
        comments = yts.Comments(video_id)

        while comments.hasMoreComments:
            comments.getNextComments()
            
        return comments.comments["result"]