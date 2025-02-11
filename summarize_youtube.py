import os
from googleapiclient.discovery import build
from pytube import YouTube
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# YouTube API setup
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Gemini API setup
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

def get_latest_videos(channel_id, max_results=5):
    """Fetch latest videos from YouTube channel."""
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=max_results,
        order="date",
        type="video"
    )
    return request.execute()['items']

def get_video_transcript(video_id):
    """Extract transcript using best available method."""
    # Pytube attempt
    try:
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
        caption = None
        
        # Try different caption tracks in priority order
        for code in ['en', 'a.en', 'en-US', 'en-GB']:
            if code in yt.captions:
                caption = yt.captions[code]
                break
                
        if not caption:
            return None
            
        return caption.generate_srt_captions()
    except Exception as e:
        print(f"Pytube error for {video_id}: {e}")
    
    # Fallback to youtube_transcript_api
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return " ".join(entry['text'] for entry in transcript)
    except Exception as e:
        print(f"Transcript API error for {video_id}: {e}")
        return None

def summarize_text(text):
    """Summarize text using Gemini API with rate limiting and retries."""
    model = genai.GenerativeModel('gemini-pro')
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                f"Summarize this YouTube video transcript in 3 bullet points:\n{text[:30000]}",
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
                }
            )
            
            response.resolve()
            
            if response.prompt_feedback.block_reason:
                print(f"Content blocked: {response.prompt_feedback.block_reason}")
                return None
                
            return response.text.strip()
            
        except Exception as e:
            if 'quota' in str(e).lower() or 'exhausted' in str(e).lower():
                print(f"API quota exceeded: {str(e)}")
                return None
                
            print(f"API attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
            else:
                print("Max retries reached. Could not summarize content.")
                return None

def main():
    videos = get_latest_videos(CHANNEL_ID)
    
    for video in videos:
        video_id = video['id']['videoId']
        if transcript := get_video_transcript(video_id):
            if summary := summarize_text(transcript):
                print(f"\nTitle: {video['snippet']['title']}")
                print(f"Summary:\n{summary}\n")

if __name__ == "__main__":
    main()
