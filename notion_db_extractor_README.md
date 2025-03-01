# Notion Database Extractor

This tool extracts content (including title and body) from Notion databases using the Notion API.

## Setup

1. **Create a Notion Integration**:
   - Go to https://www.notion.so/my-integrations
   - Create a new integration
   - Give it a name and icon
   - Copy the API key

2. **Share the database with your integration**:
   - Go to your database in Notion
   - Click "Share" in the top right
   - Use the "@" symbol and type your integration's name
   - Click "Invite"

3. **Install dependencies**:
   ```bash
   pip install notion-client python-dotenv
   ```

4. **Set up your API key**:
   - Create a `.env` file in the same directory as the script
   - Add `NOTION_API_KEY=your_api_key_here`
   - Or pass it directly using the `--api-key` parameter

## Usage

Extract content from a Notion database using the URL:

```bash
python notion_db_extractor.py --database-url "https://www.notion.so/cvk-minerva/17a8ffadd3ae811da847e86bf424a2d7?v=..."
```

Or with the database ID directly:

```bash
python notion_db_extractor.py --database-id "17a8ffadd3ae811da847e86bf424a2d7"
```

Specify an output file (optional):

```bash
python notion_db_extractor.py --database-url "..." --output "my_database_content.json"
```

## Output

The script produces two output files:
- A JSON file with all the structured data
- A text file with a more readable format

## Database ID

The database ID can be extracted from your Notion URL:
- For example, from `https://www.notion.so/cvk-minerva/17a8ffadd3ae811da847e86bf424a2d7?v=...` 
- The ID would be `17a8ffadd3ae811da847e86bf424a2d7`
