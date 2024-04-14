import os
import subprocess

def split_file(input_file, delimiter):
    with open(input_file, 'r') as file:
        content = file.read()

    sections = content.split(delimiter)

    for i, section in enumerate(sections, 1):
        z = i-1
        output_file = f"individual_abstracts/output_section_{z}.txt"
        with open(output_file, 'w') as file:
            file.write(section)

        print(f"Section {i} written to {output_file}")

# Example usage:

directory_path="individual_abstracts/"
files = os.listdir("individual_abstracts/")

for file_name in files:
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        
input_file_path = 'abstract-AmericanJo-set.txt'
delimiter_string = '. Am J Epidemiol.'  
split_file(input_file_path, delimiter_string)
os.remove("individual_abstracts/output_section_0.txt")

