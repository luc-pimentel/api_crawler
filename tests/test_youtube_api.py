import pytest
from api_crawler import YoutubeAPI


@pytest.fixture(scope="module")
def youtube():
    return YoutubeAPI()



def test_youtube_search(youtube):

    response = youtube.search('Best Python Courses')
        
    # Check if 'result' key is in the response
    assert 'result' in response, "'result' key not found in the response"
        
    # Check if the value of 'result' is a list
    assert isinstance(response['result'], list), "'result' is not a list"



def test_youtube_search_channel(youtube):

    response = youtube.search_channel('Python')

    # Check if 'result' key is in the response
    assert 'result' in response, "'result' key not found in the response"
        
    # Check if the value of 'result' is a list
    assert isinstance(response['result'], list), "'result' is not a list"
    




def test_youtube_get_videos_from_channel(youtube):
    channel_id = 'UCdu8D9NV9NP1iVPTYlenORw'
    n_videos = 5
    response = youtube.get_videos_from_channel(channel_id, n_videos)
        
    # Check if the value of 'result' is a list
    assert isinstance(response, list), "Response is not a list"
    
    # Check if the list has a size of 5
    assert len(response) == 5, "List size is not 5"



def test_youtube_get_transcript(youtube):
    video_id = 'GIRkQQHzsxI'
    response = youtube.get_transcript(video_id, timestamps=True)
    
    # Check if 'segments' key is in the response
    assert 'segments' in response, "'segments' key not found in the response"
    
    # Check if the value of 'segments' is a list
    assert isinstance(response['segments'], list), "'segments' is not a list"




@pytest.mark.parametrize("include_metadata", [True, False])
def test_youtube_get_comments(youtube, include_metadata):
    video_id = 'GIRkQQHzsxI'
    response = youtube.get_comments(video_id, include_metadata=include_metadata)
    
    if include_metadata:
        assert isinstance(response, dict), "Response is not a dict"
        assert 'items' in response, "'items' key not found in the response"
        assert isinstance(response['items'], list), "'items' is not a list"
        assert len(response['items']) > 0, "List size is not greater than 0"
    else:
        assert isinstance(response, list), "Response is not a list"
        assert all(isinstance(item, str) for item in response), "Not all items in the response are strings"



@pytest.mark.parametrize("include_metadata", [True, False])
def test_youtube_get_all_comments(youtube, include_metadata):
    video_id = 'GIRkQQHzsxI'
    response = youtube.get_all_comments(video_id, include_metadata=include_metadata)

    if include_metadata:
        assert isinstance(response, list), "Response is not a list"
        assert len(response) > 0, "List size is not greater than 0"
        assert all(isinstance(item, dict) for item in response), "Not all items in the response are dicts"
    else:
        assert isinstance(response, list), "Response is not a list"
        assert len(response) > 0, "List size is not greater than 0"
        assert all(isinstance(item, str) for item in response), "Not all items in the response are strings"



def test_youtube_get_comment_replies(youtube):
    comment_id = 'UgzmxQVvj6zVCjC4re54AaABAg'
    response = youtube.get_comment_replies(comment_id)
    
    assert isinstance(response, dict), "Response is not a dict"
    assert 'items' in response, "'items' key not found in the response"
    assert isinstance(response['items'], list), "'items' is not a list"
    


def test_youtube_get_all_comment_replies(youtube):
    comment_id = 'UgzmxQVvj6zVCjC4re54AaABAg'
    response = youtube.get_all_comment_replies(comment_id)
    
    assert isinstance(response, list), "Response is not a list"
    assert len(response) > 0, "List size is not greater than 0"
