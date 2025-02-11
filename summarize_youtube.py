import os
from googleapiclient.discovery import build
from pytube import YouTube
import google.generativeai as genai

# Set up YouTube Data API
#get api key from .env file
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)


#get channel id from .env file
CHANNEL_ID = os.getenv('CHANNEL_ID')
# Set up Gemini API
#get api key from .env file
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)

def get_latest_videos(channel_id, max_results=5):
    """Fetch the latest videos from a YouTube channel."""
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=max_results,
        order="date",
        type="video"
    )
    response = request.execute()
    return response['items']

def get_video_transcript(video_id):
    """Extract the transcript from a YouTube video.
    
    First tries using pytube to retrieve manually created or auto-generated captions.
    If that fails, falls back to using youtube_transcript_api.
    """
    # Attempt using pytube captions
    try:
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
        caption = yt.captions.get_by_language_code('en')
        if not caption:
            # Attempt auto-generated English captions
            caption = yt.captions.get_by_language_code('a.en')
        if caption:
            return caption.generate_srt_captions()
    except Exception as e:
        print(f"Error with pytube for video {video_id}: {e}")
    
    # Fallback using youtube_transcript_api
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        transcript = "\n".join(entry['text'] for entry in transcript_list)
        return transcript
    except Exception as e:
        print(f"Error using YouTubeTranscriptApi for video {video_id}: {e}")
        return None

def summarize_text(text):
    """Summarize the text using Gemini API."""
    try:
        prompt = f"Summarize the following text in three sentences:\n\n{text}"
        response = genai.generate_text(prompt)
        return response.text
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return None

def main():

    channel_id = CHANNEL_ID 
    videos = get_latest_videos(channel_id)
    
    for video in videos:
        video_id = video['id']['videoId']
        transcript = get_video_transcript(video_id)
        # print(f"\033[92m{transcript}\033[0m")
        if transcript:
            summary = summarize_text(transcript)
            print(f"Video Title: {video['snippet']['title']}")
            print(f"Summary: {summary}\n")

if __name__ == "__main__":
    main()
