import sys
import webbrowser
import os
from dotenv import load_dotenv

def check_setup():
    """Check if the basic setup is correct and guide the user"""
    
    # Load environment variables
    load_dotenv()
    
    print("=== Notion Integration Troubleshooter ===")
    print("\nChecking your setup...")
    
    # Check if API key exists
    api_key = os.environ.get('NOTION_API_KEY')
    if not api_key:
        print("❌ API key not found in environment variables or .env file")
        print("   Please ensure your .env file contains: NOTION_API_KEY=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")
    else:
        print("✅ API key found in environment")
    
    # Guide the user through the sharing process
    print("\n=== Integration Sharing Steps ===")
    print("1. You cannot share with an integration using '@' mentions")
    print("2. Instead, follow these steps:")
    print("   a. Open your database in Notion")
    print("   b. Click on '...' (three dots) in the top-right")
    print("   c. Select 'Add connections'")
    print("   d. Find 'mnrv_db_reader' in the list")
    print("   e. Click to add it to your database\n")
    
    # Ask if they want to open relevant pages
    print("Would you like to open relevant pages to fix the issue?")
    print("1. Open your Notion database")
    print("2. Open Notion integrations page")
    print("3. Open detailed troubleshooting guide")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ")
    
    if choice == '1':
        webbrowser.open("https://www.notion.so/cvk-minerva/17a8ffadd3ae811da847e86bf424a2d7")
        print("Opening your Notion database...")
    elif choice == '2':
        webbrowser.open("https://www.notion.so/my-integrations")
        print("Opening Notion integrations page...")
    elif choice == '3':
        # Open the troubleshooting guide in the default application
        guide_path = os.path.join(os.path.dirname(__file__), "notion_integration_guide.md")
        if os.path.exists(guide_path):
            if sys.platform == "win32":
                os.startfile(guide_path)
            else:
                webbrowser.open('file://' + guide_path)
            print("Opening troubleshooting guide...")
        else:
            print("Guide file not found. Check your installation.")
    elif choice == '4':
        print("Exiting troubleshooter...")
        return
    else:
        print("Invalid choice. Exiting...")
        return
    
    print("\nOnce you've shared your database with the integration, run:")
    print("python extract_ah110_db.py")

if __name__ == "__main__":
    check_setup()
