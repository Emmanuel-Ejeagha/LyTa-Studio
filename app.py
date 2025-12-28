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
        'generation_history': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ===========================================
# UTILITY FUNCTIONS
# ===========================================
def download_image(url):
    """Download image from URL and return as bytes."""
    try:
        # Add timeout and headers for better compatibility
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            st.warning(f"URL returned non-image content: {content_type}")
            
        return response.content
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
    
    # Debug: Show raw response structure
    st.write(f"Debug - Response type: {type(result)}")
    
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
    
    # Debug section (can be collapsed)
    with st.expander("🔍 Debug Information", expanded=False):
        st.write("Session State:", {
            "api_key_present": bool(st.session_state.api_key),
            "generated_images_count": len(st.session_state.get('generated_images', [])),
            "edited_image": st.session_state.get('edited_image'),
            "processing": st.session_state.get('processing', False)
        })
    
    # ===========================================
    # HEADER SECTION
    # ===========================================
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("# 🎨 LyTa Studio Pro")
        st.markdown("### Professional AI-Powered Image Editing Suite")
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
            
            **API Response Formats:**
            - Supports multiple BRIA API response formats
            - Automatic URL extraction from responses
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
                st.info(st.session_state.enhanced_prompt)
        
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
                                
                                # Debug: Show extracted URLs
                                with st.expander("📋 Generated URLs"):
                                    for i, url in enumerate(image_urls):
                                        st.write(f"Image {i+1}: {url}")
                            else:
                                st.error("❌ No image URLs found in API response")
                                # Debug: Show raw response
                                with st.expander("📋 Raw API Response"):
                                    st.json(result)
                                    
                        except Exception as e:
                            st.error(f"❌ Generation failed: {str(e)}")
                            st.write("Error details:", str(e))
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
                    # Display image with caption
                    st.image(
                        img_url,
                        caption=f"Image {idx+1}",
                        use_column_width=True
                    )
                    
                    # Download button
                    image_data = download_image(img_url)
                    if image_data:
                        st.download_button(
                            f"⬇️ Download {idx+1}",
                            image_data,
                            f"generated_image_{idx+1}.png",
                            "image/png",
                            use_container_width=True,
                            key=f"download_{idx}"
                        )
        
        # Display single edited image if available
        elif st.session_state.edited_image:
            st.markdown("---")
            st.markdown("## 🖼️ Generated Image")
            st.image(st.session_state.edited_image, use_column_width=True)
            
            image_data = download_image(st.session_state.edited_image)
            if image_data:
                st.download_button(
                    "⬇️ Download Image",
                    image_data,
                    "generated_image.png",
                    "image/png",
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
                # Image Preview
                st.markdown("### 📷 Original")
                st.image(uploaded_file, use_column_width=True)
                
                # Quick Stats
                img = Image.open(uploaded_file)
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
                                    else:
                                        st.error("No image URL in response")
                                        with st.expander("Raw Response"):
                                            st.json(result)
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
                                    else:
                                        st.error("No image URL in response")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
        
        # Display edited image if available
        if st.session_state.edited_image and uploaded_file:
            st.markdown("### 📸 Result")
            st.image(st.session_state.edited_image, use_column_width=True)
            image_data = download_image(st.session_state.edited_image)
            if image_data:
                st.download_button(
                    "⬇️ Download Result",
                    image_data,
                    "result.png",
                    "image/png",
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
                st.image(uploaded_file, caption="Original Image", use_column_width=True)
                
                # Get image for canvas
                img = Image.open(uploaded_file)
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
                                    else:
                                        st.error("No image URL in response")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            
            with col2:
                if st.session_state.edited_image:
                    st.image(st.session_state.edited_image, caption="Generated Result", use_column_width=True)
                    image_data = download_image(st.session_state.edited_image)
                    if image_data:
                        st.download_button(
                            "⬇️ Download",
                            image_data,
                            "generated.png",
                            "image/png",
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
                st.image(uploaded_file, caption="Original Image", use_column_width=True)
                
                # Get image for canvas
                img = Image.open(uploaded_file)
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
                                    else:
                                        st.error("No image URL in response")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            
            with col2:
                if st.session_state.edited_image:
                    st.image(st.session_state.edited_image, caption="Cleaned Image", use_column_width=True)
                    image_data = download_image(st.session_state.edited_image)
                    if image_data:
                        st.download_button(
                            "⬇️ Download",
                            image_data,
                            "cleaned.png",
                            "image/png",
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