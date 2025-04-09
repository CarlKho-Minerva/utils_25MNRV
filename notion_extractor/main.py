#!/usr/bin/env python3
"""
Notion Database Extractor

A tool to extract content from Notion databases with enhanced terminal UI
and intelligent session naming.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add the current directory to the path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.extractor import extract_database_content, get_notion_client
from src.utils import extract_database_id_from_url, save_entries_to_files, verify_setup
from src.terminal_ui import display_welcome, ask_for_database_info, show_extraction_progress
from src.terminal_ui import display_extraction_results, display_entry_preview, interactive_entry_viewer
from src.gemini_helper import generate_session_name, summarize_extraction

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="Extract content from Notion databases")
    parser.add_argument("--url", help="URL of the Notion database")
    parser.add_argument("--id", help="ID of the Notion database")
    parser.add_argument("--output", help="Output file name")
    parser.add_argument("--setup", action="store_true", help="Verify setup and configuration")
    parser.add_argument("--interactive", action="store_true", help="Enable interactive mode with enhanced UI")
    parser.add_argument("--view", action="store_true", help="View entries after extraction")

    args = parser.parse_args()

    # Load environment variables from .env file
    load_dotenv()

    # Determine if we should use enhanced UI
    use_enhanced_ui = args.interactive or args.view

    # If enhanced UI is enabled, display welcome screen
    if use_enhanced_ui:
        display_welcome()

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
            if use_enhanced_ui:
                # Use enhanced UI to ask for database info
                db_info = ask_for_database_info()
                if db_info:
                    if db_info["type"] == "url":
                        database_id = extract_database_id_from_url(db_info["value"])
                    else:
                        database_id = db_info["value"]
                else:
                    return
            else:
                # Use traditional CLI interface
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

    try:
        # Get database title for better naming
        database_title = "Notion Database"
        try:
            notion = get_notion_client()
            db_info = notion.databases.retrieve(database_id=database_id)
            database_title = db_info.get("title", [{}])[0].get("plain_text", "Notion Database")
        except:
            pass  # Continue even if we can't get the title
            
        # Extract database content with progress indication
        if use_enhanced_ui:
            print(f"Preparing to extract from database: {database_id}")
            entries = extract_database_content(database_id, verbose=False)
        else:
            # Extract and display traditional progress
            print(f"\n=== Extracting Database Content ===")
            print(f"Database ID: {database_id}")
            print("=" * 35)
            entries = extract_database_content(database_id)

        # Generate a session name using Gemini if available
        session_name = generate_session_name(database_title, entries)
        
        # Determine output file name
        output_name = args.output
        if not output_name and session_name:
            output_name = session_name
        elif not output_name:
            output_name = f"notion_database_{database_id[:8]}"

        # Generate summary if using enhanced UI
        summary = None
        if use_enhanced_ui:
            summary = summarize_extraction(entries)

        # Save the extracted content
        json_path, txt_path = save_entries_to_files(entries, output_name)

        # Display results
        if use_enhanced_ui:
            display_extraction_results(entries, json_path, txt_path, session_name, summary)
            display_entry_preview(entries, 3)
            
            # If view flag is set, show the interactive viewer
            if args.view:
                interactive_entry_viewer(entries)
        else:
            print(f"\n✅ Successfully extracted {len(entries)} entries!")
            print(f"📄 JSON output: {json_path}")
            print(f"📄 Text output: {txt_path}")
            if session_name:
                print(f"🏷️ Session name: {session_name}")

    except Exception as e:
        if use_enhanced_ui:
            from rich.console import Console
            from rich.panel import Panel
            console = Console()
            console.print(Panel(f"[bold red]Error:[/bold red] {str(e)}", 
                               title="Extraction Failed", 
                               border_style="red"))
            console.print("Troubleshooting tips:")
            console.print("1. Run 'python main.py --setup' to verify your setup")
            console.print("2. Make sure you've shared your database with the integration")
            console.print("3. Check your internet connection")
        else:
            print(f"\n❌ Error: {str(e)}")
            print("\nTroubleshooting tips:")
            print("1. Run 'python main.py --setup' to verify your setup")
            print("2. Make sure you've shared your database with the integration")
            print("3. Check your internet connection")

if __name__ == "__main__":
    main()
