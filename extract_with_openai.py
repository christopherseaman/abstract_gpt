#!/bin/env python3

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load the OpenAI API key from dot.env file
load_dotenv('dot.env')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the function and how it should be structured within the API call
function_definition = {
    "type": "function",
    "function": {
        "name": "extract_data",
        "description": "Extracts structured data from abstracts",
        "parameters": {
            "abstract": {
                "type": "string",
                "description": "The text of the medical abstract"
            }
        },
        "return_type": {
            "type": "object",
            "properties": {
                "PMID": {"type": "string"},
                "PointEstimate": {"type": "string"},
                "ConfidenceInterval": {"type": "string"}
            }
        }
    }
}

# Example abstract
abstract = "The study, published in 2021, shows a significant reduction in symptoms, with a mean change of 5.6 (95% CI 3.4 to 7.8). PMID: 12345678."

# API call to GPT-3.5 Turbo with the function calling
response = client.chat.completions.create(model="gpt-3.5-turbo",
messages=[
    {"role": "system", "content": "Extract structured data from medical abstracts."},
    {"role": "user", "content": abstract}
],
tools=[function_definition],
tool_choice="auto")

# Print the response from the API
print(response)