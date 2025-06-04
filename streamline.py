#!/usr/bin/env python3
"""Minimal accessible RSS client with optional Fever API support."""

import argparse
import sys

import feedparser
import requests
import webbrowser

import readchar


def print_entry(entry, count=None, total=None):
    """Print a single feed entry."""
    if count is not None and total is not None:
        print(f"Entry {count}/{total}")
    title = entry.get('title') or 'No title'
    print(f"- {title}")
    link = entry.get('link')
    if link:
        print(f"  {link}")
    summary = entry.get('summary') or entry.get('content', '')
    if summary:
        text = summary
        if len(text) > 200:
            text = text[:200] + '...'
        print(f"  {text}")
    print()


def interactive_viewer(entries):
    """Interactively browse entries using hotkeys."""
    if not entries:
        print("No entries found.")
        return

    def help_message():
        print("Hotkeys: [n]ext [p]revious [o]pen link [q]uit [?] help")

    index = 0
    total = len(entries)
    help_message()
    while True:
        print_entry(entries[index], index + 1, total)
        key = readchar.readchar()
        if key == "n":
            index = (index + 1) % total
        elif key == "p":
            index = (index - 1) % total
        elif key == "o":
            link = entries[index].get("link")
            if link:
                webbrowser.open(link)
        elif key == "q":
            break
        elif key in ("?", "h"):
            help_message()


def print_entries(entries):
    """Print feed entries in a simple, accessible format."""
    for entry in entries:
        title = entry.get('title') or 'No title'
        print(f"- {title}")
        link = entry.get('link')
        if link:
            print(f"  {link}")
        summary = entry.get('summary') or entry.get('content', '')
        if summary:
            # print first 200 chars for brevity
            text = summary
            if len(text) > 200:
                text = text[:200] + '...'
            print(f"  {text}")
        print()


def read_local(feed_path: str, interactive: bool = False) -> None:
    """Read and display a local RSS/Atom feed."""
    feed = feedparser.parse(feed_path)
    title = feed.feed.get('title', 'Untitled feed')
    print(title)
    print('=' * len(title))
    if interactive:
        interactive_viewer(feed.entries)
    else:
        print_entries(feed.entries)


def read_fever(url: str, api_key: str, interactive: bool = False) -> None:
    """Fetch unread items from a Fever API endpoint."""
    response = requests.post(url, data={'api_key': api_key, 'items': ''})
    if not response.ok:
        sys.stderr.write('Failed to fetch items from Fever API.\n')
        return
    data = response.json()
    items = data.get('items', [])
    entries = [
        {
            'title': item.get('title'),
            'link': item.get('url'),
            'summary': item.get('html')
        }
        for item in items
    ]
    if interactive:
        interactive_viewer(entries)
    else:
        print_entries(entries)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description='Accessible RSS client')
    subparsers = parser.add_subparsers(dest='command')

    parser_local = subparsers.add_parser('local', help='Read a local feed file')
    parser_local.add_argument('file', help='Path to the feed XML file')
    parser_local.add_argument('-i', '--interactive', action='store_true',
                              help='Browse entries interactively')

    parser_fever = subparsers.add_parser('fever', help='Fetch items via Fever API')
    parser_fever.add_argument('--url', required=True, help='Fever API endpoint')
    parser_fever.add_argument('--api-key', required=True, help='Fever API key')
    parser_fever.add_argument('-i', '--interactive', action='store_true',
                              help='Browse entries interactively')

    args = parser.parse_args(argv)

    if args.command == 'local':
        read_local(args.file, args.interactive)
    elif args.command == 'fever':
        read_fever(args.url, args.api_key, args.interactive)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
