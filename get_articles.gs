/**
 * Read Later - Email Article Processing Script
 * 
 * This Google Apps Script automates the process of collecting and organizing articles
 * from emails into a Google Sheet. It processes emails labeled with "__News/unprocessed",
 * extracts article URLs and metadata, and stores them in a structured format.
 * 
 * Usage:
 * 1. Set up Gmail labels:
 *    - Create a label "__News/unprocessed" for incoming articles
 *    - The script will automatically create "__News/processed" for processed emails
 * 
 * 2. Configure Google Sheet:
 *    - Create a new Google Sheet
 *    - Add this script to the sheet's Apps Script editor
 *    - The sheet should have columns for: Title, URL, Tags, Sender Name
 * 
 * 3. Processing:
 *    - Label incoming article emails with "__News/unprocessed"
 *    - Run the processNewsEmails() function manually or set up a time-based trigger
 *    - Processed emails will be moved to "__News/processed"
 * 
 * Features:
 * - Extracts URLs from HTML email content
 * - Cleans URLs by removing tracking parameters and decoding
 * - Handles special cases like TLDR newsletter tracking URLs
 * - Extracts article titles from email content
 * - Processes sender information from email headers
 * - Parses hashtags from email subjects
 * - Prevents duplicate articles
 * 
 * Dependencies:
 * - Google Apps Script
 * - Gmail API
 * - Google Sheets API
 */

function processNewsEmails() {
  // --- CONFIGURATION ---
  var UNPROCESSED_LABEL = "__News/unprocessed";
  var PROCESSED_LABEL = "__News/processed";
  
  // Use the active spreadsheet and active sheet.
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var existingUrls = getExistingUrls(sheet);
  
  // Get Gmail label for unprocessed emails.
  var unprocessedLabel = GmailApp.getUserLabelByName(UNPROCESSED_LABEL);
  if (!unprocessedLabel) {
    Logger.log("Label " + UNPROCESSED_LABEL + " not found.");
    return;
  }
  
  // Search threads with the unprocessed label.
  var threads = unprocessedLabel.getThreads();
  Logger.log("Found " + threads.length + " threads to process.");

  // Process each thread.
  threads.forEach(function(thread) {
    var messages = thread.getMessages();
    messages.forEach(function(message) {
      // Extract sender name from the "From" field.
      var senderName = extractSenderName(message.getFrom());
      // Get the email subject and extract tags.
      var subject = message.getSubject();
      var tags = extractTags(subject);
      
      // Get the HTML body of the message.
      var htmlBody = message.getBody();
      // Extract link data (URL and title) from the email.
      var links = extractLinks(htmlBody);
      links.forEach(function(linkData) {
        var cleanedUrl = cleanUrl(linkData.url);
        // Check if this URL is already in the sheet.
        if (existingUrls.indexOf(cleanedUrl) === -1) {
          // Append the new row to the sheet: Title, URL, Tags, Sender Name.
          sheet.appendRow([linkData.title, cleanedUrl, tags, senderName]);
          existingUrls.push(cleanedUrl); // Update local cache.
        }
      });
    });
    
    // Update the labels for the thread: remove unprocessed and add processed.
    thread.removeLabel(unprocessedLabel);
    var processedLabel = GmailApp.getUserLabelByName(PROCESSED_LABEL) || GmailApp.createLabel(PROCESSED_LABEL);
    thread.addLabel(processedLabel);
  });
}

/**
 * Reads the existing URLs from the sheet (assumes URL Source is in column 2).
 */
function getExistingUrls(sheet) {
  var urls = [];
  // Get all data rows; assume first row is header.
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][1]) {
      urls.push(data[i][1].toString().trim());
    }
  }
  return urls;
}

/**
 * Extracts links and link titles from an HTML string.
 * Uses a regex to capture the href attribute and inner HTML.
 */
function extractLinks(html) {
  var links = [];
  // Regular expression to find anchor tags with href and inner content.
  var anchorRegex = /<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/gi;
  var match;
  
  while ((match = anchorRegex.exec(html)) !== null) {
    var rawUrl = match[1];
    var innerHtml = match[2];
    
    // Try to extract the title from a <strong> tag if it exists.
    var titleMatch = /<strong[^>]*>(.*?)<\/strong>/i.exec(innerHtml);
    var title = titleMatch ? titleMatch[1].trim() : innerHtml.replace(/<[^>]+>/g, '').trim();
    
    links.push({
      url: rawUrl,
      title: title
    });
  }
  
  return links;
}

/**
 * Extracts tags from an email subject.
 * It finds words that start with a '#' and stops at the next space or comma.
 * Returns a comma-separated string of tags, e.g. "#tag1, #tag2, #tag3".
 */
function extractTags(subject) {
  if (!subject) return "";
  var tags = [];
  // Match a '#' followed by any characters that are not space or comma.
  var tagRegex = /#([^ ,]+)/g;
  var match;
  while ((match = tagRegex.exec(subject)) !== null) {
    // Prepend '#' to maintain consistency.
    tags.push("#" + match[1].trim());
  }
  return tags.join(", ");
}

/**
 * Extracts the sender name from a "From" string.
 * For example, for "John Doe <john.doe@example.com>", returns "John Doe".
 * If no name is found, returns the entire string.
 */
function extractSenderName(fromString) {
  // Check if the sender is in the "Name <email>" format.
  var nameMatch = fromString.match(/^(.*?)\s*<.*?>$/);
  if (nameMatch && nameMatch[1]) {
    return nameMatch[1].trim();
  }
  return fromString.trim();
}

/**
 * Cleans a URL:
 * - Decodes URI encoding if needed.
 * - If it contains a tracking wrapper, extracts the embedded URL.
 * - Removes any query parameters or tracking parameters at the end.
 * - Ensures the URL starts with "http://" or "https://".
 *
 * This example assumes tracking URLs are in the form:
 * "https://tracking.tldrnewsletter.com/CL0/{encodedURL}/..."
 */
function cleanUrl(url) {
  var cleanedUrl = url;
  
  // Check if URL contains a tracking wrapper.
  var trackingPattern = /tracking\.tldrnewsletter\.com\/CL0\/([^\/]+)/;
  var match = url.match(trackingPattern);
  if (match && match[1]) {
    // Decode the embedded URL.
    cleanedUrl = decodeURIComponent(match[1]);
  } else {
    // If the URL appears to be URI encoded, try decoding it.
    try {
      var decoded = decodeURIComponent(url);
      if (decoded !== url) {
        cleanedUrl = decoded;
      }
    } catch (e) {
      Logger.log("Decoding error for URL: " + url);
    }
  }
  
  // Remove query parameters (anything after '?' including the '?')
  if (cleanedUrl.indexOf('?') !== -1) {
    cleanedUrl = cleanedUrl.split('?')[0];
  }
  
  // Ensure the URL starts with "http://" or "https://"
  if (!/^https?:\/\//i.test(cleanedUrl)) {
    cleanedUrl = "http://" + cleanedUrl;
  }
  
  return cleanedUrl;
}
