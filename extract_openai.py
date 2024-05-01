import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import csv

# Debugging?
DEBUG = False

# Load the OpenAI API key from a .env file
load_dotenv('dot.env')
client = OpenAI()

# Directory containing the example abstract/extract pairs
examples_dir = 'examples'
if DEBUG:
    abstracts_dir = 'test_abstracts'
else:
    abstracts_dir = 'abstracts'
extracts_dir = 'extracted'
output_tsv = 'extracted_data.tsv'

# Define the function and how it should be structured within the API call
tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_from_abstract",
            "description": "Extract structured data from abstracts. Must include PMID, PublicationDate, Author, Journal, and Measures. Each measure in Measures must include Metric, MeasureType, and (PValue) and/or (CIUpper AND CILower).",
            "parameters": {
                "type": "object",
                "properties": {
                    "PMID": {"type": "string", "description": "The PubMed ID from the abstract"},
                    "PublicationDate": {"type": "string", "description": "The publication date from the abstract"},
                    "Author": {"type": "string", "description": "The first author of the publication"},
                    "Journal": {"type": "string", "description": "The journal in which the publication appeared"},
                    "StudyDesign": {"type": "string", "description": "The study design of the publication; e.g., randomized controlled trial, cohort study, case-control study, etc."},
                    "Measures": {
                        "type": "array",
                        "description": "An array of measurements with point estimates and confidence intervals",
                        "items": {
                            "type": "object",
                            "properties": {
                                "PValue": {"type": "string", "description": "The p-value associated with the measurement; e.g.,'0.05' or '<0.01'"},
                                "PointEstimate": {"type": "number", "description": "The point estimate from the abstract (numeric value)"},
                                "CILower": {"type": "number", "description": "The lower bound of the confidence interval (numeric value)"},
                                "CIUpper": {"type": "number", "description": "The upper bound of the confidence interval (numeric value)"},
                                "ConfidenceLevel": {"type": "string", "description": "Confidence level of the interval, e.g., 95%, 99%"},
                                "MeasureType": {"type": "string", "description": "Type of statistical measure (Odds Ratio, Hazard Ratio, Relative Risk, Regression Coefficient, etc.)"},
                                "Metric": {"type": "string", "description": "The measurement with the point estimate and confidence interval"},
                            },
                            "required": ["Metric", "MeasureType"]
                        }
                    }
                },
                "required": ["PMID", "PublicationDate", "Author", "Journal", "Measures"],
            },
        },
    }
]

# # Define the function that will be called by the API
def extract_from_abstract(PMID, PublicationDate, author, journal, study_design, Measures):
    return {
        "PMID": PMID,
        "Date": PublicationDate,
        "Author": author,
        "Journal": journal,
        "StudyDesign": study_design,
        "Measures": Measures
    }

# API call to GPT-3.5 Turbo with the function calling
message_template=[
        {"role": "system", "content": "Extract structured data from abstracts. Must include PMID, PublicationDate, Lead Author, Journal, and Measures. Each measure in Measures must include Metric, MeasureType, and (PValue) and/or (CIUpper AND CILower)."},
    ]

# Build the few-shot learning prompt
print("Building few-shot learning prompt...")
example_files = os.listdir(examples_dir)
for file in example_files:
    if file.endswith('.txt'):  # Identify abstract text files
        abstract_path = os.path.join(examples_dir, file)
        extract_path = os.path.join(examples_dir, file.replace('abstract', 'extract').replace('.txt', '.json'))

        # Read the abstract text
        with open(abstract_path, 'r') as file:
            abstract_text = file.read()
        
        # Load the corresponding extraction JSON
        with open(extract_path, 'r') as file:
            extraction_data = json.load(file)

        # Append the abstract and extraction data to the messages prompt
        message_template.append({"role": "user", "content": abstract_text})
        message_template.append({"role": "assistant", "content": json.dumps(extraction_data, indent=2)})

