# Extract Confidence Intervals from Abstracts

## Script Functionality
- **File Handling:** Reads filenames from a specified directory (`individual_abstracts`), assuming all are text files.
- **Regular Expressions:** Uses multiple regex patterns to extract:
  - PubMed ID (PMID)
  - Date of the article
  - Statistical estimates including point estimates and 95% confidence intervals.
- **Data Extraction:** For each text file:
  - Removes newlines for consistent pattern matching.
  - Extracts PMIDs, dates, and statistical measures.
  - Appends extracted data into a list, which is later written to a CSV file.
- **Output:** Data saved includes PMID, date, surrounding text, extracted estimates and confidence intervals, presence of specific statistical keywords (e.g., OR, HR), and beta coefficients.

## Potential Issues
- **Regular Expressions Complexity:** The complex patterns used to extract estimates may not match all possible formats in the texts, leading to missing or incorrect data.
- **Error Handling:** The script lacks error handling for file reading and regex operations, which could lead to crashes if files are corrupt or formats unexpected.

### Lesser Concerns
- **Directory and File Assumptions:** The script assumes all files in `individual_abstracts` are relevant text files. This could cause errors if non-text files are present.
- **Performance Issues:** Large number of files or large file sizes could slow down the script due to the lack of optimized file reading or concurrent processing techniques.
- **Hardcoded Paths:** The script uses a hardcoded directory path and CSV file path, which reduces flexibility and reusability.

## Regex Pattern Breakdown

```
(?<=(.{35}))(\d+(?:,\d+)*(?:\.\d+)?)[^0-9]{0,5}95%\sCI[^0-9]{0,5}(\d+(?:,\d+)*(?:\.\d+)?)[^0-9]{0,5}(\d+(?:,\d+)*(?:\.\d+)?)\)
|     1     |            2          |     3    |   4  |                 5                |                 6                |7|

```

### Components:
1. **`(?<=(.{35}))`**
   - This is a positive lookbehind assertion that checks for any 35 characters (`.{35}`) preceding the main pattern but does not include these characters in the match. It ensures that there is some context before the actual numbers being matched, which could be used for extracting surrounding text.

2. **`(\d+(?:,\d+)*(?:\.\d+)?)`**
   - Number which may contain commas (for thousands separators) and may have a decimal part.
   - `\d+` matches one or more digits.
   - `(?:,\d+)*` optionally matches groups of `,` followed by digits (handling numbers like `1,000`).
   - `(?:\.\d+)?` optionally matches a decimal point followed by one or more digits (handling decimal numbers).

3. **`[^0-9]{0,5}`**
   - Up to 5 non-digit characters

4. **`95%\sCI`**
   - This matches the literal string "95% CI", possibly separated by any whitespace (`\s`), indicating the start of a confidence interval section.

5. **`[^0-9]{0,5}(\d+(?:,\d+)*(?:\.\d+)?)`**
   - Up to 5 non-digit characters, followed by the lower limit of the 95% confidence interval.

6. **`[^0-9]{0,5}(\d+(?:,\d+)*(?:\.\d+)?)`**
   - Up to 5 non-digit characters, followed by the the upper limit of the 95% confidence interval.

7. **`\)`**
   - Matches a closing parenthesis, requiring that confidence intervals are enclosed in parentheses.

### Usage
This regex is tailored to extract numbers associated with a 95% confidence interval from scientific texts, which are formatted in a specific way. For instance, it would match expressions like "123.45 - 95% CI 100,123.67 - 150,200.89)" and extract:
- The point estimate (`123.45`)
- The lower limit of the confidence interval (`100,123.67`)
- The upper limit of the confidence interval (`150,200.89`)

### Potential Issues
- **Complexity and Specificity:** The pattern is quite specific and assumes a particular format. If the text deviates from this format (e.g., different separators, additional spaces, or textual content between numbers and the "95% CI" marker), the regex may fail to match.
- **Locale-Specific Formats:** It handles numbers with commas as thousands separators, which might not be appropriate for locales that use different separators (e.g., spaces or periods).


## Incremental Improvements
- **Optimize Regular Expressions:** If CI's are missed, refine regex patterns or use more flexible parsing techniques to improve data extraction accuracy.
- **Dynamic Pattern Recognition**: Utilize a configurable set of regex patterns or an external configuration file to adjust the patterns based on observed data formats without changing the script's source code
- **Implement Error Handling:** Add try-except blocks to manage exceptions, ensuring the script can handle unexpected issues gracefully.
- **Increase Flexibility:** Allow directory and output file paths to be parameters, enhancing the script's usability across different environments and use cases.

## Alternative Approach - NLP using OpenAI's API

It is not possible to craft RegEx clever enough to capture every possible manner of expressing confidence intervals. Instead, you could use a pre-trained large language model combined with structured output constraints. Included is an example of how this could work in [`extract_openai.py`](extract.openai.py).

### Code Summary
1. **Setup:** Loads libraries and API key from file `dot.env`
2. **Define Structure:** Creates a function for getting structured data back from OpenAI
3. **API Call:** Sends an example abstract to the API, storing the response
4. **Response Handling:** Parses the response to output the PMID, date, metric, point estimate, CI lower, and CI upper bounds

### Steps Left to Operationalize
1. **API Key Config** Add your own openai API key to the file `dot.env` (see [`dot.env.example`](dot.env.example) for format)
2. **Abstract Handling:** Update the code to iterate over abstracts, rather than using a single hard-coded example
3. **Prompt Engineering:** *(OPTIONAL)* If model responses are not sufficiently accurate, you can give examples of prompts (abstracts) and responses (PMID + CI's) as a form of prompt engineering. This is generally referred to as *few-shot learning*.
4. **Storing Output** Output to a csv file instead of stdout

### Example Output

| PMID     | Publication Date | Metric                                                                    | Point Estimate | CI Lower | CI Upper |
|----------|------------------|---------------------------------------------------------------------------|----------------|----------|----------|
| 36345076 | 2023 Feb 1       | Prevalence of vision impairment among adults with PN                      | 3.89           | 2.99     | 5.05     |
| 36345076 | 2023 Feb 1       | Prevalence of vision impairment among adults without PN                   | 1.29           | 1.04     | 1.60     |
| 36345076 | 2023 Feb 1       | Association of PN with vision impairment overall (OR)                     | 1.48           | 1.03     | 2.13     |
| 36345076 | 2023 Feb 1       | Association of PN with vision impairment among adults without diabetes (OR)| 1.80           | 1.17     | 2.77     |
| 36345076 | 2023 Feb 1       | Prevalence of hearing impairment among adults with PN                     | 26.5           | 20.4     | 33.7     |
| 36345076 | 2023 Feb 1       | Prevalence of hearing impairment among adults without PN                  | 14.2           | 12.4     | 16.3     |
| 36345076 | 2023 Feb 1       | Association of PN with moderate/severe hearing impairment overall (OR)    | 2.55           | 1.40     | 4.64     |
| 36345076 | 2023 Feb 1       | Association of PN with moderate/severe hearing impairment among adults without diabetes (OR) | 3.26   | 1.80     | 5.91     |
