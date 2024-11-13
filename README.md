# Ashraf's Label Imagery Data Extraction Project using AWS Textract and OpenAI

## Overview

This project is a web-based application that processes supplement fact panels from images uploaded by users. It uses Optical Character Recognition (OCR) to extract text from supplement labels, then cleans and formats the data. The extracted data is analyzed and returned to the user in a structured format, including nutritional information, other ingredients, and contain statements. The application then generates an Excel file with this structured data, making it easier for users to organize and manage the supplement information.

### Key Features:
- **OCR-based Text Extraction**: Uses AWS Textract to extract text from uploaded supplement panel images.
- **Data Cleaning & Formatting**: Cleans the extracted text and formats it into a structured, tabular format.
- **AI-enhanced Data Parsing**: Utilizes OpenAI's GPT model to further format and structure the extracted data into a more human-readable form.
- **Excel Export**: Allows users to download the structured data as an Excel file, which includes separate sheets for nutritional information, other ingredients, and extracted lines.
- **Customizable Input**: Users can specify whether the supplement facts include "other ingredients" and "contain statements", providing flexibility in the types of supplements processed.

## How It Works

1. **Upload an Image**: Users upload an image of a supplement fact panel (e.g., from a bottle label).
2. **Text Extraction**: The application uses AWS Textract to extract the text from the image.
3. **Data Processing**: The extracted text is cleaned and formatted by the application. It parses out nutritional information and separates "other ingredients" and "contain statements".
4. **AI Enhancement**: OpenAI’s GPT model is used to further format and structure the data into a more readable JSON format.
5. **Download Excel**: Once the data is structured, the user can download an Excel file containing the processed information.

## Technologies Used

- **Flask**: A lightweight Python web framework to build the application.
- **AWS Textract**: A service from Amazon Web Services (AWS) that automatically extracts text from scanned documents.
- **OpenAI**: Used for further formatting and processing the extracted data using GPT models.
- **Pandas & XlsxWriter**: For organizing and exporting the data into Excel format.

## Installation

### Prerequisites
- Python 3.x
- AWS Account (for AWS Textract)
- OpenAI API Key

### Steps to Run the Application Locally

Create a virtual environment (recommended):

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Set up environment variables for AWS and OpenAI API keys.

Create a .env file in the root directory and add your API keys:

env
Copy code

OPENAI_API_KEY=your-api-key-here

AWS_ACCESS_KEY_ID=your-aws-access-key-id

AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key

AWS_DEFAULT_REGION=us-east-1


Run the py app:

Usage
Navigate to the homepage and upload an image of a supplement fact panel.
Customize your input: Specify whether the panel includes other ingredients or contain statements by filling out the form.
Download the result: Once the image is processed, the application will generate an Excel file with the parsed and structured data.
