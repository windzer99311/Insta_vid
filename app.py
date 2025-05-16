import re
import os
import instaloader
import tempfile
import requests
from urllib.parse import urlparse
import streamlit as st

def validate_instagram_url(url):
    """
    Validates if the provided URL is a valid Instagram URL.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    instagram_regex = r'(https?://)?(www\.)?instagram\.com/([A-Za-z0-9_.]+(/)?(p|tv|reel|stories)/[A-Za-z0-9_-]+)'
    return bool(re.match(instagram_regex, url))

def extract_shortcode(url):
    """
    Extract the shortcode (post ID) from an Instagram URL.
    
    Args:
        url (str): The Instagram URL
        
    Returns:
        str: The shortcode or None if not found
    """
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.strip('/').split('/')
    
    # Handle different URL formats
    if len(path_segments) >= 2:
        if path_segments[0] in ['p', 'tv', 'reel']:
            return path_segments[1]
        elif path_segments[0] and path_segments[1] in ['p', 'tv', 'reel']:
            return path_segments[2]
    
    return None

def download_instagram_video(url, output_dir):
    """
    Download a video from Instagram post URL.
    
    Args:
        url (str): Instagram post URL
        output_dir (str): Directory to save the video
        
    Returns:
        dict: Video information including path, caption, and username
    """
    # Extract the shortcode from URL
    shortcode = extract_shortcode(url)
    if not shortcode:
        st.error("Could not extract post ID from URL.")
        return None

    # Initialize Instaloader instance
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    
    try:
        # Try to download anonymously first
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Check if it's a video post
        if not post.is_video:
            st.error("This post does not contain a video.")
            return None
            
        # Get post details
        username = post.owner_username
        caption = post.caption if post.caption else "No caption"
        
        # Download the video
        temp_filename = f"{username}_{shortcode}.mp4"
        video_path = os.path.join(output_dir, temp_filename)
        
        # Download video directly using requests if needed
        if hasattr(post, 'video_url'):
            video_url = post.video_url
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                with open(video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
        else:
            # Fallback to instaloader's download
            L.download_post(post, target=output_dir)
            # Find the downloaded video file
            for file in os.listdir(output_dir):
                if file.endswith('.mp4') and shortcode in file:
                    video_path = os.path.join(output_dir, file)
                    break
        
        return {
            'video_path': video_path,
            'caption': caption,
            'username': username
        }
        
    except instaloader.exceptions.LoginRequiredException:
        st.error("This post is private. You need to log in to download it.")
        return None
    except instaloader.exceptions.InstaloaderException as e:
        st.error(f"Instaloader error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None
