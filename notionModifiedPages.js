const fs = require('fs').promises;
const path = require('path');
const { Client } = require('@notionhq/client');

/**
 * Gets Notion pages that were modified after the specified timestamp
 * @param {Object} options
 * @param {string} options.authToken - Notion API token
 * @param {string} options.databaseId - Notion database ID
 * @param {Date|string} [options.sinceTimestamp] - Only fetch pages modified after this timestamp
 * @param {Object} [options.additionalFilter] - Additional filters to apply to the query
 * @returns {Promise<Array>} Array of pages modified since the timestamp
 */
async function getModifiedNotionPages(options) {
  const { authToken, databaseId, sinceTimestamp, additionalFilter = {} } = options;

  const notion = new Client({ auth: authToken });

  // Build the filter
  let filter = {};

  if (sinceTimestamp) {
    filter = {
      property: 'last_edited_time',
      date: {
        after: sinceTimestamp instanceof Date ? sinceTimestamp.toISOString() : sinceTimestamp
      }
    };

    // If there are additional filters, combine them
    if (Object.keys(additionalFilter).length > 0) {
      filter = {
        and: [filter, additionalFilter]
      };
    }
  } else if (Object.keys(additionalFilter).length > 0) {
    filter = additionalFilter;
  }

  // Query the database with filters
  const queryOptions = {
    database_id: databaseId,
    sorts: [{ timestamp: 'last_edited_time', direction: 'descending' }]
  };

  if (Object.keys(filter).length > 0) {
    queryOptions.filter = filter;
  }

  const response = await notion.databases.query(queryOptions);
  return response.results;
}

/**
 * Stores the last check timestamp
 * @param {string} key - Identifier for this particular check
 * @param {Date} timestamp - Timestamp to store
 * @param {string} [storePath='./notion_timestamps.json'] - Path to store timestamps
 */
async function storeLastCheckTimestamp(key, timestamp = new Date(), storePath = './notion_timestamps.json') {
  let timestamps = {};

  try {
    const data = await fs.readFile(storePath, 'utf-8');
    timestamps = JSON.parse(data);
  } catch (error) {
    // File doesn't exist or couldn't be parsed, use empty object
  }

  timestamps[key] = timestamp.toISOString();

  await fs.writeFile(storePath, JSON.stringify(timestamps, null, 2), 'utf-8');
  return timestamp;
}

/**
 * Gets the last check timestamp
 * @param {string} key - Identifier for this particular check
 * @param {string} [storePath='./notion_timestamps.json'] - Path where timestamps are stored
 * @returns {string|null} The timestamp as ISO string or null if not found
 */
async function getLastCheckTimestamp(key, storePath = './notion_timestamps.json') {
  try {
    const data = await fs.readFile(storePath, 'utf-8');
    const timestamps = JSON.parse(data);
    return timestamps[key] || null;
  } catch (error) {
    return null;
  }
}

/**
 * Gets pages modified since the last check and updates the last check timestamp
 * @param {Object} options
 * @param {string} options.authToken - Notion API token
 * @param {string} options.databaseId - Notion database ID
 * @param {string} options.checkKey - Identifier for this particular check
 * @param {Object} [options.additionalFilter] - Additional filters for the query
 * @returns {Promise<Array>} Array of modified pages
 */
async function getPagesSinceLastCheck(options) {
  const { authToken, databaseId, checkKey, additionalFilter } = options;

  // Get the timestamp of the last check
  const lastCheck = await getLastCheckTimestamp(checkKey);

  // Get modified pages
  const modifiedPages = await getModifiedNotionPages({
    authToken,
    databaseId,
    sinceTimestamp: lastCheck,
    additionalFilter
  });

  // Update the last check timestamp
  await storeLastCheckTimestamp(checkKey);

  return modifiedPages;
}

module.exports = {
  getModifiedNotionPages,
  storeLastCheckTimestamp,
  getLastCheckTimestamp,
  getPagesSinceLastCheck
};
