import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
import io
import requests
import time
import numpy as np
from streamlit_drawable_canvas import st_canvas

# ===========================================
# PAGE CONFIGURATION - MUST BE FIRST STREAMLIT COMMAND
# ===========================================
st.set_page_config(
    page_title="LyTa Studio Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': "### LyTa Studio Pro v1.0\nProfessional AI-Powered Image Editing Suite"
    }
)

# ===========================================
# CUSTOM CSS - COMES RIGHT AFTER PAGE CONFIG
# ===========================================
st.markdown("""
<style>
    /* Main Theme Colors */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #10b981;
        --background: #f8fafc;
        --surface: #ffffff;
        --text: #1e293b;
        --text-secondary: #64748b;
        --border: #e2e8f0;
        --shadow: 0 1px 3px rgba(0,0,0,0.1);
        --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: var(--text) !important;
    }
    
    h1 {
        background: linear-gradient(90deg, var(--primary) 0%, var(--primary-dark) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Cards and Containers */
    .card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
        margin-bottom: 1rem;
    }
    
    .card-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }
    
    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border-bottom: 2px solid var(--border);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
        transition: all 0.3s ease;
        color: var(--text-secondary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary);
        color: white !important;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(90deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        opacity: 0.9;
    }
    
    .secondary-button {
        background: var(--secondary) !important;
    }
    
    /* File Uploader */
    .uploadedFile {
        border: 2px dashed var(--border) !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        background: var(--surface) !important;
    }
    
    /* Sliders and Inputs */
    .stSlider {
        padding: 1rem 0;
    }
    
    .stSelectbox, .stTextArea, .stTextInput {
        background: var(--surface);
        border-radius: 8px;
        border: 1px solid var(--border);
    }
    
    /* Progress and Status */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid var(--primary);
    }
    
    /* Image Containers */
    .image-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow);
        margin: 1rem 0;
        max-width: 100% !important;
    }
    
    /* Image sizing */
    .stImage > img, .stImage > div > img {
        max-width: 800px !important;
        max-height: 600px !important;
        width: auto !important;
        height: auto !important;
        object-fit: contain !important;
        margin: 0 auto !important;
        display: block !important;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        background: var(--surface);
        border: 1px solid var(--border);
    }
    
    .status-badge.success {
        background: #d1fae5;
        color: #065f46;
        border-color: #a7f3d0;
    }
    
    .status-badge.warning {
        background: #fef3c7;
        color: #92400e;
        border-color: #fde68a;
    }
    
    .status-badge.info {
        background: #dbeafe;
        color: #1e40af;
        border-color: #bfdbfe;
    }
    
    /* Loading Spinner Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# ===========================================
# REST OF IMPORTS (after Streamlit commands)
# ===========================================
from services import (
    lifestyle_shot_by_image,
    lifestyle_shot_by_text,
    add_shadow,
    create_packshot,
    enhance_prompt,
    generative_fill,
    generate_hd_image,
    erase_foreground
)
from services.erase_foreground import erase_foreground

# ===========================================
# SESSION STATE MANAGEMENT
# ===========================================
def initialize_session_state():
    """Initialize session state variables."""
    # Load environment variables
    load_dotenv(verbose=True)
    
    defaults = {
        'api_key': os.getenv('BRIA_API_KEY'),
        'generated_images': [],
        'current_image': None,
        'pending_urls': [],
        'edited_image': None,
        'original_prompt': "",
        'enhanced_prompt': None,
        'active_tab': 0,
        'processing': False,
        'last_result': None,
        'generation_history': [],
        'image_quality': 85,  # Default quality for resizing
        'display_width': 800   # Default display width
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ===========================================
# UTILITY FUNCTIONS
# ===========================================
def resize_image(image_bytes, max_width=800, quality=85):
    """Resize image to reduce file size for display."""
    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(image_bytes))
        
        # Get original dimensions
        original_width, original_height = img.size
        
        # Calculate new dimensions maintaining aspect ratio
        if original_width > max_width:
            ratio = max_width / original_width
            new_width = max_width
            new_height = int(original_height * ratio)
            
            # Resize image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed (for JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                # Composite the image onto the background
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save to bytes with reduced quality
        output_bytes = io.BytesIO()
        img.save(output_bytes, format='JPEG', quality=quality, optimize=True)
        
        # Get file size
        file_size_kb = len(output_bytes.getvalue()) / 1024
        
        return output_bytes.getvalue(), file_size_kb, img.size
    except Exception as e:
        st.error(f"❌ Error resizing image: {str(e)}")
        return image_bytes, len(image_bytes) / 1024, None

def download_image(url, resize_for_display=True, max_width=800, quality=85):
    """Download image from URL and return as bytes."""
    try:
        # Add timeout and headers for better compatibility
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        original_bytes = response.content
        original_size_kb = len(original_bytes) / 1024
        
        # Check if we should resize for display
        if resize_for_display:
            resized_bytes, resized_size_kb, new_dimensions = resize_image(
                original_bytes, 
                max_width=max_width, 
                quality=quality
            )
            
            # Log size reduction
            reduction_percent = ((original_size_kb - resized_size_kb) / original_size_kb) * 100
            st.info(f"📏 Image optimized: {original_size_kb:.1f}KB → {resized_size_kb:.1f}KB ({reduction_percent:.1f}% smaller)")
            
            return {
                'original': original_bytes,
                'resized': resized_bytes,
                'original_size_kb': original_size_kb,
                'resized_size_kb': resized_size_kb,
                'dimensions': new_dimensions
            }
        else:
            return {
                'original': original_bytes,
                'resized': original_bytes,
                'original_size_kb': original_size_kb,
                'resized_size_kb': original_size_kb,
                'dimensions': None
            }
            
    except requests.exceptions.Timeout:
        st.error("❌ Timeout error downloading image. The server is taking too long to respond.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ HTTP error downloading image: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Error downloading image: {str(e)}")
        return None

def extract_image_urls_from_response(result):
    """Extract image URLs from various API response formats."""
    image_urls = []
    
    if not result:
        return image_urls
    
    if isinstance(result, dict):
        # Format 1: {"result": [{"urls": ["url1", "url2"]}, ...]}
        if "result" in result and isinstance(result["result"], list):
            for item in result["result"]:
                if isinstance(item, dict):
                    if "urls" in item and isinstance(item["urls"], list):
                        image_urls.extend(item["urls"])
                    elif "result_url" in item:
                        image_urls.append(item["result_url"])
                elif isinstance(item, str):  # Direct URL in list
                    image_urls.append(item)
        
        # Format 2: {"urls": ["url1", "url2"]}
        elif "urls" in result and isinstance(result["urls"], list):
            image_urls.extend(result["urls"])
        
        # Format 3: {"result_url": "url"}
        elif "result_url" in result:
            image_urls.append(result["result_url"])
        
        # Format 4: {"result_urls": ["url1", "url2"]}
        elif "result_urls" in result and isinstance(result["result_urls"], list):
            image_urls.extend(result["result_urls"])
        
        # Format 5: Direct URL in dict
        elif "url" in result:
            image_urls.append(result["url"])
    
    elif isinstance(result, list):
        # Direct list of URLs or response objects
        for item in result:
            if isinstance(item, str):
                image_urls.append(item)
            elif isinstance(item, dict):
                if "urls" in item and isinstance(item["urls"], list):
                    image_urls.extend(item["urls"])
                elif "result_url" in item:
                    image_urls.append(item["result_url"])
                elif "url" in item:
                    image_urls.append(item["url"])
    
    elif isinstance(result, str):
        # Direct URL string
        image_urls.append(result)
    
    # Clean up URLs (remove query parameters if they cause issues)
    cleaned_urls = []
    for url in image_urls:
        if url:
            # Basic URL validation
            if url.startswith(('http://', 'https://')):
                cleaned_urls.append(url)
    
    return cleaned_urls

def create_info_box(title, content, icon="ℹ️"):
    """Create a styled information box."""
    st.markdown(f"""
    <div class="card">
        <div class="card-header">
            <span>{icon}</span>
            <span>{title}</span>
        </div>
        <p style="color: var(--text-secondary); margin-bottom: 0;">{content}</p>
    </div>
    """, unsafe_allow_html=True)

def create_status_badge(status, message):
    """Create a status badge for different states."""
    color_class = {
        "success": "success",
        "warning": "warning",
        "info": "info",
        "error": "error"
    }.get(status, "info")
    
    icons = {
        "success": "✅",
        "warning": "⚠️",
        "info": "ℹ️",
        "error": "❌"
    }
    
    st.markdown(f"""
    <div class="status-badge {color_class}">
        <span>{icons.get(status, '')} {message}</span>
    </div>
    """, unsafe_allow_html=True)

def check_generated_images():
    """Check if pending images are ready and update the display."""
    if st.session_state.pending_urls:
        ready_images = []
        still_pending = []
        
        for url in st.session_state.pending_urls:
            try:
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    ready_images.append(url)
                else:
                    still_pending.append(url)
            except:
                still_pending.append(url)
        
        st.session_state.pending_urls = still_pending
        
        if ready_images:
            st.session_state.edited_image = ready_images[0]
            if len(ready_images) > 1:
                st.session_state.generated_images.extend(ready_images)
            return True
    return False

# ===========================================
# MAIN APPLICATION
# ===========================================
def main():
    # Initialize session state
    initialize_session_state()
    
    # ===========================================
    # HEADER SECTION
    # ===========================================
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("# 🎨 LyTa Studio Pro")
        st.markdown("### LyTa AI-Powered Image Editing Suite")
    with col3:
        st.markdown("---")
        st.caption("⚡ Powered by BRIA AI")
        st.caption("v1.0 • Enterprise Ready")
    
    st.markdown("---")
    
    # ===========================================
    # SIDEBAR - SETTINGS & INFO
    # ===========================================
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # API Key Section
        with st.expander("🔑 API Settings", expanded=True):
            api_key = st.text_input(
                "BRIA API Key",
                value=st.session_state.api_key or "",
                type="password",
                help="Enter your BRIA AI API key to access all features"
            )
            if api_key:
                st.session_state.api_key = api_key
                st.success("✅ API Key Configured")
            else:
                st.warning("⚠️ API Key Required")
        
        st.markdown("---")
        
        # Image Display Settings
        with st.expander("🖼️ Display Settings", expanded=True):
            st.session_state.display_width = st.slider(
                "Max Display Width (px)",
                min_value=400,
                max_value=1200,
                value=800,
                step=100,
                help="Maximum width for displayed images"
            )
            
            st.session_state.image_quality = st.slider(
                "Image Quality (%)",
                min_value=50,
                max_value=100,
                value=85,
                step=5,
                help="Quality for displayed images (lower = smaller file size)"
            )
            
            st.info(f"Display: {st.session_state.display_width}px width at {st.session_state.image_quality}% quality")
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("## 📊 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Images Generated", len(st.session_state.get('generation_history', [])))
        with col2:
            if st.session_state.processing:
                st.metric("Status", "Processing", delta="Active")
            else:
                st.metric("Status", "Ready", delta="Idle")
        
        st.markdown("---")
        
        # Support & Documentation
        with st.expander("📚 Help & Resources"):
            st.info("""
            **Need Help?**
            - Use descriptive prompts for better results
            - Try different aspect ratios
            - Enable content moderation for safe generation
            
            **Image Optimization:**
            - Adjust display width in sidebar
            - Lower quality = smaller file size
            - Images are optimized for web display
            """)
        
        # Clear Results Button
        st.markdown("---")
        if st.button("🗑️ Clear All Results", use_container_width=True):
            st.session_state.generated_images = []
            st.session_state.edited_image = None
            st.session_state.pending_urls = []
            st.success("Results cleared!")
            st.rerun()
    
    # ===========================================
    # MAIN TABS NAVIGATION
    # ===========================================
    tab_labels = ["✨ Generate", "📸 Product Studio", "🎨 Generative Fill", "🧹 Cleanup"]
    tab_icons = ["✨", "📸", "🎨", "🧹"]
    
    tabs = st.tabs([f"{icon} {label}" for icon, label in zip(tab_icons, tab_labels)])
    
    # ===========================================
    # TAB 1: IMAGE GENERATION
    # ===========================================
    with tabs[0]:
        st.markdown("## ✨ AI Image Generation")
        st.markdown("Create stunning images from text descriptions using advanced AI models.")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Prompt Section
            with st.container():
                st.markdown("### 📝 Creative Prompt")
                prompt = st.text_area(
                    "Describe your vision...",
                    height=120,
                    placeholder="A serene mountain landscape at sunset with a crystal clear lake reflecting the sky...",
                    help="Be descriptive for better results. Include style, mood, and details.",
                    key="gen_prompt"
                )
                
                # Store original prompt
                if prompt != st.session_state.original_prompt:
                    st.session_state.original_prompt = prompt
                    st.session_state.enhanced_prompt = None
        
        with col2:
            # Generation Settings
            with st.container():
                st.markdown("### ⚙️ Settings")
                
                num_images = st.select_slider(
                    "Number of Images",
                    options=[1, 2, 3, 4],
                    value=1
                )
                
                aspect_ratio = st.selectbox(
                    "Aspect Ratio",
                    ["1:1 (Square)", "16:9 (Widescreen)", "9:16 (Portrait)", "4:3 (Standard)", "3:4 (Vertical)"]
                )
                
                style = st.selectbox(
                    "Art Style",
                    ["Photorealistic", "Digital Art", "Watercolor", "Oil Painting", 
                     "Sketch", "Anime", "Cyberpunk", "Minimalist"]
                )
        
        # Enhance Prompt Section
        col_a, col_b, col_c = st.columns([2, 1, 1])
        with col_a:
            if st.session_state.enhanced_prompt:
                st.markdown("### ✨ Enhanced Prompt")
                # Custom styled container with better visibility
                st.markdown(
                    f"""
                    <div style="
                        background-color: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 16px;
                        margin: 10px 0;
                        color: #212529;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        font-size: 14px;
                        line-height: 1.5;
                        white-space: pre-wrap;
                        max-height: 150px;
                        overflow-y: auto;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    ">
                        {st.session_state.enhanced_prompt}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        with col_b:
            if st.button("✨ Enhance Prompt", use_container_width=True, disabled=not prompt):
                if not prompt:
                    st.warning("Please enter a prompt to enhance")
                else:
                    with st.spinner("Enhancing prompt..."):
                        try:
                            result = enhance_prompt(st.session_state.api_key, prompt)
                            if result:
                                st.session_state.enhanced_prompt = result
                                st.success("Prompt enhanced!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

        # Generate Button
        col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
        with col_gen2:
            generate_btn = st.button(
                "🎨 Generate Images",
                type="primary",
                use_container_width=True,
                disabled=not st.session_state.api_key or not prompt
            )
            
            if generate_btn:
                if not st.session_state.api_key:
                    st.error("Please configure your API key in the sidebar")
                elif not prompt:
                    st.error("Please enter a prompt")
                else:
                    st.session_state.processing = True
                    with st.spinner("🎨 Creating your masterpiece..."):
                        try:
                            # Convert aspect ratio for API
                            aspect_map = {
                                "1:1 (Square)": "1:1",
                                "16:9 (Widescreen)": "16:9",
                                "9:16 (Portrait)": "9:16",
                                "4:3 (Standard)": "4:3",
                                "3:4 (Vertical)": "3:4"
                            }
                            
                            result = generate_hd_image(
                                prompt=st.session_state.enhanced_prompt or prompt,
                                api_key=st.session_state.api_key,
                                num_results=num_images,
                                aspect_ratio=aspect_map[aspect_ratio],
                                sync=True,
                                enhance_image=True,
                                medium="photography" if style == "Photorealistic" else "art",
                                content_moderation=True
                            )
                            
                            # Extract image URLs from response
                            image_urls = extract_image_urls_from_response(result)
                            
                            if image_urls:
                                st.session_state.generated_images = image_urls
                                st.session_state.edited_image = image_urls[0]
                                st.session_state.generation_history.append({
                                    "prompt": prompt,
                                    "urls": image_urls,
                                    "timestamp": time.time()
                                })
                                st.success(f"✨ Generated {len(image_urls)} image(s) successfully!")
                            else:
                                st.error("❌ No image URLs found in API response")
                                    
                        except Exception as e:
                            st.error(f"❌ Generation failed: {str(e)}")
                        finally:
                            st.session_state.processing = False
                            st.rerun()
        
        # Display Generated Images
        if st.session_state.get('generated_images'):
            st.markdown("---")
            st.markdown(f"## 🖼️ Generated Images ({len(st.session_state.generated_images)} total)")
            
            # Create columns for images
            num_cols = min(4, len(st.session_state.generated_images))
            cols = st.columns(num_cols)
            
            for idx, img_url in enumerate(st.session_state.generated_images):
                with cols[idx % num_cols]:
                    # Download and resize image
                    image_data = download_image(
                        img_url,
                        resize_for_display=True,
                        max_width=st.session_state.display_width,
                        quality=st.session_state.image_quality
                    )
                    
                    if image_data:
                        # Display resized image
                        st.image(
                            image_data['resized'],
                            caption=f"Image {idx+1}",
                            use_column_width=True
                        )
                        
                        # Show image info
                        with st.expander(f"📊 Image {idx+1} Info"):
                            col_info1, col_info2 = st.columns(2)
                            with col_info1:
                                st.metric("Original Size", f"{image_data['original_size_kb']:.1f}KB")
                            with col_info2:
                                st.metric("Display Size", f"{image_data['resized_size_kb']:.1f}KB")
                            
                            if image_data['dimensions']:
                                st.write(f"Display dimensions: {image_data['dimensions'][0]}x{image_data['dimensions'][1]}px")
                        
                        # Download buttons for both original and resized
                        col_dl1, col_dl2 = st.columns(2)
                        with col_dl1:
                            st.download_button(
                                "⬇️ Original",
                                image_data['original'],
                                f"original_image_{idx+1}.png",
                                "image/png",
                                use_container_width=True,
                                key=f"download_original_{idx}"
                            )
                        with col_dl2:
                            st.download_button(
                                "⬇️ Optimized",
                                image_data['resized'],
                                f"optimized_image_{idx+1}.jpg",
                                "image/jpeg",
                                use_container_width=True,
                                key=f"download_optimized_{idx}"
                            )
        
        # Display single edited image if available (for backward compatibility)
        elif st.session_state.edited_image:
            st.markdown("---")
            st.markdown("## 🖼️ Generated Image")
            
            image_data = download_image(
                st.session_state.edited_image,
                resize_for_display=True,
                max_width=st.session_state.display_width,
                quality=st.session_state.image_quality
            )
            
            if image_data:
                st.image(image_data['resized'], use_column_width=True)
                
                # Show image info
                with st.expander("📊 Image Info"):
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.metric("Original Size", f"{image_data['original_size_kb']:.1f}KB")
                    with col_info2:
                        st.metric("Display Size", f"{image_data['resized_size_kb']:.1f}KB")
                    
                    if image_data['dimensions']:
                        st.write(f"Display dimensions: {image_data['dimensions'][0]}x{image_data['dimensions'][1]}px")
                
                # Download buttons
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button(
                        "⬇️ Original Image",
                        image_data['original'],
                        "original_image.png",
                        "image/png",
                        use_container_width=True
                    )
                with col_dl2:
                    st.download_button(
                        "⬇️ Optimized Image",
                        image_data['resized'],
                        "optimized_image.jpg",
                        "image/jpeg",
                        use_container_width=True
                    )
    
    # ===========================================
    # TAB 2: PRODUCT STUDIO
    # ===========================================
    with tabs[1]:
        st.markdown("## 📸 Product Studio")
        st.markdown("Professional product photography and editing tools.")
        
        # File Upload with Drag & Drop
        uploaded_file = st.file_uploader(
            "📤 Upload Product Image",
            type=["png", "jpg", "jpeg"],
            help="Upload your product image (PNG, JPG, JPEG)"
        )
        
        if uploaded_file:
            col_img, col_edit = st.columns([2, 3])
            
            with col_img:
                # Image Preview (resized)
                st.markdown("### 📷 Original")
                # Resize uploaded image for display
                img = Image.open(uploaded_file)
                original_size = img.size
                
                # Resize for display
                if img.size[0] > st.session_state.display_width:
                    ratio = st.session_state.display_width / img.size[0]
                    new_size = (st.session_state.display_width, int(img.size[1] * ratio))
                    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Convert to bytes
                    buffer = io.BytesIO()
                    img_resized.save(buffer, format='JPEG', quality=st.session_state.image_quality)
                    buffer.seek(0)
                    
                    st.image(buffer, use_column_width=True)
                    st.caption(f"Display: {new_size[0]}x{new_size[1]}px (Original: {original_size[0]}x{original_size[1]}px)")
                else:
                    st.image(uploaded_file, use_column_width=True)
                
                # Quick Stats
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                with col_stats1:
                    st.metric("Dimensions", f"{img.width}×{img.height}")
                with col_stats2:
                    st.metric("Format", img.format)
                with col_stats3:
                    st.metric("Mode", img.mode)
            
            with col_edit:
                # Editing Options
                st.markdown("### 🛠️ Edit Options")
                
                edit_option = st.radio(
                    "Choose editing tool:",
                    ["Create Packshot", "Add Shadow", "Lifestyle Shot"],
                    horizontal=True
                )
                
                if edit_option == "Create Packshot":
                    bg_color = st.color_picker("Background Color", "#FFFFFF")
                    if st.button("Create Packshot", use_container_width=True):
                        with st.spinner("Creating packshot..."):
                            try:
                                result = create_packshot(
                                    st.session_state.api_key,
                                    uploaded_file.getvalue(),
                                    background_color=bg_color
                                )
                                if result:
                                    image_urls = extract_image_urls_from_response(result)
                                    if image_urls:
                                        st.session_state.edited_image = image_urls[0]
                                        st.success("Packshot created!")
                                        st.rerun()
                                    else:
                                        st.error("No image URL in response")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                
                elif edit_option == "Add Shadow":
                    shadow_type = st.selectbox("Shadow Type", ["Natural", "Drop"])
                    if st.button("Add Shadow", use_container_width=True):
                        with st.spinner("Adding shadow..."):
                            try:
                                result = add_shadow(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    shadow_type=shadow_type.lower()
                                )
                                if result:
                                    image_urls = extract_image_urls_from_response(result)
                                    if image_urls:
                                        st.session_state.edited_image = image_urls[0]
                                        st.success("Shadow added!")
                                        st.rerun()
                                    else:
                                        st.error("No image URL in response")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                
                elif edit_option == "Lifestyle Shot":
                    scene_desc = st.text_area("Describe the environment", 
                                            placeholder="A modern living room with soft lighting...")
                    if st.button("Generate Lifestyle Shot", use_container_width=True):
                        with st.spinner("Generating lifestyle shot..."):
                            try:
                                result = lifestyle_shot_by_text(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    scene_description=scene_desc,
                                    placement_type="automatic",
                                    num_results=1,
                                    sync=True
                                )
                                if result:
                                    image_urls = extract_image_urls_from_response(result)
                                    if image_urls:
                                        st.session_state.edited_image = image_urls[0]
                                        st.success("Lifestyle shot created!")
                                        st.rerun()
                                    else:
                                        st.error("No image URL in response")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
        
        # Display edited image if available
        if st.session_state.edited_image and uploaded_file:
            st.markdown("---")
            st.markdown("### 📸 Result")
            
            image_data = download_image(
                st.session_state.edited_image,
                resize_for_display=True,
                max_width=st.session_state.display_width,
                quality=st.session_state.image_quality
            )
            
            if image_data:
                st.image(image_data['resized'], use_column_width=True)
                
                # Show image info
                with st.expander("📊 Image Info"):
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.metric("Original Size", f"{image_data['original_size_kb']:.1f}KB")
                    with col_info2:
                        st.metric("Display Size", f"{image_data['resized_size_kb']:.1f}KB")
                
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button(
                        "⬇️ Download Original",
                        image_data['original'],
                        "result_original.png",
                        "image/png",
                        use_container_width=True
                    )
                with col_dl2:
                    st.download_button(
                        "⬇️ Download Optimized",
                        image_data['resized'],
                        "result_optimized.jpg",
                        "image/jpeg",
                        use_container_width=True
                    )
    
    # ===========================================
    # TAB 3: GENERATIVE FILL
    # ===========================================
    with tabs[2]:
        st.markdown("## 🎨 Generative Fill")
        st.markdown("Intelligently fill selected areas with AI-generated content.")
        
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="fill_upload")
        
        if uploaded_file:
            col1, col2 = st.columns(2)
            
            with col1:
                # Display original (resized)
                img = Image.open(uploaded_file)
                if img.size[0] > 600:
                    ratio = 600 / img.size[0]
                    new_size = (600, int(img.size[1] * ratio))
                    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
                    buffer = io.BytesIO()
                    img_resized.save(buffer, format='JPEG', quality=85)
                    buffer.seek(0)
                    st.image(buffer, caption="Original Image", use_column_width=True)
                else:
                    st.image(uploaded_file, caption="Original Image", use_column_width=True)
                
                # Get image for canvas
                img_width, img_height = img.size
                aspect_ratio = img_height / img_width
                canvas_width = min(img_width, 600)
                canvas_height = int(canvas_width * aspect_ratio)
                img_resized = img.resize((canvas_width, canvas_height))
                
                # Canvas for drawing mask
                stroke_width = st.slider("Brush Size", 1, 50, 20)
                canvas_result = st_canvas(
                    fill_color="rgba(255, 255, 255, 0.0)",
                    stroke_width=stroke_width,
                    stroke_color="#fff",
                    drawing_mode="freedraw",
                    background_image=img_resized,
                    height=canvas_height,
                    width=canvas_width,
                    key="canvas"
                )
                
                prompt = st.text_area("Describe what to generate", 
                                    placeholder="A beautiful flower, realistic clouds, etc.")
                
                if st.button("Generate", type="primary", use_container_width=True):
                    if not prompt:
                        st.warning("Please enter a description")
                    elif canvas_result.image_data is None:
                        st.warning("Please draw on the image first")
                    else:
                        with st.spinner("Generating..."):
                            try:
                                # Convert mask
                                mask_img = Image.fromarray(canvas_result.image_data.astype('uint8'), mode='RGBA')
                                mask_img = mask_img.convert('L')
                                mask_bytes = io.BytesIO()
                                mask_img.save(mask_bytes, format='PNG')
                                
                                result = generative_fill(
                                    st.session_state.api_key,
                                    uploaded_file.getvalue(),
                                    mask_bytes.getvalue(),
                                    prompt
                                )
                                
                                if result:
                                    image_urls = extract_image_urls_from_response(result)
                                    if image_urls:
                                        st.session_state.edited_image = image_urls[0]
                                        st.success("Generation complete!")
                                        st.rerun()
                                    else:
                                        st.error("No image URL in response")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            
            with col2:
                if st.session_state.edited_image:
                    image_data = download_image(
                        st.session_state.edited_image,
                        resize_for_display=True,
                        max_width=st.session_state.display_width,
                        quality=st.session_state.image_quality
                    )
                    
                    if image_data:
                        st.image(image_data['resized'], caption="Generated Result", use_column_width=True)
                        
                        col_dl1, col_dl2 = st.columns(2)
                        with col_dl1:
                            st.download_button(
                                "⬇️ Original",
                                image_data['original'],
                                "generated_original.png",
                                "image/png",
                                use_container_width=True
                            )
                        with col_dl2:
                            st.download_button(
                                "⬇️ Optimized",
                                image_data['resized'],
                                "generated_optimized.jpg",
                                "image/jpeg",
                                use_container_width=True
                            )
    
    # ===========================================
    # TAB 4: CLEANUP
    # ===========================================
    with tabs[3]:
        st.markdown("## 🧹 Cleanup Tools")
        st.markdown("Remove unwanted elements and clean up images.")
        
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="erase_upload")
        
        if uploaded_file:
            col1, col2 = st.columns(2)
            
            with col1:
                # Display original (resized)
                img = Image.open(uploaded_file)
                if img.size[0] > 600:
                    ratio = 600 / img.size[0]
                    new_size = (600, int(img.size[1] * ratio))
                    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
                    buffer = io.BytesIO()
                    img_resized.save(buffer, format='JPEG', quality=85)
                    buffer.seek(0)
                    st.image(buffer, caption="Original Image", use_column_width=True)
                else:
                    st.image(uploaded_file, caption="Original Image", use_column_width=True)
                
                # Get image for canvas
                img_width, img_height = img.size
                aspect_ratio = img_height / img_width
                canvas_width = min(img_width, 600)
                canvas_height = int(canvas_width * aspect_ratio)
                img_resized = img.resize((canvas_width, canvas_height))
                
                # Canvas for selecting area to erase
                stroke_width = st.slider("Brush Size", 1, 50, 20, key="erase_brush")
                canvas_result = st_canvas(
                    fill_color="rgba(255, 255, 255, 0.0)",
                    stroke_width=stroke_width,
                    stroke_color="#fff",
                    drawing_mode="freedraw",
                    background_image=img_resized,
                    height=canvas_height,
                    width=canvas_width,
                    key="erase_canvas"
                )
                
                if st.button("Erase Selected Area", type="primary", use_container_width=True):
                    if canvas_result.image_data is None:
                        st.warning("Please draw on the image to select area to erase")
                    else:
                        with st.spinner("Erasing..."):
                            try:
                                result = erase_foreground(
                                    st.session_state.api_key,
                                    image_data=uploaded_file.getvalue()
                                )
                                
                                if result:
                                    image_urls = extract_image_urls_from_response(result)
                                    if image_urls:
                                        st.session_state.edited_image = image_urls[0]
                                        st.success("Area erased successfully!")
                                        st.rerun()
                                    else:
                                        st.error("No image URL in response")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            
            with col2:
                if st.session_state.edited_image:
                    image_data = download_image(
                        st.session_state.edited_image,
                        resize_for_display=True,
                        max_width=st.session_state.display_width,
                        quality=st.session_state.image_quality
                    )
                    
                    if image_data:
                        st.image(image_data['resized'], caption="Cleaned Image", use_column_width=True)
                        
                        col_dl1, col_dl2 = st.columns(2)
                        with col_dl1:
                            st.download_button(
                                "⬇️ Original",
                                image_data['original'],
                                "cleaned_original.png",
                                "image/png",
                                use_container_width=True
                            )
                        with col_dl2:
                            st.download_button(
                                "⬇️ Optimized",
                                image_data['resized'],
                                "cleaned_optimized.jpg",
                                "image/jpeg",
                                use_container_width=True
                            )
    
    # ===========================================
    # FOOTER
    # ===========================================
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    with footer_col1:
        st.caption("© 2024 LyTa Studio Pro. All rights reserved.")
    with footer_col2:
        st.caption("Made with ❤️ for creative professionals")
    with footer_col3:
        st.caption("[Terms] • [Privacy] • [Support]")

# ===========================================
# APPLICATION ENTRY POINT
# ===========================================
if __name__ == "__main__":
    main()