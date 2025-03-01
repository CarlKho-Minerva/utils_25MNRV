# Notion Integration Sharing Guide

You're seeing the error `"@mnrv_db_reader" is not a valid email` because Notion integrations are not shared using the regular "@" mention method. Here's how to properly share your database with your integration:

## Correct Way to Share with an Integration

1. **Open your database** in Notion (https://www.notion.so/cvk-minerva/17a8ffadd3ae811da847e86bf424a2d7)

2. **Click on the "..." (three dots)** menu in the top-right corner

3. **Select "Add connections"** from the dropdown menu
   - If you don't see "Add connections", look for similar options like "Connections" or "Integrations"

4. **Find and select "mnrv_db_reader"** from the list of available integrations
   - The integration should appear in this list if it's properly set up

5. **Click "Confirm"** to grant the integration access to your database

## Troubleshooting

If you don't see your integration in the list:

### 1. Verify Integration Setup

Make sure your integration is properly set up:
- Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
- Confirm "mnrv_db_reader" is listed and active
- Check that it's associated with the correct workspace

### 2. Check Workspace Association

Your integration must be associated with the workspace containing your database:
- When you created the integration, you selected a specific workspace
- The integration can only access content in that workspace
- If your database is in a different workspace, you'll need to create a new integration for that workspace

### 3. Integration Capabilities

Ensure your integration has the proper capabilities:
- Edit your integration at [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
- Under "Capabilities", make sure "Read content" is enabled
- Save your changes and try sharing again

### 4. Browser Issues

Sometimes clearing cache or using a different browser can help:
- Clear your browser cache
- Try a different browser
- Try the Notion desktop app

## Alternative Sharing Method

If the above doesn't work, you can also try this alternative method:

1. Open your database
2. Click "Share" in the top-right corner
3. In the sharing modal, look for a section labeled "Connections" or "Integrations"
4. Your integration may be listed there to enable access

## Need More Help?

- Check [Notion's API documentation](https://developers.notion.com/docs/getting-started)
- Visit [Notion's support page](https://www.notion.so/help/guides/what-is-an-integration)
