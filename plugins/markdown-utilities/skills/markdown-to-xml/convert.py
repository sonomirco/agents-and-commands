#!/usr/bin/env python3

import sys
import os
import re
from pathlib import Path

def find_article_file(search_term, articles_path):
    """Find article file in the Articles folder"""
    articles = list(articles_path.glob("*.md"))

    # Try exact match first
    for article in articles:
        if article.name == search_term:
            return article

    # Try partial match
    matches = []
    for article in articles:
        if search_term.lower() in article.name.lower():
            matches.append(article)

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"Multiple matches found for '{search_term}':")
        for match in matches:
            print(f"  - {match.name}")
        print("Please be more specific.")
        sys.exit(1)
    else:
        print(f"No article found matching '{search_term}'")
        sys.exit(1)

def extract_article_section(content):
    """Extract content under ### Article header"""
    lines = content.split('\n')
    article_start = None
    article_end = None

    for i, line in enumerate(lines):
        if line.strip() == "### Article":
            article_start = i + 1
        elif article_start is not None and line.startswith("###"):
            article_end = i
            break

    if article_start is None:
        print("No '### Article' section found in the file")
        sys.exit(1)

    if article_end is None:
        article_content = lines[article_start:]
    else:
        article_content = lines[article_start:article_end]

    return '\n'.join(article_content).strip()

def convert_markdown_to_xml(text):
    """Convert markdown formatting to XML"""

    # Store code blocks temporarily to avoid processing them
    code_blocks = []
    def save_code_block(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"

    # Save code blocks
    text = re.sub(r'```[\s\S]*?```', save_code_block, text)
    text = re.sub(r'`[^`]+`', save_code_block, text)

    # Split into paragraphs
    paragraphs = text.split('\n\n')
    converted_paragraphs = []

    for para in paragraphs:
        if not para.strip():
            continue

        # Check if it's a header (h1-h6 based on number of #)
        if para.startswith('#'):
            # Match headers with 1-6 hashtags
            header_match = re.match(r'^(#{1,6})\s+(.+)$', para)
            if header_match:
                level = len(header_match.group(1))  # Count the hashtags
                content = header_match.group(2)
                content = convert_inline_formatting(content)
                converted_paragraphs.append(f"<h{level}>{content}</h{level}>")
                continue

        # Check if it's a blockquote
        if para.startswith('>'):
            quote_lines = []
            for line in para.split('\n'):
                if line.startswith('>'):
                    quote_lines.append(line[1:].strip())
            quote_content = ' '.join(quote_lines)
            quote_content = convert_inline_formatting(quote_content)
            converted_paragraphs.append(f"<blockquote>{quote_content}</blockquote>")
            continue

        # Check if it's a list
        if re.match(r'^[-*]\s', para):
            list_items = []
            for line in para.split('\n'):
                if re.match(r'^[-*]\s', line):
                    item_content = re.sub(r'^[-*]\s+', '', line)
                    item_content = convert_inline_formatting(item_content)
                    list_items.append(f"  <li>{item_content}</li>")
            converted_paragraphs.append(f"<ul>\n{''.join(list_items)}\n</ul>")
            continue

        # Regular paragraph - no <p> tags, just the content
        para = convert_inline_formatting(para)
        converted_paragraphs.append(para)

    result = '\n\n'.join(converted_paragraphs)

    # Restore code blocks
    for i, code in enumerate(code_blocks):
        result = result.replace(f"__CODE_BLOCK_{i}__", f"<code>{code.strip('`')}</code>")

    return result

def convert_inline_formatting(text):
    """Convert inline markdown formatting to XML"""

    # Convert bold (handle both ** and __ formats)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)

    # Convert italic (handle both * and _ formats, but avoid matching bold)
    text = re.sub(r'(?<!\*)\*(?!\*)([^*]+)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!_)_(?!_)([^_]+)(?<!_)_(?!_)', r'<em>\1</em>', text)

    # Convert links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

    # Convert line breaks
    text = text.replace('\n', ' ')

    return text

def main():
    if len(sys.argv) < 2:
        print("Usage: claude markdown-to-xml [filename]")
        print("Example: claude markdown-to-xml '17. ProductInterview'")
        sys.exit(1)

    search_term = sys.argv[1]

    # Find the Obsidian vault path (assuming it's in the user's home directory)
    vault_paths = [
        Path.home() / "Documents" / "Obsidian",
        Path.home() / "Obsidian",
        Path.home() / "Documents" / "Vault",
        Path.home() / "Vault"
    ]

    articles_path = None
    for vault_path in vault_paths:
        potential_articles = vault_path / "Articles"
        if potential_articles.exists():
            articles_path = potential_articles
            break

    if articles_path is None:
        # Try to find any Articles folder
        for root, dirs, files in os.walk(Path.home()):
            if "Articles" in dirs:
                potential_path = Path(root) / "Articles"
                # Check if it has .md files
                if list(potential_path.glob("*.md")):
                    articles_path = potential_path
                    break

    if articles_path is None:
        print("Could not find Articles folder in your Obsidian vault")
        sys.exit(1)

    print(f"Found Articles folder at: {articles_path}")

    # Find the article file
    article_file = find_article_file(search_term, articles_path)
    print(f"Processing: {article_file.name}")

    # Read the file
    with open(article_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract article section
    article_content = extract_article_section(content)

    # Convert to XML
    xml_content = convert_markdown_to_xml(article_content)

    # Save to Desktop
    desktop_path = Path.home() / "Desktop"
    output_file = desktop_path / "article_converted.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print(f"✓ Article converted and saved to: {output_file}")

if __name__ == "__main__":
    main()