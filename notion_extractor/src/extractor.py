import os
import time
from notion_client import Client
from tqdm import tqdm
from dotenv import load_dotenv

def get_notion_client():
    """Initialize and return a Notion client with proper authentication"""
    load_dotenv()

    api_key = os.environ.get('NOTION_API_KEY')
    if not api_key:
        raise ValueError("Notion API key not found. Please set it in the .env file.")

    return Client(auth=api_key)

def extract_database_content(database_id, verbose=True):
    """
    Extract all content from a Notion database

    Args:
        database_id: The ID of the Notion database
        verbose: Whether to show progress indicators

    Returns:
        List of processed database entries
    """
    notion = get_notion_client()

    # First, query the database to get all entries
    try:
        if verbose:
            print(f"Connecting to Notion API...")
            print(f"Querying database {database_id}...")

        results = []
        has_more = True
        next_cursor = None

        # Get all pages from the database with pagination
        while has_more:
            if verbose:
                print(f"Fetching page {len(results)//100 + 1}...")

            if next_cursor:
                response = notion.databases.query(database_id=database_id, start_cursor=next_cursor)
            else:
                response = notion.databases.query(database_id=database_id)

            results.extend(response['results'])
            has_more = response.get('has_more', False)
            next_cursor = response.get('next_cursor')

            if verbose:
                print(f"Retrieved {len(results)} entries so far")

        if verbose:
            print(f"Successfully retrieved {len(results)} total entries")
            print("Now extracting content from each entry...")

        # Process each database entry to extract its content
        processed_entries = []

        # Use tqdm for a progress bar if verbose
        iterator = tqdm(results, desc="Extracting entries", unit="entry") if verbose else results

        for entry in iterator:
            processed_entry = process_database_entry(entry, notion)
            processed_entries.append(processed_entry)
            # Add a small delay to avoid API rate limits
            time.sleep(0.1)

        if verbose:
            print(f"Successfully extracted content from all {len(processed_entries)} entries")

        return processed_entries

    except Exception as e:
        print(f"Error extracting database content: {str(e)}")
        raise

def process_database_entry(entry, notion):
    """Extract and process all relevant content from a database entry"""
    # Basic metadata
    processed = {
        "id": entry["id"],
        "url": entry["url"],
        "created_time": entry["created_time"],
        "last_edited_time": entry["last_edited_time"]
    }

    # Extract properties (title, etc.)
    properties = entry.get("properties", {})
    for prop_name, prop_data in properties.items():
        prop_type = prop_data.get("type")

        if prop_type == "title":
            # Extract title
            title_content = prop_data.get("title", [])
            title_text = "".join([text_obj.get("plain_text", "") for text_obj in title_content])
            processed["title"] = title_text

        elif prop_type == "rich_text":
            # Extract rich text properties
            rich_text = prop_data.get("rich_text", [])
            text = "".join([text_obj.get("plain_text", "") for text_obj in rich_text])
            processed[prop_name] = text

        elif prop_type == "select":
            # Extract select properties
            select_data = prop_data.get("select")
            if select_data:
                processed[prop_name] = select_data.get("name")

        elif prop_type == "date":
            # Extract date properties
            date_data = prop_data.get("date")
            if date_data:
                processed[prop_name] = date_data.get("start")

    # Fetch page blocks (body content)
    try:
        page_blocks = notion.blocks.children.list(block_id=entry["id"])
        processed["body"] = extract_blocks_content(page_blocks.get("results", []), notion)
    except Exception as e:
        processed["body"] = f"Error retrieving body content: {str(e)}"

    return processed

def extract_blocks_content(blocks, notion, depth=0):
    """Recursively extract content from blocks and child blocks"""
    if depth > 5:  # Prevent excessive recursion
        return ""

    content = []

    for block in blocks:
        block_type = block.get("type")

        # Extract text based on block type
        if block_type == "paragraph":
            text = extract_rich_text(block.get("paragraph", {}).get("rich_text", []))
            if text:
                content.append(text)

        elif block_type == "heading_1":
            text = extract_rich_text(block.get("heading_1", {}).get("rich_text", []))
            if text:
                content.append(f"# {text}")

        elif block_type == "heading_2":
            text = extract_rich_text(block.get("heading_2", {}).get("rich_text", []))
            if text:
                content.append(f"## {text}")

        elif block_type == "heading_3":
            text = extract_rich_text(block.get("heading_3", {}).get("rich_text", []))
            if text:
                content.append(f"### {text}")

        elif block_type == "bulleted_list_item":
            text = extract_rich_text(block.get("bulleted_list_item", {}).get("rich_text", []))
            if text:
                content.append(f"• {text}")

        elif block_type == "numbered_list_item":
            text = extract_rich_text(block.get("numbered_list_item", {}).get("rich_text", []))
            if text:
                content.append(f"1. {text}")

        elif block_type == "to_do":
            checked = block.get("to_do", {}).get("checked", False)
            text = extract_rich_text(block.get("to_do", {}).get("rich_text", []))
            checkbox = "[x]" if checked else "[ ]"
            if text:
                content.append(f"{checkbox} {text}")

        elif block_type == "toggle":
            text = extract_rich_text(block.get("toggle", {}).get("rich_text", []))
            if text:
                content.append(f"▶ {text}")

        elif block_type == "code":
            language = block.get("code", {}).get("language", "")
            text = extract_rich_text(block.get("code", {}).get("rich_text", []))
            if text:
                content.append(f"```{language}\n{text}\n```")

        elif block_type == "quote":
            text = extract_rich_text(block.get("quote", {}).get("rich_text", []))
            if text:
                content.append(f"> {text}")

        elif block_type == "callout":
            text = extract_rich_text(block.get("callout", {}).get("rich_text", []))
            emoji = block.get("callout", {}).get("icon", {}).get("emoji", "ℹ️")
            if text:
                content.append(f"{emoji} {text}")

        # Handle child blocks by recursively fetching them
        if block.get("has_children", False):
            try:
                children = notion.blocks.children.list(block_id=block["id"])
                child_content = extract_blocks_content(
                    children.get("results", []), notion, depth + 1
                )
                if child_content:
                    # Add indentation for child content based on depth
                    indented_content = "\n".join(["  " * depth + line for line in child_content.split("\n")])
                    content.append(indented_content)
            except Exception:
                pass  # Skip failed children fetches

    return "\n".join(content)

def extract_rich_text(rich_text_list):
    """Extract plain text from a rich text object list"""
    return "".join([text.get("plain_text", "") for text in rich_text_list])
