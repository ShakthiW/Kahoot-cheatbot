import time
from datetime import datetime
import os
from dotenv import load_dotenv
import subprocess
from pynput import keyboard
import base64
from openai import OpenAI
from PIL import Image
import pytesseract

class QuizAnalyzer:
    def __init__(self):
        # Initialize OpenAI
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found")
        self.client = OpenAI(api_key=api_key)
        # Change to a faster model
        self.model = "gpt-4o-mini"
        
        # Configure Tesseract
        if os.path.exists('/usr/local/bin/tesseract'):
            pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
        elif os.path.exists('/opt/homebrew/bin/tesseract'):
            pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

    def take_screenshot(self):
        """Take a screenshot using screencapture command"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'screenshot_{timestamp}.png'
            
            # Use macOS screencapture command
            subprocess.run(['screencapture', '-x', filename], check=True)
            
            # Optimize the image before processing
            self.optimize_image(filename)
            print(f"Screenshot saved as: {filename}")
            return filename
        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")
            return None

    def optimize_image(self, image_path):
        """Optimize the image to reduce size and processing time"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if the image is too large
                max_size = 1500
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Optimize and save
                img.save(image_path, 'PNG', optimize=True, quality=85)
        except Exception as e:
            print(f"Error optimizing image: {str(e)}")

    def extract_text_ocr(self, image_path):
        """Extract text using Tesseract OCR"""
        try:
            with Image.open(image_path) as img:
                # Use multiple OCR configurations for better results
                configs = [
                    '--psm 6',  # Assume uniform block of text
                    '--psm 3',  # Fully automatic page segmentation
                ]
                
                for config in configs:
                    text = pytesseract.image_to_string(img, config=config)
                    if text.strip():
                        return text.strip()
                return None
        except Exception as e:
            print(f"OCR Error: {str(e)}")
            return None

    def encode_image(self, image_path):
        """Encode image to base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {str(e)}")
            return None

    def analyze_image(self, image_path):
        """Analyze image using GPT-4 Vision"""
        try:
            # First try OCR
            print("Trying OCR...")
            ocr_text = self.extract_text_ocr(image_path)
            
            if ocr_text:
                # If OCR successful, use GPT to analyze the text
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Faster model for text analysis
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a quiz assistant. Quickly identify the question and options from the text, and provide the most likely answer. Be very concise."
                        },
                        {
                            "role": "user",
                            "content": f"Analyze this quiz text and provide the answer:\n{ocr_text}"
                        }
                    ],
                    max_tokens=200,
                    temperature=1
                )
                return response.choices[0].message.content.strip()
            
            # If OCR fails, fall back to Vision API
            print("OCR unclear, trying Vision API...")
            base64_image = self.encode_image(image_path)
            if not base64_image:
                return None
            
            prompt = """You are a quiz assistant. 
                Quickly identify the question and options, and provide the most likely answer. 
                Be very concise. If you didnt get the answer in the text don't provide an answer based on the prompt just give the correct answer."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What's the question and answer?"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return None

def analyze_screen(analyzer):
    """Function to handle screen analysis"""
    print("\nAnalyzing screen...")
    
    # Take screenshot
    screenshot_path = analyzer.take_screenshot()
    if not screenshot_path:
        print("Failed to take screenshot")
        return

    print("Processing...")
    # Analyze with GPT-4 Vision
    analysis = analyzer.analyze_image(screenshot_path)
    if analysis:
        print("\nResult:")
        print("-" * 30)
        print(analysis)
        print("-" * 30)
    else:
        print("Analysis failed")

    print(f"Screenshot saved at: {screenshot_path}")

def main():
    print("Starting Quiz Answer Bot")
    analyzer = QuizAnalyzer()
    
    print("""
    Quiz Answer Bot Ready!
    Instructions:
    1. Make sure the quiz is visible on screen
    2. Press 'q' to analyze the current screen
    3. Press 'esc' to exit
    """)

    # Flag to control the main loop
    running = True

    def on_press(key):
        nonlocal running
        try:
            if key.char == 'q':
                analyze_screen(analyzer)
            elif key == keyboard.Key.esc:
                running = False
                return False  # Stop listener
        except AttributeError:
            pass

    # Set up the listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        while running:
            time.sleep(0.1)
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        listener.stop()
        print("\nBot terminated")

if __name__ == "__main__":
    main()
