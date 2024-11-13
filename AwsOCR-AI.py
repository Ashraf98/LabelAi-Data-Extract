from flask import Flask, request, jsonify, render_template, send_file
import boto3
import botocore  
import logging 

from PIL import Image
import openai
import pandas as pd
import io
import json
import numpy as np

# boto3 debug logging
logging.basicConfig(level=logging.DEBUG)
boto3.set_stream_logger(name='boto3', level=logging.DEBUG)

# AWS session and Textract client
try:
    session = boto3.Session(profile_name="my-profile")
    textract = session.client('textract', region_name='us-east-1')  
    credentials = session.get_credentials()
    logging.info(f"AWS Access Key: {credentials.access_key}")
    logging.info(f"AWS Secret Key: {credentials.secret_key}")
    logging.info(f"AWS Region: {session.region_name}")
except botocore.exceptions.BotoCoreError as e:
    logging.error(f"Error retrieving AWS credentials: {str(e)}")

# OpenAI API key 
openai.api_key = "MyKey" 

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        image_bytes = file.read()
        image_size_mb = len(image_bytes) / (1024 * 1024)
        if image_size_mb > 5:
            return jsonify({"error": "Image size exceeds 5 MB limit"}), 400

        image = Image.open(io.BytesIO(image_bytes))

        response = textract.analyze_document(
            Document={'Bytes': image_bytes},
            FeatureTypes=['TABLES']
        )

        lines = extract_text_from_response(response)
        cleaned_data = clean_data(lines)
        structured_data = format_with_ai(cleaned_data)

        excel_file = convert_to_excel(structured_data, lines)

        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='output.xlsx'
        )

    except botocore.exceptions.ClientError as error:
        error_code = error.response['Error'].get('Code', 'Unknown')
        error_message = error.response['Error'].get('Message', 'No message provided')
        return jsonify({"error": f"AWS Textract error: {error_code} - {error_message}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

def extract_text_from_response(response):
    lines = []
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            lines.append(block['Text'])
    return lines

def clean_data(lines):
    supplement_facts = []
    other_ingredients = []

    in_facts_section = False
    found_facts_start = False

    facts_start_keywords = ["nutrition facts", "supplement facts", "serving size", "calories"]
    nutrient_keywords = [
        "calories", "total fat", "saturated fat", "trans fat", "cholesterol", "sodium",
        "total carbohydrate", "dietary fiber", "total sugars", "added sugars", "protein",
        "vitamin", "iron", "calcium", "potassium", "phosphorus", "zinc", "folate", "niacin", "riboflavin"
    ]

    print("Extracted Lines for Debugging:")
    for i, line in enumerate(lines):
        print(f"Line {i + 1}: {line}")

    for line in lines:
        stripped_line = line.strip().lower()

        if any(keyword in stripped_line for keyword in facts_start_keywords):
            in_facts_section = True
            found_facts_start = True
            supplement_facts.append(line.strip())
            continue

        if any(phrase in stripped_line for phrase in ["% daily value", "advice", "not a significant source"]):
            in_facts_section = False
            continue

        if in_facts_section or any(keyword in stripped_line for keyword in nutrient_keywords):
            supplement_facts.append(line.strip())

        if "contains" in stripped_line or "ingredient" in stripped_line:
            other_ingredients.append(line.strip())

    if not other_ingredients and not in_facts_section:
        possible_ingredients = [
            line.strip() for line in lines if "ingredient" in line.lower() or "," in line
        ]
        other_ingredients_text = ' '.join(possible_ingredients).replace("  ", " ").strip() if possible_ingredients else "No other ingredients found."
    else:
        other_ingredients_text = ' '.join(other_ingredients).replace("  ", " ").strip() if other_ingredients else "No other ingredients found."

    print("Final Supplement Facts:", supplement_facts)
    print("Final Other Ingredients:", other_ingredients_text)

    return {
        "supplement_facts": supplement_facts,
        "other_ingredients": other_ingredients_text
    }

def format_with_ai(data):
    supplement_facts_text = "\n".join(data['supplement_facts'])
    prompt = f"""
    Here is an extracted facts panel from an OCR tool. Please cleanly format the data, separating each nutrient name and value into a tabular format.
    Ignore lines without relevant data, but dont remove nutritional info that has 0 as a value. This should stay as it's part of the fact's panel. Correct any obvious OCR errors and only include actual data. Skip any missing fields.

    Facts:
    {supplement_facts_text}

    Please provide the output as a JSON with 'Nutritional Info' as a dictionary and 'Other Ingredients' as a string.
    """

    print("Prompt sent to OpenAI:", prompt)

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    gpt_response = response.choices[0].message.content.strip()
    print("GPT Response:", gpt_response)

    try:
        structured_data = json.loads(gpt_response)
    except json.JSONDecodeError:
        structured_data = {"Nutritional Info": {}, "Other Ingredients": "No other ingredients found."}

    return structured_data

def convert_to_excel(data, extracted_lines):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        nutritional_info_data = data.get("Nutritional Info", {})
        nutritional_info_list = [{"Ingredient": key, "Amount": value} for key, value in nutritional_info_data.items()]

        nutritional_info_df = pd.DataFrame(nutritional_info_list)
        nutritional_info_df.to_excel(writer, index=False, sheet_name="Nutritional Info")

        other_ingredients_text = data.get("Other Ingredients", "No other ingredients found.")
        other_ingredients_df = pd.DataFrame({"Other Ingredients": [other_ingredients_text]})
        other_ingredients_df.to_excel(writer, index=False, sheet_name="Other Ingredients")

        extracted_lines_df = pd.DataFrame({"Extracted Lines": extracted_lines})
        extracted_lines_df.to_excel(writer, index=False, sheet_name="Extracted Lines")

    output.seek(0)
    return output

if __name__ == '__main__':
    app.run(debug=True)