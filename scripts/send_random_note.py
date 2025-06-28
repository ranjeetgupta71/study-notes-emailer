import json
import random
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def load_all_notes():
    """Load all notes from JSON files"""
    notes = []
    notes_dir = 'notes'

    for filename in os.listdir(notes_dir):
        if filename.endswith('.json'):
            with open(f'{notes_dir}/{filename}', 'r', encoding='utf-8') as f:
                category_notes = json.load(f)
                notes.extend(category_notes)

    return notes

def create_email_content(note):
    """Create HTML email content"""
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
            📚 Daily Study Revision
          </h2>

          <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #e74c3c; margin-top: 0;">
              🎯 {note['title']}
            </h3>

            <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
              <p style="margin: 0;"><strong>Category:</strong>
                <span style="background-color: #3498db; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">
                  {note['category']}
                </span>
              </p>
            </div>

            <div style="background-color: white; padding: 15px; border-radius: 5px;">
              <h4 style="color: #27ae60; margin-top: 0;">📝 Content:</h4>
              <div style="white-space: pre-line; font-size: 14px;">
                {note['content']}
              </div>
            </div>

            {f'<div style="background-color: white; padding: 15px; border-radius: 5px; margin-top: 15px;"><h4 style="color: #f39c12; margin-top: 0;">💡 Example:</h4><code style="background-color: #f1f2f6; padding: 10px; display: block; border-radius: 3px;">{note["example"]}</code></div>' if note.get('example') else ''}
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

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📚 Daily Revision: {note['title']}"
    msg['From'] = email_user
    msg['To'] = to_email

    html_content = create_email_content(note)
    msg.attach(MIMEText(html_content, 'html'))

    # Gmail SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_user, email_pass)
    server.send_message(msg)
    server.quit()

    print(f"✅ Email sent successfully: {note['title']}")

def main():
    try:
        notes = load_all_notes()
        if not notes:
            print("❌ No notes found!")
            return

        random_note = random.choice(notes)
        send_email(random_note)

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
