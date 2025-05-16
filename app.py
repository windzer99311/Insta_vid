import streamlit as st
import os
import tempfile
from datetime import datetime
from utils import download_instagram_video, is_valid_instagram_url, get_shortcode_from_url

# Set page configuration
st.set_page_config(
    page_title="Instagram Video Downloader",
    page_icon="📹",
    layout="centered"
)

# Load external CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state for download history
if 'download_history' not in st.session_state:
    st.session_state.download_history = []

# Override Streamlit's default text colors
    st.markdown("""
        <style>
        .stAlert p {
            color: #000000 !important;
        }
        .streamlit-expanderHeader {
            color: #000000 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # App header with attractive styling
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/132px-Instagram_logo_2016.svg.png", width=80)

# Attractive title with gradient
st.markdown('<h1 class="app-title">Instagram Video Downloader</h1>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">Download your favorite Instagram videos with just one click</p>', unsafe_allow_html=True)

# Create tabs for navigation
tab1, tab2 = st.tabs(["Download", "History"])

with tab1:
    # Main content - Downloader tab
    st.header("Download Instagram Videos")
    
    # Instructions
    st.markdown("""
    ### How to use:
    1. Paste an Instagram video URL (post or reel) below
    2. Click the Download button
    3. Preview the video and download it to your device
    """)
    
    # Input field for Instagram URL with paste button
    url_container = st.container()
    with url_container:
        col1, col2 = st.columns([5, 1])
        with col1:
            instagram_url = st.text_input("Enter Instagram Video URL:", placeholder="https://www.instagram.com/p/...", label_visibility="visible")
        with col2:
            st.markdown('<div style="margin-top: 25px;">', unsafe_allow_html=True)
            if st.button("📋 Paste", use_container_width=True):
                try:
                    import pyperclip
                    clipboard_text = pyperclip.paste()
                    if is_valid_instagram_url(clipboard_text):
                        st.session_state['instagram_url'] = clipboard_text
                        st.rerun()
                except:
                    st.error("Could not access clipboard")
    
    # Create containers for status and video
    status_container = st.empty()
    video_container = st.empty()
    download_container = st.empty()
    
    # Download button
    if st.button("Download", type="primary"):
        if not instagram_url:
            status_container.error("Please enter an Instagram URL.")
        elif not is_valid_instagram_url(instagram_url):
            status_container.error("Invalid Instagram URL. Please enter a valid Instagram post or reel URL.")
        else:
            # Show processing message
            status_container.info("Processing... Please wait.")
            
            try:
                # Download the video
                video_path = download_instagram_video(instagram_url)
                
                if video_path:
                    # Display success message
                    status_container.success("Video downloaded successfully!")
                    
                    # Add to download history
                    shortcode = get_shortcode_from_url(instagram_url)
                    st.session_state.download_history.append({
                        "url": instagram_url,
                        "shortcode": shortcode,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "file_path": video_path
                    })
                    
                    # Read the video file once
                    with open(video_path, "rb") as video_file:
                        video_bytes = video_file.read()
                    
                    # Clear previous display
                    video_container.empty()
                    
                    # Use a horizontal layout with the video and download button side by side
                    cols = video_container.columns([3, 2])
                    
                    # Display video in the left column with proper frame
                    with cols[0]:
                        st.markdown('<div style="border:1px solid #ddd; border-radius:5px; padding:10px; background-color:#f0f0f0;">', unsafe_allow_html=True)
                        st.video(video_bytes)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add styled download button in the right column
                    with cols[1]:
                        st.markdown('<div style="height:30px"></div>', unsafe_allow_html=True)  # Add some spacing for alignment
                        st.download_button(
                            label="⬇️ Download Video",
                            data=video_bytes,
                            file_name=os.path.basename(video_path),
                            mime="video/mp4",
                            key="video_download",
                            use_container_width=True
                        )
                        
                        # Add file info
                        file_size = round(len(video_bytes) / (1024 * 1024), 2)  # Size in MB
                        st.markdown(f"<div style='padding:5px; margin-top:5px;'><strong>Size:</strong> {file_size} MB<br><strong>Format:</strong> MP4</div>", unsafe_allow_html=True)
                    
                    # Clear the download container as we've integrated it
                    download_container.empty()
                else:
                    status_container.error("Could not download the video. Make sure the URL contains a video and is publicly accessible.")
            
            except Exception as e:
                status_container.error(f"An error occurred: {str(e)}")

with tab2:
    # History tab
    st.header("Download History")
    
    if len(st.session_state.download_history) == 0:
        st.info("You haven't downloaded any videos yet.")
    else:
        # Display download history
        for i, item in enumerate(reversed(st.session_state.download_history)):
            st.markdown(f"**URL:** {item['url']}")
            st.markdown(f"**Downloaded:** {item['timestamp']}")
            
            # Add download button if file still exists
            if os.path.exists(item["file_path"]):
                with open(item["file_path"], "rb") as file:
                    st.download_button(
                        label="Download Again",
                        data=file.read(),
                        file_name=os.path.basename(item["file_path"]),
                        mime="video/mp4",
                        key=f"history_download_{i}"
                    )
            else:
                st.error("File no longer available")
            
            st.markdown("---")

# Footer
st.markdown("---")
st.caption("Instagram Video Downloader - Use responsibly and respect copyright")
st.caption("This app only works with public Instagram posts and reels")