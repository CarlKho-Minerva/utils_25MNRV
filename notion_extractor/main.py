#!/usr/bin/env python3
"""
Notion Database Extractor

A tool to extract content from Notion databases.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add the current directory to the path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.extractor import extract_database_content
from src.utils import extract_database_id_from_url, save_entries_to_files, verify_setup

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="Extract content from Notion databases")
    parser.add_argument("--url", help="URL of the Notion database")
    parser.add_argument("--id", help="ID of the Notion database")
    parser.add_argument("--output", help="Output file name")
    parser.add_argument("--setup", action="store_true", help="Verify setup and configuration")
    
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # If setup flag is provided, just verify setup and exit
    if args.setup:
        verify_setup()
        return
    
    # Determine the database ID to use
    database_id = None
    
    # Use command-line args if provided
    if args.id:
        database_id = args.id
    elif args.url:
        database_id = extract_database_id_from_url(args.url)
    
    # If no ID provided, use the default or prompt the user
    if not database_id:
        database_id = os.environ.get('DEFAULT_DATABASE_ID')
        
        # If still no ID, prompt the user
        if not database_id:
            print("\nNo database ID provided. Please enter one:")
            print("1. Enter a Notion database URL")
            print("2. Enter a Notion database ID directly")
            print("3. Verify setup first")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                url = input("Enter the Notion database URL: ")
                database_id = extract_database_id_from_url(url)
                if not database_id:
                    print("Could not extract a valid database ID from that URL.")
                    return
            elif choice == '2':
                database_id = input("Enter the Notion database ID: ")
            elif choice == '3':
                verify_setup()
                return
            else:
                print("Exiting...")
                return
    
    # Determine output file name
    output_name = args.output
    if not output_name:
        output_name = f"notion_database_{database_id[:8]}"
    
    # Extract and save the database content
    print(f"\n=== Extracting Database Content ===")
    print(f"Database ID: {database_id}")
    print(f"Output Name: {output_name}")
    print("=" * 35)
    
    try:
        entries = extract_database_content(database_id)
        json_path, txt_path = save_entries_to_files(entries, output_name)
        
        print(f"\n✅ Successfully extracted {len(entries)} entries!")
        print(f"📄 JSON output: {json_path}")
        print(f"📄 Text output: {txt_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Run 'python main.py --setup' to verify your setup")
        print("2. Make sure you've shared your database with the integration")
        print("3. Check your internet connection")

if __name__ == "__main__":
    main()
