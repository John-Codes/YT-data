from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
load_dotenv()

# Set up YouTube Data API
# get youtube api key from .env file:
YOUTUBE_API_KEY=os.getenv('YOUTUBE_API_KEY')


youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def get_channel_id(handle):
    """Fetch the channel ID from a YouTube handle."""
    request = youtube.search().list(
        part="snippet",
        type="channel",
        q=handle
    )
    response = request.execute()
    if response['items']:
        return response['items'][0]['id']['channelId']
    return None

channel_id = get_channel_id('@CryptoBanterGroup')
print(channel_id)
