AI OCR Tool
This project is a web application built with Flask that allows users to upload product label images (e.g., Nutrition Facts or Supplement Facts panels). The application leverages AWS Textract for Optical Character Recognition (OCR) and OpenAI's GPT model for enhanced data formatting and extraction. The extracted data is then processed, cleaned, and returned as an Excel file.

Features
Image Upload: Users can upload an image of a product label.
OCR with AWS Textract: The application uses AWS Textract to extract text from uploaded images.
Data Cleaning: The extracted text is cleaned and categorized into nutritional facts and other ingredients.
AI Formatting: OpenAI's GPT model formats the cleaned data into a structured JSON format.
Excel Export: The processed data is exported as an Excel file with multiple sheets (Nutritional Info, Other Ingredients, Extracted Lines).
Error Handling: Handles various errors like AWS client errors, invalid uploads, and JSON parsing issues.
Prerequisites
Before running the application, ensure you have the following:

Python 3.9 or higher.
An AWS account with configured AWS Textract and valid credentials.
An OpenAI API key for GPT model access.
Installed dependencies (listed in requirements.txt).
