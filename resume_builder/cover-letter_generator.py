import json

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON. Please ensure the file is a valid JSON format.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def generate_cover_letter_from_json(json_data):
    markdown = ""
    for paragraph in json_data['paragraphs']:
        # Adding two spaces at the end of each paragraph for a Markdown line break
        markdown += f"   {paragraph}  \n\n"  # Indented paragraph with two spaces at the end

    markdown += f"{json_data['sign_off']},  \n\n{json_data['author']}"
    return markdown

if __name__ == "__main__":
    # Reading the JSON file
    cover_letter_data = read_json_file('coverletter.json')

    if cover_letter_data:
        markdown = f'''---
margin-left: 2cm
margin-right: 2cm
margin-top: 1cm
margin-bottom: 2cm
title: {cover_letter_data['title']}
author:
- {cover_letter_data['author']}
subject: {cover_letter_data['position_name']}
---  \n\n
'''
        markdown += generate_cover_letter_from_json(cover_letter_data)

        # Write the content to a Markdown file
        with open("coverletter.md", "w") as file:
            file.write(markdown)
