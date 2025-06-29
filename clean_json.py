import json
import os
import re

def clean_json_files():
    """Clean all JSON files in the notes directory"""
    notes_dir = 'notes'

    for filename in os.listdir(notes_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(notes_dir, filename)
            print(f"Cleaning {filename}...")

            # Read the file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Replace problematic characters
            replacements = {
                '\xa0': ' ',           # Non-breaking space
                '\u00a0': ' ',         # Non-breaking space (alternative)
                '\u2019': "'",         # Right single quotation mark
                '\u2018': "'",         # Left single quotation mark
                '\u201c': '"',         # Left double quotation mark
                '\u201d': '"',         # Right double quotation mark
                '\u2013': '-',         # En dash
                '\u2014': '--',        # Em dash
                '\u2026': '...',       # Horizontal ellipsis
                '\u2022': '*',         # Bullet point
            }

            for unicode_char, replacement in replacements.items():
                content = content.replace(unicode_char, replacement)

            # Remove any remaining non-ASCII characters (except newlines and tabs)
            content = ''.join(char for char in content if ord(char) < 128)

            # Write back the cleaned content
            with open(file_path, 'w', encoding='ascii', errors='ignore') as f:
                f.write(content)

            print(f"Cleaned {filename}")

if __name__ == "__main__":
    clean_json_files()
    print("All JSON files cleaned!")
