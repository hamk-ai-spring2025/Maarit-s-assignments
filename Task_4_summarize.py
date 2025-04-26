import argparse
import os
from embedchain import App
import requests
from bs4 import BeautifulSoup
from docx import Document
from pypdf import PdfReader
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Function to process a URL and extract text
def process_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

# Function to initialize EmbedChain app and process input files or URL content
def process_with_embedchain(input_files, query=None, url_content=None):
    app = App()
    app.reset()

    # Process input files
    for file in input_files:
        ext = os.path.splitext(file)[1].lower()
        print(f"Processing file: {file} with extension: {ext}")
        if ext == '.csv':
            with open(file, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            print(f"Extracted CSV content (first 500 characters): {csv_content[:500]}")
            app.add(csv_content, data_type='text')
        elif ext == '.docx':
            doc = Document(file)
            doc_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            print(f"Extracted DOCX content (first 500 characters): {doc_text[:500]}")
            app.add(doc_text, data_type='text')
        elif ext == '.pdf':
            pdf_reader = PdfReader(file)
            pdf_text = "".join([page.extract_text() for page in pdf_reader.pages])
            print(f"Extracted PDF content (first 500 characters): {pdf_text[:500]}")
            app.add(pdf_text, data_type='text')
        elif ext == '.txt':
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"Extracted TXT content (first 500 characters): {content[:500]}")
            app.add(content, data_type='text')
        else:
            print(f"Unsupported file type: {ext}")

    # Process URL content if provided
    if url_content:
        print("Adding URL content to EmbedChain.")
        app.add(url_content, data_type='text')

    # Execute the query
    query = query or "Summarize the content"
    print(f"Executing query: {query}")
    result = app.query(query)

    # Handle the query result
    if isinstance(result, tuple):
        answer, _ = result
    else:
        answer = result

    print("Query result obtained.")
    return answer

# CLI entry point
def main():
    parser = argparse.ArgumentParser(description="Process and summarize text from various sources.")
    parser.add_argument('-f', '--file', nargs='+', help='Input file(s) (text, csv, docx, pdf)')
    parser.add_argument('-u', '--url', help='URL to extract text from')
    parser.add_argument('-q', '--query', help='Custom query to run on the data')
    parser.add_argument('-o', '--output', help='File to output the result to')

    args = parser.parse_args()

    # Ensure at least one input source is provided
    if not args.file and not args.url:
        print("Error: You must provide at least one input source: a file (-f) or a URL (-u).")
        return

    result = ""
    if args.url:
        print(f"Processing URL: {args.url}")
        url_content = process_url(args.url)
        result = process_with_embedchain([], query=args.query, url_content=url_content)
    elif args.file:
        print(f"Processing files: {args.file}")
        result = process_with_embedchain(args.file, query=args.query)

    # Output the result
    if result:
        if args.output:
            print(f"Writing result to: {args.output}")
            with open(args.output, 'w') as output_file:
                output_file.write(result)
        else:
            print("Result:")
            print(result)
    else:
        print("No result was generated.")

if __name__ == "__main__":
    main()