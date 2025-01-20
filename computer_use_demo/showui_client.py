from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import torch
from PIL import Image
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

from tools import BashTool, ComputerTool, EditTool, ToolCollection, ToolResult

import platform
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, cast

import httpx

@dataclass
class ShowUIMessage:
    role: str
    content: List[Dict[str, Any]]

class ShowUIClient:
    def __init__(self):
        self.MIN_PIXELS = 256 * 28 * 28
        self.MAX_PIXELS = 1344 * 28 * 28
        self._SYSTEM = "You are a helpful computer assistant. You can control the computer by clicking and typing. Provide coordinates as [x, y] scaled from 0 to 1."
        
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

    def create_message(self, messages: List[ShowUIMessage]) -> dict:
        # Convert messages to ShowUI format
        formatted_messages = []
        for msg in messages:
            content = []
            for block in msg.content:
                if block["type"] == "image":
                    content.append({
                        "type": "image",
                        "image": block["source"]["data"],
                        "min_pixels": self.MIN_PIXELS,
                        "max_pixels": self.MAX_PIXELS
                    })
                elif block["type"] == "text":
                    content.append({
                        "type": "text",
                        "text": block["text"]
                    })
            formatted_messages.append({
                "role": msg.role,
                "content": content
            })

        # Process with ShowUI model
        text = self.processor.apply_chat_template(
            formatted_messages,
            tokenize=False,
            add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(formatted_messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        ).to("cuda")

        # Generate response
        generated_ids = self.model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]

        # Try to parse coordinates if present
        try:
            coords = ast.literal_eval(output_text)
            if isinstance(coords, list) and len(coords) == 2:
                return {
                    "content": [
                        {"type": "text", "text": output_text},
                        {"type": "tool_use", "name": "computer", "input": {"action": "click", "coordinates": coords}}
                    ]
                }
        except:
            pass

        # Return text response if no coordinates found
        return {
            "content": [
                {"type": "text", "text": output_text}
            ]
        }

async def sampling_loop(
    *,
    messages: List[ShowUIMessage],
    output_callback: Callable[[Dict[str, Any]], None],
    tool_output_callback: Callable[[ToolResult, str], None],
    **kwargs  # Accept but ignore other params from original
):
    """Modified sampling loop using ShowUI model"""
    tool_collection = ToolCollection(
        ComputerTool(),
        BashTool(),
        EditTool(),
    )
    
    client = ShowUIClient()

    while True:
        # Get response from ShowUI model
        response = client.create_message(messages)
        
        # Process response similar to original loop
        for content_block in response["content"]:
            output_callback(content_block)
            if content_block["type"] == "tool_use":
                result = await tool_collection.run(
                    name=content_block["name"],
                    tool_input=content_block["input"]
                )
                tool_output_callback(result, content_block.get("id", ""))
                messages.append(ShowUIMessage(
                    role="user",
                    content=[{
                        "type": "tool_result",
                        "content": result.output,
                        "tool_use_id": content_block.get("id", "")
                    }]
                ))
                break
        else:
            # No tool use, end loop
            return messages

        messages.append(ShowUIMessage(
            role="assistant",
            content=response["content"]
        ))