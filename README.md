# 📚 Study Notes Emailer

Automated daily email system that sends random study notes for revision using GitHub Actions.

## ✨ Features

- 📧 Daily automated emails with random notes
- 🎯 Multiple categories (DSA, OS, DBMS)
- 🎨 Beautiful HTML email formatting
- 🔄 Easy note management via JSON files
- 💰 Completely FREE using GitHub Actions
- ⚡ Manual trigger option for testing

## 🚀 Quick Setup

### 1. Fork/Clone this repository

### 2. Set up Gmail App Password

1. Enable 2-factor authentication in Gmail
2. Go to Google Account > Security > App passwords
3. Generate new app password for this project

### 3. Add GitHub Secrets

Go to Repository Settings > Secrets and variables > Actions:

- `EMAIL_USER`: Your Gmail address
- `EMAIL_PASS`: Gmail App Password (from step 2)
- `TO_EMAIL`: Email where you want to receive notes

### 4. Test the workflow

- Go to Actions tab
- Run "Daily Study Notes Email" manually
- Check your email!

## 📝 Adding Notes

Add your notes in JSON format to the `notes/` directory:

```json
[
  {
    "title": "Your Topic",
    "category": "Subject",
    "content": "Your detailed notes here...",
    "example": "Optional example"
  }
]
