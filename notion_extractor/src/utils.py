import os
import re
import sys
import json
import webbrowser
from datetime import datetime

def extract_database_id_from_url(url):
    """Extract database ID from a Notion URL"""
    if not url:
        return None

    # Try to extract using regex pattern for 32-character hex string
    match = re.search(r'([a-f0-9]{32})', url)
    if match:
        return match.group(1)

    # Alternative extraction from URL path
    parts = url.split('/')
    for part in parts:
        if '-' in part and len(part) > 30:
            db_id_part = part.split('?')[0]
            if '-' in db_id_part:
                db_id = db_id_part.split('-')[-1]
                return db_id

    return None

def save_entries_to_files(entries, output_name=None):
    """Save entries to both JSON and TXT formats"""
    if not output_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"notion_extract_{timestamp}"

    # Ensure we have the .json extension
    if not output_name.endswith('.json'):
        json_path = f"{output_name}.json"
    else:
        json_path = output_name
        output_name = output_name[:-5]  # Remove .json for the base name

    # Create text file path
    txt_path = f"{output_name}.txt"

    # Save JSON file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    # Save text file
    with open(txt_path, 'w', encoding='utf-8') as f:
        for i, entry in enumerate(entries):
            f.write(f"ENTRY {i+1}: {entry.get('title', 'No Title')}\n")
            f.write("="*50 + "\n")
            f.write(f"URL: {entry.get('url')}\n")
            f.write(f"Created: {entry.get('created_time')}\n")
            f.write(f"Last Edited: {entry.get('last_edited_time')}\n")
            f.write("-"*50 + "\n")
            f.write(entry.get('body', 'No content') + "\n\n")
            f.write("="*50 + "\n\n")

    return json_path, txt_path

def verify_setup():
    """Verify the setup is correct and guide the user if needed"""
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    print("\n===== Notion Extractor Setup Verification =====\n")

    # Check API key
    api_key = os.environ.get('NOTION_API_KEY')
    if not api_key:
        print("❌ API key not found in .env file")
        print("   Please make sure your .env file contains the API key")
        return False
    else:
        print("✅ API key found in .env file")

    # Check database ID
    db_id = os.environ.get('DEFAULT_DATABASE_ID')
    if not db_id:
        print("⚠️ No default database ID found in .env file")
        print("   You'll need to provide the database ID manually")
    else:
        print(f"✅ Default database ID found: {db_id}")

    # Guide on sharing with integration
    print("\n----- Sharing with Integration -----")
    print("To properly share your Notion database with the integration:")
    print("1. Open your database in Notion")
    print("2. Click the '...' menu in the top-right corner")
    print("3. Select 'Add connections'")
    print("4. Find and select 'mnrv_db_reader'")

    # Ask if they want to open the database
    print("\nWould you like to open your Notion database now? (y/n)")
    choice = input().lower()
    if choice == 'y' or choice == 'yes':
        if db_id:
            webbrowser.open(f"https://www.notion.so/cvk-minerva/{db_id}")
            print("Opening your Notion database...")
        else:
            webbrowser.open("https://www.notion.so/")
            print("Opening Notion...")

    print("\nSetup verification complete!\n")
    return True

def show_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """Display a custom progress bar in the console"""
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')
