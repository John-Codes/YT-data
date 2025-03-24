import os
import asyncio
import re
import httpx
from googleapiclient.discovery import build
from pytube import YouTube
from dotenv import load_dotenv
import time
import random
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()

# YouTube API setup
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Gemini API setup
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

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
    """Extract transcript using youtube_transcript_api."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return " ".join(entry['text'] for entry in transcript)
    except Exception as e:
        print(f"Transcript API error for {video_id}: {e}")
        return None

async def summarize_text(text):
    """Summarize text using Ollama manager."""
    from Ollama_manager import OllamaService
    max_retries = 3
    retry_delay = random.randint(1, 3)
    
    for attempt in range(max_retries):
        try:
            ollama = OllamaService()
            ollama.manual_start()
            model = "deepseek-r1:32b"
            ollama.load(model)
            messages = [
                {"role": "user", "content": f"Summarize this YouTube video transcript and cite the sources of the info be consice and use laymans terms also dont add comments or promotions.Summarize the video content by providing only key insights and updates related to market trends, economic developments, and financial news. Exclude any references to personal promotions, sponsored content, course advertisements, or unrelated discussions. Keep the summary concise and strictly relevant to the market analysis Do not use mark up or list just a plain text paragraph of sentences no lists :\n{text[:30000]}"}
            ]
            summary = ollama.get_full_response(model, messages)
            summary = remove_think_tags(summary)
            ollama.unload(model)
            ollama.manual_stop()
            return summary.strip()
        except Exception as e:
            print(f"Ollama attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
    
    print("Ollama failed to summarize the text.")
    return None

@staticmethod
def remove_think_tags(text):
    # Define the pattern to match text between <think> and </think> tags
    pattern = re.compile(r'<think>\n.*?\n</think>', re.DOTALL)

    # Substitute the matched pattern with an empty string
    result = pattern.sub('', text)

    return result

async def main():
    print("Fetching latest videos...")
    videos = get_latest_videos(CHANNEL_ID)
    print(f"Found {len(videos)} videos.")
    
    for video in videos:
        video_id = video['id']['videoId']
        print(f"Processing video ID: {video_id}")
        if transcript := get_video_transcript(video_id):
            print(f"Transcript fetched for video ID: {video_id}")
            if summary := await summarize_text(transcript):
                print(f"\nTitle: {video['snippet']['title']}")
                print(f"Summary:\n{summary}\n")
            else:
                print(f"Failed to summarize video ID: {video_id}")
        else:
            print(f"Failed to fetch transcript for video ID: {video_id}")

if __name__ == "__main__":
    asyncio.run(main())
