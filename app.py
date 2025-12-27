import streamlit as st
import os
from dotenv import load_dotenv
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
from PIL import Image
import io
import requests
import json
import time
import base64
from streamlit_drawable_canvas import st_canvas
import numpy as np
from services.erase_foreground import erase_foreground