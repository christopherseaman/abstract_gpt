import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load the OpenAI API key from a .env file
load_dotenv('dot.env')
client = OpenAI()

# Define the function and how it should be structured within the API call
tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_from_abstract",
            "description": "Extracts structured data from abstracts",
            "parameters": {
                "type": "object",
                "properties": {
                    "PMID": {"type": "string", "description": "The PubMed ID from the abstract"},
                    "PublicationDate": {"type": "string", "description": "The publication date from the abstract"},
                    "Measures": {
                        "type": "array",
                        "description": "An array of measurements with point estimates and confidence intervals",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Metric": {"type": "string", "description": "The measurement with the point estimate and confidence interval"},
                                "PointEstimate": {"type": "string", "description": "The point estimate from the abstract"},
                                "CILower": {"type": "string", "description": "The lower bound of the confidence interval"},
                                "CIUpper": {"type": "string", "description": "The upper bound of the confidence interval"}
                            },
                            "required": ["Metric", "PointEstimate", "CILower", "CIUpper"]
                        }
                    }
                },
                "required": ["PMID", "PublicationDate"],
            },
        },
    }
]

# Define the function that will be called by the API
def extract_from_abstract(PMID, PublicationDate, Measures):
    return {
        "PMID": PMID,
        "Date": PublicationDate,
        "Measures": Measures
    }

# FIXME: To do this properly, you would iterate through the abstracts and call OpenAI separately for each 
# Example abstract (#24 chosen because of multiple CI's present)
abstract = """
 2023 Feb 1;192(2):237-245. doi: 10.1093/aje/kwac195.

Peripheral Neuropathy and Vision and Hearing Impairment in US Adults With and 
Without Diabetes.

Hicks CW, Wang D, Lin FR, Reed N, Windham BG, Selvin E.

We aimed to assess the associations of peripheral neuropathy (PN) with vision 
and hearing impairment among adults aged ≥40 years who attended the 
lower-extremity disease exam for the National Health and Nutrition Examination 
Survey (United States, 1999-2004). Overall, 11.8% (standard error (SE), 0.5) of 
adults had diabetes, 13.2% (SE, 0.5) had PN (26.6% (SE, 1.4) with diabetes, 
11.4% (SE, 0.5) without diabetes), 1.6% (SE, 0.1) had vision impairment, and 
15.4% (SE, 1.1) had hearing impairment. The prevalence of vision impairment was 
3.89% (95% CI: 2.99, 5.05) among adults with PN and 1.29% (95% CI: 1.04, 1.60) 
among adults without PN (P < 0.001). After adjustment, PN was associated with 
vision impairment overall (odds ratio (OR) = 1.48, 95% confidence interval (CI): 
1.03, 2.13) and among adults without diabetes (OR = 1.80, 95% CI: 1.17, 2.77) 
but not among adults with diabetes (P for interaction = 0.018). The prevalence 
of hearing impairment was 26.5% (95% CI: 20.4, 33.7) among adults with PN and 
14.2% (95% CI: 12.4, 16.3) among adults without PN (P < 0.001). The association 
of PN with moderate/severe hearing impairment was significant overall (OR = 
2.55, 95% CI: 1.40, 4.64) and among adults without diabetes (OR = 3.26, 95% CI: 
1.80, 5.91). Overall, these findings suggest an association between peripheral 
and audiovisual sensory impairment that is unrelated to diabetes.

© The Author(s) 2022. Published by Oxford University Press on behalf of the 
Johns Hopkins Bloomberg School of Public Health. All rights reserved. For 
permissions, please e-mail: journals.permissions@oup.com.

DOI: 10.1093/aje/kwac195
PMCID: PMC10308505
PMID: 36345076 [Indexed for MEDLINE]


25
"""

# API call to GPT-3.5 Turbo with the function calling
messages=[
        {"role": "system", "content": "Extract structured data from medical abstracts."},
        {"role": "user", "content": abstract}
    ]

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0,
    max_tokens=512,
    tools=tools,
    frequency_penalty=0,
    presence_penalty=0,
    tool_choice="auto"
)

response_message = response.choices[0].message

tool_calls = response_message.tool_calls
# print(tool_calls)

# Parse the output from OpenAI API
rows = []

# Extract information for each tool call
if tool_calls:
    available_functions = {
        "extract_from_abstract": extract_from_abstract,
    }  
    messages.append(response_message)  

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = tool_call.function.arguments
        try:
            args_js = json.loads(tool_call.function.arguments)
        except:
            args_js = {}
            print("Possible error in parsing JSON. Check the response from OpenAI, possibly cut off by token limit?")
            print("Response should be JSON:")
            print(function_args)
        if args_js['PMID']:
            pmid = args_js['PMID']
            date = args_js['PublicationDate']
            measures = []
            for measure in args_js['Measures']:
                metric = measure['Metric']
                point_estimate = measure['PointEstimate']
                ci_lower = measure['CILower']
                ci_upper = measure['CIUpper']
                measures.append({"Metric": metric, "PointEstimate": point_estimate, "CILower": ci_lower, "CIUpper": ci_upper})
            rows.append(extract_from_abstract(pmid, date, measures))

# Print the extracted data as PMID, Date, and Metric, Point Estimate, CI Lower, CI Upper
# Repeat PMID and Date for each metric extracted
for row in rows:
    # Print the header
    print(f"PMID, Publication Date, Metric: Point Estimate, CI Lower, CI Upper")
    for measure in row['Measures']:
        print(f"{row['PMID']}, {row['Date']}, {measure['Metric']}, {measure['PointEstimate']}, {measure['CILower']}, {measure['CIUpper']}")