import json
import random
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sys

# Set UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def clean_text(text):
    """Clean text by removing problematic Unicode characters and normalizing"""
    if isinstance(text, str):
        # Replace non-breaking space with regular space
        text = text.replace('\xa0', ' ')
        # Replace other problematic Unicode characters
        text = text.replace('\u2019', "'")  # Right single quotation mark
        text = text.replace('\u2018', "'")  # Left single quotation mark
        text = text.replace('\u201c', '"')  # Left double quotation mark
        text = text.replace('\u201d', '"')  # Right double quotation mark
        text = text.replace('\u2013', '-')  # En dash
        text = text.replace('\u2014', '--') # Em dash
        text = text.replace('\u2026', '...') # Horizontal ellipsis
        # Normalize multiple spaces
        text = ' '.join(text.split())
    return text

def load_all_notes():
    """Load all notes from JSON files"""
    notes = []
    notes_dir = 'notes'

    try:
        for filename in os.listdir(notes_dir):
            if filename.endswith('.json'):
                file_path = f'{notes_dir}/{filename}'
                print(f"📁 Loading {filename}...")

                with open(file_path, 'r', encoding='utf-8') as f:
                    category_notes = json.load(f)

                    # Clean all text fields in each note
                    for note in category_notes:
                        note['title'] = clean_text(note.get('title', ''))
                        note['category'] = clean_text(note.get('category', ''))
                        note['content'] = clean_text(note.get('content', ''))
                        if 'example' in note:
                            note['example'] = clean_text(note.get('example', ''))

                    notes.extend(category_notes)
                    print(f"✅ Loaded {len(category_notes)} notes from {filename}")

        print(f"📚 Total notes loaded: {len(notes)}")
        return notes

    except Exception as e:
        print(f"❌ Error loading notes: {str(e)}")
        return []

def create_email_content(note):
    """Create HTML email content with proper encoding"""

    # Ensure all note fields are properly cleaned
    title = clean_text(note.get('title', 'Untitled'))
    category = clean_text(note.get('category', 'General'))
    content = clean_text(note.get('content', 'No content available'))
    example = clean_text(note.get('example', '')) if note.get('example') else ''

    # Convert newlines to HTML breaks for content
    content_html = content.replace('\n', '<br>')

    html = f"""
    <html>
      <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      </head>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
            📚 Daily Study Revision
          </h2>

          <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #e74c3c; margin-top: 0;">
              🎯 {title}
            </h3>

            <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
              <p style="margin: 0;"><strong>Category:</strong>
                <span style="background-color: #3498db; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">
                  {category}
                </span>
              </p>
            </div>

            <div style="background-color: white; padding: 15px; border-radius: 5px;">
              <h4 style="color: #27ae60; margin-top: 0;">📝 Content:</h4>
              <div style="font-size: 14px;">
                {content_html}
              </div>
            </div>

            {f'''<div style="background-color: white; padding: 15px; border-radius: 5px; margin-top: 15px;">
            <h4 style="color: #f39c12; margin-top: 0;">💡 Example:</h4>
            <div style="background-color: #f1f2f6; padding: 10px; border-radius: 3px; font-family: monospace;">
            {example.replace('<', '&lt;').replace('>', '&gt;')}
            </div>
            </div>''' if example else ''}
          </div>

          <div style="text-align: center; margin-top: 30px; padding: 15px; background-color: #ecf0f1; border-radius: 5px;">
            <p style="margin: 0; color: #7f8c8d; font-size: 12px;">
              ⏰ Sent on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </p>
            <p style="margin: 5px 0 0 0; color: #7f8c8d; font-size: 12px;">
              Keep studying! 💪 Next email tomorrow!
            </p>
          </div>
        </div>
      </body>
    </html>
    """
    return html

def send_email(note):
    """Send email with the selected note"""
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    to_email = os.getenv('TO_EMAIL')

    if not all([email_user, email_pass, to_email]):
        raise ValueError("Missing email configuration. Check your GitHub secrets.")

    # Clean the title for the subject line
    clean_title = clean_text(note.get('title', 'Study Note'))

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📚 Daily Revision: {clean_title}"
    msg['From'] = email_user
    msg['To'] = to_email

    # Set charset to UTF-8
    msg.set_charset('utf-8')

    html_content = create_email_content(note)
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)

    try:
        # Gmail SMTP with better error handling
        print("📧 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)

        print("📤 Sending email...")
        server.send_message(msg)
        server.quit()

        print(f"✅ Email sent successfully: {clean_title}")

    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication failed. Check your email credentials.")
        raise
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {str(e)}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        raise

def main():
    try:
        print("🚀 Starting Study Notes Emailer...")

        notes = load_all_notes()
        if not notes:
            print("❌ No notes found!")
            return

        print("🎲 Selecting random note...")
        random_note = random.choice(notes)

        print(f"📚 Selected: {clean_text(random_note.get('title', 'Unknown'))}")
        print(f"📂 Category: {clean_text(random_note.get('category', 'Unknown'))}")

        send_email(random_note)
        print("🎉 Process completed successfully!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        # Print more detailed error info for debugging
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