# Define the function to extract structured data from an abstract using ChatGPT
def extract_abstract(abstract_text, message_template):
    messages = message_template.copy()
    messages.append({"role": "user", "content": abstract_text})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=2048,
        tools=tools,
        frequency_penalty=0,
        presence_penalty=0,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if DEBUG:
        print(response_message)

    # Parse the output from OpenAI API
    rows = []

    # Extract information for each tool call
    if tool_calls:
        available_functions = {
            "extract_from_abstract": extract_from_abstract,
        } 

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
                author = args_js['Author']
                journal = args_js['Journal']
                study_design = args_js.get('StudyDesign', None)
                measures = []
                for measure in args_js['Measures']:
                    measures.append({
                        "Metric": measure['Metric'],
                        "MeasureType": measure['MeasureType'],
                        "PointEstimate": measure.get('PointEstimate', None),
                        "CILower": measure.get('CILower', None),
                        "CIUpper": measure.get('CIUpper', None),
                        "ConfidenceLevel": measure.get('ConfidenceLevel', None),
                        "PValue": measure.get('PValue', None)
                        })
                rows.append({
                    "PMID": pmid,
                    "Date": date,
                    "Author": author,
                    "Journal": journal,
                    "StudyDesign": study_design,
                    "Measures": measures
                })
    return rows

# Iterate over each abstract file
for root, dirs, files in os.walk(abstracts_dir):
    for file in files:
        if file.endswith('.txt'):
            abstract_path = os.path.join(root, file)
            extract_rel_path = os.path.relpath(abstract_path, abstracts_dir)
            extract_path = os.path.join(extracts_dir, extract_rel_path.replace('.txt', '.json'))

            # Ensure the directory exists before saving
            os.makedirs(os.path.dirname(extract_path), exist_ok=True)

            print(f"Extracting data for: {abstract_path}")
            if not os.path.exists(extract_path):
                # Read and process the abstract
                with open(abstract_path, 'r') as f:
                    abstract_text = f.read()
                extracted_data = extract_abstract(abstract_text, message_template)

                # Save the extracted data
                with open(extract_path, 'w') as f:
                    json.dump(extracted_data, f, indent=4)
                print(f"Extraction saved to: {extract_path}")
            else:
                print(f"Extraction exists  : {extract_path}")

# Print the extracted data as extracted_data.tsv in the following format:
# PMID, Date, Author, Journal, Study_Design, Point Estimate, CI Lower, CI Upper, P-Value, Confidence_Level, Measure_Type, Metric
# One row for each measure extracted from the abstracts
print("Converting extracted data to TSV file...")

headers = ['PMID', 'Date', 'Author', 'Journal', 'Study_Design', 'Point_Estimate', 'CI_Lower', 'CI_Upper', 'P_Value', 'Confidence_Level', 'Measure_Type', 'Metric']
with open(output_tsv, 'w', newline='', encoding='utf-8') as tsvfile:
    writer = csv.DictWriter(tsvfile, fieldnames=headers, delimiter='\t')
    writer.writeheader()
    
    # Walk through each file in the extracts directory
    for root, dirs, files in os.walk(extracts_dir):
        for filename in files:
            if filename.endswith('.json'):
                filepath = os.path.join(root, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        for measure in item['Measures']:
                            writer.writerow({
                                'PMID': item['PMID'],
                                'Date': item['Date'],
                                'Author': item['Author'],
                                'Journal': item['Journal'],
                                'Study_Design': item.get('Study_Design', None),
                                'Point_Estimate': measure.get('PointEstimate', None),
                                'CI_Lower': measure.get('CILower', None),
                                'CI_Upper': measure.get('CIUpper', None),
                                'P_Value': measure.get('PValue', None),
                                'Confidence_Level': measure.get('ConfidenceLevel', None),
                                'Measure_Type': measure['MeasureType'],
                                'Metric': measure['Metric']
                            })

print(f"Data conversion to TSV completed. Check {output_tsv} for the output.")
