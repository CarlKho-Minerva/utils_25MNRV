import os
from notion_db_extractor import extract_notion_database, save_entries_to_file

# The URL of your database: https://www.notion.so/cvk-minerva/17a8ffadd3ae811da847e86bf424a2d7?v=17a8ffadd3ae8141b5a6000c9cde58fb&pvs=4
# Database ID extracted from URL
DATABASE_ID = "17a8ffadd3ae811da847e86bf424a2d7"

def main():
    print("Starting extraction of AH110 Notion database")
    print("Database ID:", DATABASE_ID)
    
    # Extract the data
    try:
        entries = extract_notion_database(DATABASE_ID)
        
        # Save to AH110 specific files
        output_path = os.path.join(os.path.dirname(__file__), "ah110_database_content.json")
        save_entries_to_file(entries, output_path)
        
        print("\nExtraction completed successfully!")
        print(f"Extracted {len(entries)} entries from your AH110 database")
        print(f"Data saved to: {output_path} and {output_path.replace('.json', '.txt')}")
    
    except Exception as e:
        print(f"Error extracting database content: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you've shared the database with your integration")
        print("   - Go to your database in Notion")
        print("   - Click 'Share' in the top right")
        print("   - Type '@mnrv_db_reader' and select your integration")
        print("   - Click 'Invite'")
        print("2. Verify your API key in the .env file is correct")
        print("3. Check your internet connection")

if __name__ == "__main__":
    main()
