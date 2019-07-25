#!/bin/bash

# reset Zotero Connector
# Remove from Chrome manually
rm -rf /Users/Nafty/Library/Application Support/Google/Chrome/Profile 2/Extensions/ekhagklcjbdpajgpjgmbionohlpdbjgc
rm -rf /Users/Nafty/Library/Application Support/Google/Chrome/Profile 2/Local Extension Settings/ekhagklcjbdpajgpjgmbionohlpdbjgc
# re-Add to Chrome: https://chrome.google.com/webstore/detail/ekhagklcjbdpajgpjgmbionohlpdbjgc


# reset ZoteroGoogleDrive-PDFLinker-Cloud caches
rm -rf /Users/Nafty/Library/Caches/GoogleZoteroPDFLinker
rm /Users/Nafty/Downloads/ZoteroGoogleDrive-PDFLinker-Cloud/hashfile


# reset Zotero 5.0
rm -rf ~/Zotero
rm -rf ~/Library/Caches/Zotero
rm -rf /Users/Nafty/Library/Application Support/Zotero
rm -rf /Users/Nafty/Library/Group Containers/UBF8T346G9.Office/User
rm -rf Content.localized/Startup.localized/Word/Zotero.dotm
rm -rf /Users/Nafty/Library/Preferences/org.zotero.zotero.plist
rm -rf /Users/Nafty/Library/Saved Application State/org.zotero.zotero.savedState


# reset Zotero-hhs Google Drive folder
# manually delete everything
