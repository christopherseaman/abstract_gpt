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
   - Matches a closing parenthesis, suggesting that the confidence interval is enclosed in parentheses.

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

## Alternative Approach - NLP Using ChatGPT via API
