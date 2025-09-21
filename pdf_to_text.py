import subprocess

def extract_text_with_layout(pdf_path):
    command = ['pdftotext', '-layout', pdf_path, '-']
    try:
        output = subprocess.check_output(command)
        text = output.decode('utf-8')
        return text
    except subprocess.CalledProcessError as e:
        print(f"Error extracting text: {e}")
        return None

# Usage
pdf_file = "Driver's Handbook 2024-25 - drivers_handbook.pdf"
text = extract_text_with_layout(pdf_file)
if text:
    with open("extracted_text_layout.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Text extracted with layout preserved and saved to 'extracted_text_layout.txt'")
