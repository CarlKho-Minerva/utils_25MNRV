import os
import json
from notion_client import Client
import argparse
from dotenv import load_dotenv
from datetime import datetime

def extract_notion_database(database_id, api_key=None):
    """
    Extract all entries from a Notion database
    
    Args:
        database_id: The ID of the Notion database
        api_key: Notion API key (optional, can be loaded from environment)
        
    Returns:
        List of database entries with extracted content
    """
    # Use provided API key or get from environment
    if not api_key:
        if 'NOTION_API_KEY' not in os.environ:
            raise ValueError("Please provide a Notion API key or set NOTION_API_KEY environment variable")
        api_key = os.environ['NOTION_API_KEY']
    
    # Initialize Notion client
    notion = Client(auth=api_key)
    
    # Query the database
    try:
        results = []
        has_more = True
        next_cursor = None
        
        print(f"Fetching database entries...")
        
        while has_more:
            if next_cursor:
                response = notion.databases.query(database_id=database_id, start_cursor=next_cursor)
            else:
                response = notion.databases.query(database_id=database_id)
            
            results.extend(response['results'])
            has_more = response.get('has_more', False)
            next_cursor = response.get('next_cursor')
            
            print(f"Fetched {len(results)} entries so far...")
            
        print(f"Total entries retrieved: {len(results)}")
        
        # Process and extract content from each entry
        processed_entries = []
        
        for entry in results:
            processed_entry = extract_entry_content(entry, notion)
            processed_entries.append(processed_entry)
            
        return processed_entries
    
    except Exception as e:
        print(f"Error querying Notion database: {e}")
        raise

def extract_entry_content(entry, notion_client):
    """
    Extract relevant content from a database entry
    
    Args:
        entry: Notion database entry object
        notion_client: Initialized Notion client for fetching page content
        
    Returns:
        Dictionary with extracted content
    """
    # Initialize content dictionary
    content = {
        "id": entry["id"],
        "url": entry["url"],
        "created_time": entry["created_time"],
        "last_edited_time": entry["last_edited_time"]
    }
    
    # Extract properties (including title)
    properties = entry.get("properties", {})
    for prop_name, prop_data in properties.items():
        prop_type = prop_data.get("type")
        
        if prop_type == "title":
            title_content = prop_data.get("title", [])
            title_text = "".join([text_obj.get("plain_text", "") for text_obj in title_content])
            content["title"] = title_text
        
        # Extract other property types as needed
        elif prop_type == "rich_text":
            rich_text = prop_data.get("rich_text", [])
            text = "".join([text_obj.get("plain_text", "") for text_obj in rich_text])
            content[prop_name] = text
        
        # Add more property type handlers as needed
    
    # Fetch page content (body)
    try:
        page_content = notion_client.blocks.children.list(block_id=entry["id"])
        content["body"] = extract_blocks_content(page_content.get("results", []), notion_client)
    except Exception as e:
        print(f"Error fetching content for entry {entry['id']}: {e}")
        content["body"] = "Error fetching content"
    
    return content

