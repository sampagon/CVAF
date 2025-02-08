import docker
import time
import requests
import json
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
import ast
import base64
from PIL import Image, ImageDraw
from io import BytesIO
import torch

class Framework:
    def __init__(self, image_name="sampagon/cvaf:latest", ports=None):
        if ports is None:
            ports = {
                '5900/tcp': 5900,
                '8501/tcp': 8501,
                '6080/tcp': 6080,
                '8080/tcp': 8080,
                '5000/tcp': 5000
            }
        self.client = docker.from_env()
        self.image_name = image_name
        self.ports = ports
        self.container = None
        self.MIN_PIXELS = 256 * 28 * 28
        self.MAX_PIXELS = 1344 * 28 * 28
        self._SYSTEM = "Based on the screenshot of the page, I give a text description and you give its corresponding location. The coordinate represents a clickable location [x, y] for an element, which is a relative coordinate on the screenshot, scaled from 0 to 1."

        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            "showlab/ShowUI-2B",
            torch_dtype=torch.bfloat16,
            device_map="cuda"
        )
        self.processor = AutoProcessor.from_pretrained(
            "Qwen/Qwen2-VL-2B-Instruct", 
            min_pixels=self.MIN_PIXELS, 
            max_pixels=self.MAX_PIXELS
        )

    def start(self):
        # Run the container in the background
        self.container = self.client.containers.run(
            self.image_name,  # Image name
            ports=self.ports,
            detach=True,  # Run in background
            tty=True  # Keep the terminal open
        )
        
        url = "http://127.0.0.1:6080"
        print("Waiting for the container to be ready...")
        while True:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print(f"Container started successfully with ID: {self.container.id}")
                    break  # Exit the loop once the container is ready
            except requests.exceptions.RequestException:
                # Container is not ready yet, wait and retry
                time.sleep(1)
    
    def stop(self):
        if self.container:
            self.container.stop()
            print(f"Container with ID: {self.container.id} has been stopped")
        else:
            print("No container to stop.")
    
    def __command(self, action, text=None, coordinate=None):
        url = 'http://127.0.0.1:5000/perform_action'
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'action': action,
            'text': text,
            'coordinate': coordinate
        }

        # Send the request to the Flask API
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error sending command: {e}")

    def left_click(self, action="left_click", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def right_click(self, action="right_click", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def middle_click(self, action="middle_click", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def double_click(self, action="double_click", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def mouse_move(self, action="mouse_move", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def mouse_move(self, action="mouse_move", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def left_click_drag(self, action="left_click_drag", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def cursor_position(self, action="cursor_position", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def screenshot(self, action="screenshot", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def type(self, action="type", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def key(self, action="key", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def vision_system(self, query):
        # Convert base64 to PIL Image

        image_data = base64.b64decode(self.screenshot().json()['base64_image'])
        image = Image.open(BytesIO(image_data))
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": self._SYSTEM},
                    {"type": "image", "image": image, "min_pixels": self.MIN_PIXELS, "max_pixels": self.MAX_PIXELS},
                    {"type": "text", "text": query}
                ],
            }
        ]

        # Rest of the processing remains same
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        ).to("cuda")

        generated_ids = self.model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, 
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]

        coords = ast.literal_eval(output_text)
        coords = [
            int(coords[0] * image.width),
            int(coords[1] * image.height)
        ]

        return coords
