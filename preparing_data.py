import json
import re

def normalize_text(text):
    """Normalize text for comparison: lowercase and single spaces"""
    return re.sub(r'\s+', ' ', text.lower().strip())

def find_section_start(lines, number, title, start_index, end_index):
    """Find the starting line index of a section within a range"""
    search_patterns = []
    if number and title:
        search_patterns.append(normalize_text(f"{number} {title}"))
    if title:
        search_patterns.append(normalize_text(title))
    
    for i in range(start_index, min(end_index, len(lines))):
        line_normalized = normalize_text(lines[i])
        for pattern in search_patterns:
            if pattern in line_normalized:
                return i
    return -1

def extract_content_without_header(lines, start_idx, end_idx, header_pattern):
    """Extract content and remove the header line and any duplicate headers"""
    if start_idx >= end_idx:
        return ""
    
    content_lines = lines[start_idx:end_idx]
    
    # Remove the header line and any duplicate headers
    cleaned_lines = []
    for line in content_lines:
        line_normalized = normalize_text(line)
        if header_pattern in line_normalized:
            continue
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def process_sections(lines, sections, parent_start, parent_end):
    """Recursively process sections and subsections within a parent range"""
    results = []
    
    for i, section in enumerate(sections):
        number = section.get('number', '')
        title = section.get('title', '')
        
        # Find start of this section within parent range
        section_start = find_section_start(lines, number, title, parent_start, parent_end)
        if section_start == -1:
            continue
        
        # Find end of this section (start of next section at same level or parent's end)
        section_end = parent_end
        if i < len(sections) - 1:
            next_section = sections[i + 1]
            next_number = next_section.get('number', '')
            next_title = next_section.get('title', '')
            section_end = find_section_start(lines, next_number, next_title, section_start + 1, parent_end)
            if section_end == -1:
                section_end = parent_end
        
        # Extract content for this section (from after header to before first child)
        children = section.get('children', [])
        content_end = section_end
        
        if children:
            # Find the first child to determine where this section's content ends
            first_child = children[0]
            child_number = first_child.get('number', '')
            child_title = first_child.get('title', '')
            first_child_start = find_section_start(lines, child_number, child_title, section_start + 1, section_end)
            if first_child_start != -1:
                content_end = first_child_start
        
        # Create header pattern for this section to exclude from content
        header_pattern = normalize_text(f"{number} {title}") if number else normalize_text(title)
        
        # Extract content (skip the header line)
        content = extract_content_without_header(lines, section_start + 1, content_end, header_pattern)
        
        # Process children recursively (within this section's boundaries)
        children_content = process_sections(lines, children, content_end, section_end)
        
        # Build result object
        result = {
            "number": number,
            "title": title,
            "content": content,
            "tables": [],
            "children": children_content
        }
        results.append(result)
    
    return results

def main(text_file_path, json_file_path):
    # Read text file
    with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    lines = text.split('\n')
    
    # Read JSON TOC
    with open(json_file_path, 'r', encoding='utf-8') as f:
        toc = json.load(f)
    
    # Process all sections
    chunked_data = process_sections(lines, toc, 0, len(lines))
    
    # Save results
    with open('chunked_data.json', 'w', encoding='utf-8') as f:
        json.dump(chunked_data, f, indent=2, ensure_ascii=False)
        
if __name__ == "__main__":
    main('page_numbers_removed_text.txt', 'table_of_content_hirarchy.json')