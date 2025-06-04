#!/usr/bin/env python3
"""Accessible GUI RSS reader using wxPython."""

import json
import os
import re
import feedparser
import requests
import wx

try:
    from readability import Document
    import lxml.html
except Exception:
    Document = None

FEED_FILE = 'feeds.json'


def load_feeds():
    if os.path.exists(FEED_FILE):
        with open(FEED_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_feeds(feeds):
    with open(FEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(feeds, f, indent=2)


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Streamline RSS")
        self.feeds = load_feeds()
        self.build_ui()
        self.Bind(wx.EVT_CHAR_HOOK, self.on_hotkey)

    def build_ui(self):
        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.tree = wx.TreeCtrl(panel)
        self.text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        hbox.Add(self.tree, 1, wx.EXPAND)
        hbox.Add(self.text, 2, wx.EXPAND)
        panel.SetSizer(hbox)
        self.populate_tree()
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activate)

    def populate_tree(self):
        self.tree.DeleteAllItems()
        root = self.tree.AddRoot("Feeds")
        for url in self.feeds:
            fitem = self.tree.AppendItem(root, url)
            feed = feedparser.parse(url)
            for entry in feed.entries:
                child = self.tree.AppendItem(fitem, entry.get('title', 'No title'))
                self.tree.SetItemData(child, entry)
        self.tree.Expand(root)

    def on_activate(self, event):
        item = event.GetItem()
        data = self.tree.GetItemData(item)
        if isinstance(data, dict):
            summary = data.get('summary') or data.get('content', '')
            self.text.SetValue(summary or 'No content available.')
            self.text.SetFocus()

    def on_hotkey(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_TAB:
            if self.tree.HasFocus():
                self.text.SetFocus()
            else:
                self.tree.SetFocus()
        elif code == ord('I') and event.ControlDown():
            self.import_feeds()
        elif code == ord('E') and event.ControlDown():
            self.export_feeds()
        elif code == ord('T') and event.ControlDown():
            self.load_full_text()
        else:
            event.Skip()

    def import_feeds(self):
        with wx.FileDialog(self, "Import feeds", wildcard="OPML or text files (*.opml;*.txt)|*.opml;*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            path = dlg.GetPath()
            feeds = []
            if path.endswith('.opml'):
                content = open(path, encoding='utf-8').read()
                feeds.extend(re.findall(r'xmlUrl="([^"]+)"', content))
            else:
                with open(path, encoding='utf-8') as f:
                    for line in f:
                        url = line.strip()
                        if url:
                            feeds.append(url)
            for url in feeds:
                if url not in self.feeds:
                    self.feeds.append(url)
            save_feeds(self.feeds)
            self.populate_tree()

    def export_feeds(self):
        with wx.FileDialog(self, "Export feeds", wildcard="Text files (*.txt)|*.txt",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            path = dlg.GetPath()
            with open(path, 'w', encoding='utf-8') as f:
                for url in self.feeds:
                    f.write(url + '\n')

    def load_full_text(self):
        item = self.tree.GetSelection()
        data = self.tree.GetItemData(item)
        if not isinstance(data, dict):
            return
        link = data.get('link')
        if not link:
            return
        try:
            resp = requests.get(link, timeout=10)
            text = resp.text
            if Document:
                doc = Document(text)
                html = doc.summary()
                root = lxml.html.fromstring(html)
                text = root.text_content()
            self.text.SetValue(text)
        except Exception as exc:
            self.text.SetValue(f"Failed to load article: {exc}")


class App(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True


if __name__ == '__main__':
    app = App()
    app.MainLoop()
