# Notion Database Extractor

A simple tool for extracting content from Notion databases.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Extract content from your database
python main.py
```

## Setup Instructions

1. **Create a Notion Integration** (already done)
   - Integration name: mnrv_db_reader
   - API key: Already configured in .env file

2. **Share your database with the integration**
   - Open your database in Notion
   - Click the "..." menu in the top-right corner
   - Select "Add connections"
   - Find and select "mnrv_db_reader"

## Files Explained

- `main.py` - Main entry point with interactive menu
- `.env` - Stores your API key
- `src/extractor.py` - Core database extraction logic
- `src/utils.py` - Helper functions
- `requirements.txt` - Project dependencies

## Troubleshooting

If you encounter any issues:

1. Run `python main.py --setup` to verify your configuration
2. Check that the database is shared with your integration
3. Verify your API key in the `.env` file
