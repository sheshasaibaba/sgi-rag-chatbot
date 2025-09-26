import json
import re

def estimate_tokens(text):
    return len(text) // 4  # Rough character-to-token estimate

def split_by_sentences(text, max_tokens):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence_tokens = estimate_tokens(sentence)
        current_tokens = estimate_tokens(current_chunk)

        if current_tokens + sentence_tokens > max_tokens:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def split_large_chunks(sections, max_tokens=800):
    result = []

    for section in sections:
        content = section.get("content", "")
        if content and estimate_tokens(content) > max_tokens:
            # Split the large content into smaller chunks
            sub_chunks = split_by_sentences(content, max_tokens)
            # For each chunk, create a new section with the title as Part N
            for i, chunk in enumerate(sub_chunks):
                new_section = {
                    "number": section.get("number", ""),
                    "title": f"{section.get('title', '')} (Part {i+1})",
                    "content": chunk,
                    "tables": section.get("tables", []),
                    "children": []  # Optionally can handle children differently here
                }
                result.append(new_section)
        else:
            # If content small, keep as is
            # Recursively split children too if exist
            if "children" in section and section["children"]:
                section["children"] = split_large_chunks(section["children"], max_tokens)
            result.append(section)

    return result

def main(input_json="chunked_data.json", output_json="optimally_chunked_data.json", max_tokens=800):
    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    optimally_chunked = split_large_chunks(data, max_tokens)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(optimally_chunked, f, indent=2, ensure_ascii=False)

# Usage
main()
