# Read Later

A sophisticated AI-powered system for collecting, organizing, and managing articles for later reading. This project automates the process of gathering articles from various sources, processing them with AI, and generating valuable content from your reading notes.

## Overview

Read Later is designed to simplify your learning and content creation workflow. It uses email as a central collection point, leveraging the Gmail/Google ecosystem for initial data collection, and combines AI/ML techniques to provide intelligent content curation and knowledge synthesis.

## Process Diagram

A visual representation of the Read Later workflow:

![Read Later Process Flow](process.png)

## Features

### Content Collection & Processing
- **Email-based Collection**: Easy article submission through email
- **Google Sheets Integration**: Initial data collection and staging
- **Local Database Storage**: Secure storage using DuckDB
- **Tag-based Organization**: AI-enhanced categorization system
- **Cross-platform Accessibility**: Access your reading list from any device

### AI/ML Capabilities
- **Intelligent Content Curation**: AI agents analyze and tag articles
- **Smart Summarization**: Automatic generation of article summaries
- **Related Content Discovery**: ML-based recommendation of related articles
- **Knowledge Synthesis**: AI-powered generation of reading notes
- **Content Generation**: Automated creation of various content types

### Content Generation
- **Lesson Plans**: Structured learning materials
- **Blog Posts**: Engaging content for your blog
- **Video Scripts**: Ready-to-use video content
- **Reading Guides**: Curated learning paths
- **News Summaries**: Concise overviews of topics
- **Social Posts**: Shareable content snippets
- **Research Topics**: AI-identified research areas
- **Trend Monitoring**: Automated trend analysis
- **Newsletters**: Curated content for your audience

## Process Flow

1. **Collection & Initial Storage**
   - Articles are collected through email submissions
   - Sources include:
     - Manual submissions via email
     - Automated newsletters (TLDR, MarTech)
     - Daily topic-based collections
   - Data is initially stored in Google Sheets
   - Python scripts monitor Google Sheets for updates
   - New entries are transferred to local DuckDB database

2. **Processing & Analysis**
   - System extracts unique URLs from incoming emails
   - Processes article metadata including:
     - Title
     - Source
     - Tags
   - AI agents analyze and enhance article metadata
   - ML models identify related content
   - Articles are summarized and tagged

3. **Knowledge Management**
   - Articles are processed using Zettelkasten methodology
   - Reading notes are automatically generated in Markdown
   - Notes are integrated with Obsidian for knowledge management
   - AI agents generate permanent notes and connections

4. **Content Generation**
   - Local AI (Ollama) processes reading notes
   - MSTY (or similar) generates various content types
   - Content is automatically formatted and organized
   - Regular updates and refinements through AI feedback

## Technical Details

The system is built using:
- Google Apps Script for email automation
- Google Sheets for initial data collection
- Python scripts for data synchronization
- DuckDB for local data storage
- Apache Airflow for task scheduling
- AI/ML frameworks for content processing
- Ollama for local AI processing
- Obsidian for knowledge management
- Markdown for note formatting

### Data Loading Process

The system uses a Python script (`load_data.py`) to synchronize data from Google Sheets to a local DuckDB database:

1. **Google Sheets Connection**
   - Uses Google Sheets API with OAuth 2.0 authentication
   - Reads data from the specified spreadsheet
   - Handles authentication via `credentials.json`

2. **Data Processing**
   - Extracts article data including:
     - Title
     - URL (used as unique identifier)
     - Tags
     - Sender Name
   - Adds timestamp for tracking updates

3. **Database Integration**
   - Uses DuckDB for local storage
   - Implements upsert functionality to:
     - Insert new records
     - Track last update time
   - Maintains data integrity with URL as primary key

4. **Synchronization**
   - Automatically detects new and modified records
   - Provides statistics about sync operations
   - Handles connection management and error cases

### Email Processing Logic

The system uses a sophisticated email processing workflow:

1. **Label-based Organization**
   - Uses Gmail labels `__News/unprocessed` and `__News/processed` to track article status
   - Automatically moves processed emails to the processed label

2. **URL Extraction and Deduplication**
   - Extracts URLs from HTML email content using regex pattern matching
   - Maintains a list of existing URLs to prevent duplicates
   - Cleans URLs by:
     - Removing tracking parameters
     - Decoding URI-encoded URLs
     - Handling tracking wrapper URLs (e.g., TLDR newsletter format)
     - Ensuring proper URL protocol (http/https)

3. **Metadata Processing**
   - Extracts article titles from email content
   - Processes sender information from email headers
   - Parses hashtags from email subjects (e.g., #tag1, #tag2)
   - Stores initial metadata in Google Sheets

4. **Data Storage**
   - Initial storage in Google Sheets with columns for:
     - Title
     - URL
     - Tags
     - Sender Name
   - Python scripts (`update.py`) monitor for changes
   - Data is synchronized to DuckDB with additional columns for:
     - AI-generated metadata
     - Reading notes
     - Generated content

### Automation Features

- Automated processing of labeled emails
- Google Sheets to DuckDB synchronization
- Intelligent URL cleaning and validation
- Smart title extraction from email content
- Tag-based categorization system
- Duplicate prevention mechanism
- Scheduled content updates via Airflow
- AI-powered content generation
- Automated knowledge synthesis

## Getting Started

[To be added: Setup instructions, configuration details, and usage guidelines]

## Contributing

[To be added: Contribution guidelines and process]

## License

[To be added: License information]
