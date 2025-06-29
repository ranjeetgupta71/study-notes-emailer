import json
import random
import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Set UTF-8 encoding for stdout to handle special characters
sys.stdout.reconfigure(encoding='utf-8')

def load_all_notes():
    """Load all notes from JSON files"""
    notes = []
    notes_dir = 'notes'

    for filename in os.listdir(notes_dir):
        if filename.endswith('.json'):
            try:
                with open(f'{notes_dir}/{filename}', 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Clean problematic characters
                    content = content.replace('\xa0', ' ')  # Replace non-breaking space
                    content = content.replace('\u2022', '•')  # Ensure bullet points are standard
                    category_notes = json.loads(content)
                    notes.extend(category_notes)
                    print(f"✅ Loaded {len(category_notes)} notes from {filename}")
            except Exception as e:
                print(f"❌ Error loading {filename}: {str(e)}")
                continue

    return notes

def create_email_content(note):
    """Create HTML email content"""
    # Clean the note content to handle special characters
    title = note['title'].replace('\xa0', ' ').replace('\u2022', '•')
    category = note['category'].replace('\xa0', ' ')
    content = note['content'].replace('\xa0', ' ').replace('\u2022', '•')
    example = note.get('example', '').replace('\xa0', ' ') if note.get('example') else ''

    html = f"""
    <html>
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
              <div style="white-space: pre-line; font-size: 14px;">
                {content}
              </div>
            </div>

            {f'<div style="background-color: white; padding: 15px; border-radius: 5px; margin-top: 15px;"><h4 style="color: #f39c12; margin-top: 0;">💡 Example:</h4><code style="background-color: #f1f2f6; padding: 10px; display: block; border-radius: 3px;">{example}</code></div>' if example else ''}
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

    # Check if all required environment variables are present
    if not all([email_user, email_pass, to_email]):
        print("❌ Missing email credentials in environment variables")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📚 Daily Revision: {note['title'].replace('\xa0', ' ')}"
        msg['From'] = email_user
        msg['To'] = to_email

        html_content = create_email_content(note)
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        # Gmail SMTP
        print("🔄 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)
        server.send_message(msg)
        server.quit()

        print(f"✅ Email sent successfully: {note['title']}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed. Check your email credentials.")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        return False

def main():
    try:
        print("🚀 Starting Study Notes Emailer...")

        notes = load_all_notes()
        if not notes:
            print("❌ No notes found!")
            return

        print(f"📚 Found {len(notes)} total notes")

        random_note = random.choice(notes)
        print(f"🎯 Selected note: {random_note['title']} ({random_note['category']})")

        success = send_email(random_note)
        if success:
            print("🎉 Mission accomplished! Check your email.")
        else:
            print("❌ Mission failed. Check the logs above.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
