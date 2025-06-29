import json
import random
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sys

def safe_str(text):
    """Convert any text to ASCII-safe string"""
    if not isinstance(text, str):
        text = str(text)

    # Remove or replace problematic Unicode characters
    replacements = {
        '\xa0': ' ',           # Non-breaking space
        '\u2019': "'",         # Right single quotation mark
        '\u2018': "'",         # Left single quotation mark
        '\u201c': '"',         # Left double quotation mark
        '\u201d': '"',         # Right double quotation mark
        '\u2013': '-',         # En dash
        '\u2014': '--',        # Em dash
        '\u2026': '...',       # Horizontal ellipsis
        '\u2022': '*',         # Bullet point
        '\u00a9': '(c)',       # Copyright symbol
        '\u00ae': '(R)',       # Registered trademark
        '\u2122': '(TM)',      # Trademark symbol
    }

    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)

    # Convert to ASCII, ignoring any remaining problematic characters
    try:
        text = text.encode('ascii', 'ignore').decode('ascii')
    except:
        # If all else fails, keep only basic ASCII characters
        text = ''.join(char for char in text if ord(char) < 128)

    # Clean up extra whitespace
    return ' '.join(text.split())

def load_all_notes():
    """Load all notes from JSON files with safe encoding"""
    notes = []
    notes_dir = 'notes'

    try:
        if not os.path.exists(notes_dir):
            print(f"Notes directory '{notes_dir}' not found!")
            return []

        json_files = [f for f in os.listdir(notes_dir) if f.endswith('.json')]

        if not json_files:
            print("No JSON files found in notes directory!")
            return []

        for filename in json_files:
            file_path = os.path.join(notes_dir, filename)
            print(f"Loading {filename}...")

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Clean the entire JSON content first
                    content = safe_str(content)
                    category_notes = json.loads(content)

                # Clean each note's fields
                cleaned_notes = []
                for note in category_notes:
                    cleaned_note = {
                        'title': safe_str(note.get('title', 'Untitled')),
                        'category': safe_str(note.get('category', 'General')),
                        'content': safe_str(note.get('content', 'No content')),
                    }
                    if 'example' in note and note['example']:
                        cleaned_note['example'] = safe_str(note.get('example', ''))

                    cleaned_notes.append(cleaned_note)

                notes.extend(cleaned_notes)
                print(f"Loaded {len(cleaned_notes)} notes from {filename}")

            except json.JSONDecodeError as e:
                print(f"JSON error in {filename}: {e}")
                continue
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                continue

        print(f"Total notes loaded: {len(notes)}")
        return notes

    except Exception as e:
        print(f"Error accessing notes directory: {e}")
        return []

def create_email_content(note):
    """Create HTML email content with safe ASCII content"""

    title = note.get('title', 'Study Note')
    category = note.get('category', 'General')
    content = note.get('content', 'No content available')
    example = note.get('example', '')

    # Convert newlines to HTML breaks
    content_html = content.replace('\n', '<br>')

    # Build example section if it exists
    example_section = ''
    if example:
        example_html = example.replace('<', '&lt;').replace('>', '&gt;')
        example_section = f'''
        <div style="background-color: white; padding: 15px; border-radius: 5px; margin-top: 15px;">
            <h4 style="color: #f39c12; margin-top: 0;">Example:</h4>
            <div style="background-color: #f1f2f6; padding: 10px; border-radius: 3px; font-family: monospace;">
                {example_html}
            </div>
        </div>'''

    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Daily Study Note</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
            Daily Study Revision
        </h2>

        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #e74c3c; margin-top: 0;">
                {title}
            </h3>

            <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <p style="margin: 0;"><strong>Category:</strong>
                    <span style="background-color: #3498db; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">
                        {category}
                    </span>
                </p>
            </div>

            <div style="background-color: white; padding: 15px; border-radius: 5px;">
                <h4 style="color: #27ae60; margin-top: 0;">Content:</h4>
                <div style="font-size: 14px;">
                    {content_html}
                </div>
            </div>

            {example_section}
        </div>

        <div style="text-align: center; margin-top: 30px; padding: 15px; background-color: #ecf0f1; border-radius: 5px;">
            <p style="margin: 0; color: #7f8c8d; font-size: 12px;">
                Sent on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </p>
            <p style="margin: 5px 0 0 0; color: #7f8c8d; font-size: 12px;">
                Keep studying! Next email tomorrow!
            </p>
        </div>
    </div>
</body>
</html>'''

    return html

def send_email(note):
    """Send email with the selected note"""
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    to_email = os.getenv('TO_EMAIL')

    if not all([email_user, email_pass, to_email]):
        raise ValueError("Missing email configuration. Check EMAIL_USER, EMAIL_PASS, and TO_EMAIL environment variables.")

    title = note.get('title', 'Study Note')

    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Daily Revision: {title}"
    msg['From'] = email_user
    msg['To'] = to_email

    # Create HTML content
    html_content = create_email_content(note)
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)

    try:
        print("Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)

        print("Sending email...")
        server.send_message(msg)
        server.quit()

        print(f"Email sent successfully: {title}")

    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication failed. Check your email credentials.")
        raise
    except Exception as e:
        print(f"Error sending email: {e}")
        raise

def main():
    try:
        print("Starting Study Notes Emailer...")

        # Load notes
        notes = load_all_notes()
        if not notes:
            print("No notes found! Please add some notes to the notes/ directory.")
            sys.exit(1)

        # Select random note
        random_note = random.choice(notes)
        print(f"Selected note: {random_note.get('title', 'Unknown')}")
        print(f"Category: {random_note.get('category', 'Unknown')}")

        # Send email
        send_email(random_note)
        print("Process completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
