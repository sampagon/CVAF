import streamlit as st
import torch
from PIL import Image, ImageDraw
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
import ast
import numpy as np
import base64
from io import BytesIO

from tools import ComputerTool, ToolResult

class ButtonFinder:
    def __init__(self):
        # Keep existing initialization
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
        
        self.computer_tool = ComputerTool()

    def find_button(self, base64_image, query):
        """Find button location in image based on query."""
        # Convert base64 to PIL Image
        image_data = base64.b64decode(base64_image)
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
        result_image = self.draw_point(image, coords, radius=10)
        
        # Convert result image back to base64
        buffered = BytesIO()
        result_image.save(buffered, format="PNG")
        result_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return coords, result_base64

async def main():
    st.title("ShowUI Button Finder Chat")
    
    if 'finder' not in st.session_state:
        st.session_state.finder = ButtonFinder()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "image" in message:
                st.image(base64.b64decode(message["image"]))

    # Get user input
    user_query = st.chat_input("What would you like me to find?")
    
    if user_query:
        # Take screenshot using ComputerTool
        tool_result = await st.session_state.finder.computer_tool.run({"action": "screenshot"})
        
        if tool_result.base64_image:
            # Add user message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_query
            })
            
            # Find button and get response
            with st.spinner("Finding element..."):
                try:
                    coords, marked_image = st.session_state.finder.find_button(tool_result.base64_image, user_query)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"I found the element at coordinates: {coords}",
                        "image": marked_image
                    })
                    
                    # Execute click using ComputerTool
                    await st.session_state.finder.computer_tool.run({
                        "action": "click",
                        "coordinates": coords
                    })
                    
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error processing request: {str(e)}")

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())