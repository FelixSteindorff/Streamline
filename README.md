# Streamline

Streamline is a minimal, accessible RSS reader written in Python. It can
parse local feed files or retrieve items from a Fever API compatible
server. The output is kept simple so that it works well with assistive
technologies such as screen readers.

## Requirements

```
pip install -r requirements.txt
```

## Usage

Read a local feed file:

```
python streamline.py local path/to/feed.xml
```

Interactive browsing:

```
python streamline.py local path/to/feed.xml --interactive
```

Fetch items from a Fever API endpoint:

```
python streamline.py fever --url https://example.com/fever --api-key YOUR_KEY
```

Add `--interactive` to use hotkeys for navigation when fetching from Fever.

The client prints the title, link and a short summary of each entry. In
interactive mode you can navigate with these hotkeys:

- **n**: next entry
- **p**: previous entry
- **o**: open the entry link in the default browser
- **q**: quit the viewer

## Graphical interface

For a tree view of your feeds, run the WxPython GUI:

```
python streamline_gui.py
```

Hotkeys inside the GUI:

- **Tab**: switch between feed tree and article text
- **Ctrl+I**: import feeds from an OPML or text file
- **Ctrl+E**: export your feed list
- **Ctrl+T**: fetch and display the full article text

The GUI stores subscribed feeds in `feeds.json`.
