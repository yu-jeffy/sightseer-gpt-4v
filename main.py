import os
import time
import base64
import json
import math
import re
import subprocess
import pyautogui
import argparse
import platform
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageGrab
import Xlib.display
import Xlib.X
import Xlib.Xutil 
from openai import OpenAI

load_dotenv()

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

monitor_size = {
    "width": 1920,
    "height": 1080,
}

ASSISTANT_PROMPT = """
You are a Self-Operating Computer and Quiz Assistant.

View the screenshot identify the quiz question and answers.

Answer the question and provide the correct answer. Explain your reasoning.

Answer in the format:
QUESTION: <question>
ANSWER: <answer>

If there are multiple questions, answer each of them. Be direct and straightforward.

"""

file_path = "screenshot.png"

def capture_screen_with_cursor(file_path):
    user_platform = platform.system()

    if user_platform == "Windows":
        screenshot = pyautogui.screenshot()
        screenshot.save(file_path)
    elif user_platform == "Linux":
        # Use xlib to prevent scrot dependency for Linux
        screen = Xlib.display.Display().screen()
        size = screen.width_in_pixels, screen.height_in_pixels
        monitor_size["width"] = size[0]
        monitor_size["height"] = size[1]
        screenshot = ImageGrab.grab(bbox=(0, 0, size[0], size[1]))
        screenshot.save(file_path)
    elif user_platform == "Darwin":  # (Mac OS)
        # Use the screencapture utility to capture the screen with the cursor
        subprocess.run(["screencapture", "-C", file_path])
    else:
        print(f"The platform you're using ({user_platform}) is not currently supported")

def ask_assistant(file_path):
    try:
        with open(file_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": ASSISTANT_PROMPT},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_base64}",
                    },
                    },
                ],
                }
            ],
            max_tokens=500,
        )

        content = response.choices[0].message.content
        return content
    
    except Exception as e:
        print(f"Error: {e}")

capture_screen_with_cursor(file_path)
print(ask_assistant(file_path))