def extract_blocks_content(blocks, notion_client, depth=0):
    """
    Recursively extract content from blocks
    
    Args:
        blocks: List of Notion blocks
        notion_client: Initialized Notion client
        depth: Current recursion depth
        
    Returns:
        Extracted text content
    """
    if depth > 5:  # Prevent infinite recursion
        return ""
    
    content = []
    
    for block in blocks:
        block_type = block.get("type")
        block_id = block.get("id")
        
        if block_type == "paragraph":
            paragraph_text = "".join([text.get("plain_text", "") 
                             for text in block.get("paragraph", {}).get("rich_text", [])])
            content.append(paragraph_text)
        
        elif block_type == "heading_1":
            heading_text = "".join([text.get("plain_text", "") 
                           for text in block.get("heading_1", {}).get("rich_text", [])])
            content.append(f"# {heading_text}")
        
        elif block_type == "heading_2":
            heading_text = "".join([text.get("plain_text", "") 
                           for text in block.get("heading_2", {}).get("rich_text", [])])
            content.append(f"## {heading_text}")
        
        elif block_type == "heading_3":
            heading_text = "".join([text.get("plain_text", "") 
                           for text in block.get("heading_3", {}).get("rich_text", [])])
            content.append(f"### {heading_text}")
        
        elif block_type == "bulleted_list_item":
            item_text = "".join([text.get("plain_text", "") 
                        for text in block.get("bulleted_list_item", {}).get("rich_text", [])])
            content.append(f"• {item_text}")
        
        elif block_type == "numbered_list_item":
            item_text = "".join([text.get("plain_text", "") 
                        for text in block.get("numbered_list_item", {}).get("rich_text", [])])
            content.append(f"1. {item_text}")  # Note: All items will be "1." but it shows the type
        
        elif block_type == "to_do":
            checked = block.get("to_do", {}).get("checked", False)
            item_text = "".join([text.get("plain_text", "") 
                        for text in block.get("to_do", {}).get("rich_text", [])])
            checkbox = "[x]" if checked else "[ ]"
            content.append(f"{checkbox} {item_text}")
        
        elif block_type == "toggle":
            toggle_text = "".join([text.get("plain_text", "") 
                          for text in block.get("toggle", {}).get("rich_text", [])])
            content.append(f"▶ {toggle_text}")
        
        # Handle nested blocks
        if block.get("has_children", False) and block_id:
            try:
                children = notion_client.blocks.children.list(block_id=block_id)
                child_content = extract_blocks_content(
                    children.get("results", []), notion_client, depth + 1
                )
                if child_content:
                    content.append(child_content)
            except Exception as e:
                print(f"Error fetching children for block {block_id}: {e}")
    
    return "\n".join(content)

def save_entries_to_file(entries, output_path=None):
    """
    Save extracted entries to a file
    
    Args:
        entries: List of entry dictionaries
        output_path: Path to save the output (optional)
    """
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"notion_db_content_{timestamp}.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(entries)} entries to {output_path}")
    
    # Also save a text version for easy reading
    text_output = output_path.replace('.json', '.txt')
    with open(text_output, 'w', encoding='utf-8') as f:
        for i, entry in enumerate(entries):
            f.write(f"ENTRY {i+1}: {entry.get('title', 'No Title')}\n")
            f.write("="*50 + "\n")
            f.write(f"URL: {entry.get('url')}\n")
            f.write(f"Created: {entry.get('created_time')}\n")
            f.write(f"Last Edited: {entry.get('last_edited_time')}\n")
            f.write("-"*50 + "\n")
            f.write(entry.get('body', 'No content') + "\n\n")
            f.write("="*50 + "\n\n")
    
    print(f"Saved readable format to {text_output}")

def extract_database_id_from_url(url):
    """Extract database ID from a Notion URL"""
    # Example URL: https://www.notion.so/cvk-minerva/17a8ffadd3ae811da847e86bf424a2d7?v=...
    # We need to extract the 17a8ffadd3ae811da847e86bf424a2d7 part
    
    if not url:
        return None
    
    # Find the database ID in the URL
    # This is a simplified approach; Notion URLs can vary
    parts = url.split('/')
    for part in parts:
        if '-' in part and len(part) > 30:  # Database IDs contain hyphens and are long
            # Extract the ID portion, removing any query parameters
            db_id_part = part.split('?')[0]
            # Sometimes the format is name-databaseId
            if '-' in db_id_part:
                db_id = db_id_part.split('-')[-1]
                return db_id
    
    # Alternative approach: look for a pattern like 17a8ffadd3ae811da847e86bf424a2d7
    import re
    match = re.search(r'([a-f0-9]{32})', url)
    if match:
        return match.group(1)
    
    return None

if __name__ == "__main__":
    # Load environment variables from .env file if present
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Extract content from a Notion database')
    parser.add_argument('--database-id', type=str, help='Notion database ID')
    parser.add_argument('--database-url', type=str, help='Notion database URL')
    parser.add_argument('--api-key', type=str, help='Notion API key')
    parser.add_argument('--output', type=str, help='Output file path')
    
    args = parser.parse_args()
    
    database_id = args.database_id
    if not database_id and args.database_url:
        database_id = extract_database_id_from_url(args.database_url)
        if not database_id:
            print("Could not extract database ID from the provided URL")
            exit(1)
    
    if not database_id:
        print("Please provide a database ID or URL")
        exit(1)
    
    entries = extract_notion_database(database_id, args.api_key)
    save_entries_to_file(entries, args.output)
