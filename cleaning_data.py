import re
import json

def remove_page_number_lines_from_file(file_path, min_leading_spaces=30):
    """
    Reads text file, removes lines that are page numbers or roman numerals 
    based on the pattern, and writes cleaned text back to the same file.
    
    :param file_path: Path to the text file to clean.
    :param min_leading_spaces: Minimum spaces before the number to consider a page line.
    """
    roman_pattern = r"^(x{0,3})(ix|iv|v?i{0,3})$"  # basic roman numerals i to xxx
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    cleaned_lines = []
    for line in lines:
        if len(line) - len(line.lstrip(' ')) >= min_leading_spaces:
            stripped_line = line.strip()
            tokens = stripped_line.split()
            if tokens:
                last_token = tokens[-1].strip().lower()
                # print(f"Checking line: '{line.rstrip()}' | Last token: '{last_token}'")
                if last_token.isdigit():
                    print(" - Removing line: ends with digit", f"'{line.rstrip()}' | Last token: '{last_token}'" )
                    continue
                if re.fullmatch(roman_pattern, last_token, re.IGNORECASE):
                    print(" - Removing line: ends with roman numeral", f"'{line.rstrip()}' | Last token: '{last_token}'")
                    continue
        cleaned_lines.append(line)

    
    with open("page_numbers_removed_text.txt", 'w', encoding='utf-8') as file:
        file.writelines(cleaned_lines)



def extract_and_save_toc(file_path="page_numbers_removed_text.txt", output_json="table_of_content_hirarchy.json"):
    """
    Extracts table of contents hierarchy from text file and saves as JSON.
    Also removes the TOC lines from the original text file.
    
    :param file_path: Path to the cleaned text file.
    :param output_json: Filename for saving TOC hierarchy JSON.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Pattern to identify TOC lines: contain dots and end with a page number (integer)
    toc_line_pattern = re.compile(r"\.+\s*\d+$")
    
    toc_lines = []
    remaining_lines = []
    
    # Separate TOC lines from remaining content
    for line in lines:
        if toc_line_pattern.search(line.strip()):
            toc_lines.append(line.strip())
        else:
            remaining_lines.append(line)
    
    toc = []
    stack = []
    
    for line in toc_lines:
        # Remove trailing page number and dots
        line = re.sub(r"\.+\s*\d+$", "", line).rstrip()
        
        # Extract numbering and title
        match = re.match(r"^(\d+(\.\d+)*)?\s*(.*)$", line)
        section_number = match.group(1) if match.group(1) else ""
        title = match.group(3).strip() if match.group(3) else ""
        title = title.replace(".", "").strip()
        
        if not section_number and stack:
            parent = stack[-1]
            parent.setdefault("children", []).append({"number": "", "title": title, "children": []})
            continue
        
        level = section_number.count(".") if section_number else 0
        
        while stack and stack[-1]["level"] >= level:
            stack.pop()
        
        toc_item = {"number": section_number, "title": title, "children": [], "level": level}
        
        if stack:
            parent = stack[-1]
            parent.setdefault("children", []).append(toc_item)
        else:
            toc.append(toc_item)
        
        stack.append(toc_item)
    
    def remove_levels(items):
        for item in items:
            item.pop("level", None)
            if "children" in item and item["children"]:
                remove_levels(item["children"])
            elif "children" in item and not item["children"]:
                item.pop("children")
    
    remove_levels(toc)
    
    # Save TOC to JSON file
    with open(output_json, 'w', encoding='utf-8') as json_file:
        json.dump(toc, json_file, indent=2, ensure_ascii=False)
    
    # Write back the remaining lines (without TOC) to the original file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(remaining_lines)

# Usage example
extract_and_save_toc()



# Usage example:
# remove_page_number_lines_from_file("extracted_text_layout.txt")

