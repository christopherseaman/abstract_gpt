import re
import pandas as pd
import csv
import os

csv_file_path = 'output.csv'

columns = ["PMID","Date","PreceedingText",'Estimate', 'Lower', 'Upper','Ratio','Beta']
with open(csv_file_path, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    # Write the header
    writer.writerow(columns)

#(?:CI|\bconfidence\s*interval\b\s*(?:\(\s*CI\s*\))?):
# Define a regular expression pattern
#pattern1 = re.compile(r'(?<=(.{35}))(\d+(?:,\d+)*(?:\.\d+)?),?\s*\(?95%\sCI:?.?\s?=?\s?(\d+(?:,\d+)*(?:\.\d+)?)\s*[-,][-]?\s*(\d+(?:,\d+)*(?:\.\d+)?)\)')
#pattern2 = re.compile(r'(?<=(.{35}))(\d+(?:,\d+)*(?:\.\d+)?),?\s*\(?95%\sconfidence\sinterval:?.?\s?=?\s?(\d+(?:,\d+)*(?:\.\d+)?)\s*[-,][-]?\s*(\d+(?:,\d+)*(?:\.\d+)?)\)')
#pattern3 = re.compile(r'(?<=(.{35}))(\d+(?:,\d+)*(?:\.\d+)?),?\s*\(?95%\sconfidence\sinterval.?\s\(CI\):?.?\s?=?\s?(\d+(?:,\d+)*(?:\.\d+)?)\s*[-,][-]?\s*(\d+(?:,\d+)*(?:\.\d+)?)\)')
pattern1 = re.compile(r'(?<=(.{35}))(\d+(?:,\d+)*(?:\.\d+)?)[^0-9]{0,5}95%\sCI[^0-9]{0,5}(\d+(?:,\d+)*(?:\.\d+)?)[^0-9]{0,5}(\d+(?:,\d+)*(?:\.\d+)?)\)')
pattern2 = re.compile(r'(?<=(.{35}))(\d+(?:,\d+)*(?:\.\d+)?)[^0-9]{0,5}95%\sconfidence\sinterval[^0-9]{0,5}(\d+(?:,\d+)*(?:\.\d+)?)[^0-9]{0,5}(\d+(?:,\d+)*(?:\.\d+)?)\)')
pattern3 = re.compile(r'(?<=(.{35}))(\d+(?:,\d+)*(?:\.\d+)?)[^0-9]{0,5}95%\sconfidence\sinterval\s\(CI\)[^0-9]{0,5}(\d+(?:,\d+)*(?:\.\d+)?)[^0-9]{0,5}(\d+(?:,\d+)*(?:\.\d+)?)\)')


for filename in os.listdir("individual_abstracts"):
    print(filename)
    if filename.endswith('.txt'):  
        file_path = os.path.join("individual_abstracts", filename)
        
        with open(file_path, 'r') as file:
            text = file.read()
            text_without_newlines = text.replace('\n', '').replace('\r', '')
            # Search for the pattern in the text
            pmid_pattern = re.compile(r'PMID: (\d+)')
            pmid_matches = pmid_pattern.findall(text)
            if pmid_matches:
                pmid = pmid_matches[-1]
                print(pmid)
            else:
                print("No PMID found in the text.")
            date_pattern = r'\b\d{4}( [A-Za-z]{3} )?\d{0,2}'
            date_match = re.search(date_pattern, text)
            date = date_match.group() if date_match else None
            print(date)
            matches1 = pattern1.findall(text_without_newlines)
            matches2 = pattern2.findall(text_without_newlines)
            matches3 = pattern3.findall(text_without_newlines)
            matches =  matches3 + matches2 + matches1
            modified_list = [(pmid,date,) + x for x in matches]
            print(modified_list)

            keywords_to_check = ["OR", "HR", "RR", "IRR", "SIR", "ratio", "relative"]
            def contains_keyword(entry):
                return any(keyword in ''.join(str(e) for e in entry[1:] if e is not None) for keyword in keywords_to_check)


            betas_to_check = ["beta","\u03B2"]
            def contains_beta(entry):
                return any(beta in ''.join(str(e) for e in entry[1:] if e is not None) for beta in betas_to_check)
            result_tuples = [(entry + (contains_keyword(entry),contains_beta(entry),)) for entry in modified_list]
            print(result_tuples)

            with open(csv_file_path, 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                # Write the data
                writer.writerows(result_tuples)

print(f"CSV file '{csv_file_path}' has been created.")
