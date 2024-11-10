# app/prompts/handlers.py

import os
import aiohttp
from fastapi import logger

from app.prompts.config import PromptConfig

class PromptHandler:
    def __init__(self):
        self.config = PromptConfig()

    async def check_assessment_and_location(self, user_message: str) -> tuple[bool, str]:
        """
        Checks if an assessment should be run and returns the location if applicable.
        Returns a tuple of (should_run_assessment: bool, location: str)
        """
        assessment_prompt = self.config.get_assessment_prompt().format(
            user_message=user_message
        )
        
        try:
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{
                    "role": "user",
                    "content": assessment_prompt
                }]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    response_data = await response.json()
                    location = response_data["choices"][0]["message"]["content"].strip()
                    
                    if location == "NO_ASSESSMENT":
                        return False, ""
                    else:
                        return True, location

        except Exception as e:
            return False, ""

    def extract_location(self, user_message: str) -> str:
        """Extract location name from user message."""
        user_message = user_message.lower()
        
        # List of phrases to remove
        remove_phrases = [
            "calculate energy for",
            "calculate energy in",
            "calculate the energy for",
            "calculate the energy in",
            "energy calculation for",
            "energy assessment for",
            "assess energy in",
            "what is the energy in"
        ]
        
        # Remove each phrase if present
        for phrase in remove_phrases:
            if phrase in user_message:
                return user_message.replace(phrase, "").strip()
        
        # If no phrase found, try to extract the last word or phrase
        words = user_message.split()
        if len(words) > 0:
            return words[-1]
        
        return user_message.strip()