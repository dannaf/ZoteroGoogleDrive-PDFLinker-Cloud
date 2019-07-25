#!/bin/bash


############
## REMOVE ##
############

# reset Zotero Connector
echo "Manually 'Remove from Chrome'"
rm -rf /Users/Nafty/Library/Application Support/Google/Chrome/Profile 2/Extensions/ekhagklcjbdpajgpjgmbionohlpdbjgc
rm -rf /Users/Nafty/Library/Application Support/Google/Chrome/Profile 2/Local Extension Settings/ekhagklcjbdpajgpjgmbionohlpdbjgc
echo "Manually re-'Add to Chrome' Zotero Connector at https://chrome.google.com/webstore/detail/ekhagklcjbdpajgpjgmbionohlpdbjgc"


# reset ZoteroGoogleDrive-PDFLinker-Cloud caches
rm -rf /Users/Nafty/Library/Caches/GoogleZoteroPDFLinker
rm /Users/Nafty/Downloads/ZoteroGoogleDrive-PDFLinker-Cloud/hashfile


# reset Zotero 5.0
rm -rf /Applications/Zotero.app
rm -rf ~/Zotero
rm -rf ~/Library/Caches/Zotero
rm -rf /Users/Nafty/Library/Application Support/Zotero
rm -rf /Users/Nafty/Library/Group Containers/UBF8T346G9.Office/User
rm -rf Content.localized/Startup.localized/Word/Zotero.dotm
rm -rf /Users/Nafty/Library/Preferences/org.zotero.zotero.plist
rm -rf /Users/Nafty/Library/Saved Application State/org.zotero.zotero.savedState


# reset Zotero-hhs Google Drive folder
echo 'Manually delete gdrive Zotero-hhs folder'  # manually delete everything  # TODO: can automate this with pydrive


################
## RE-INSTALL ##
################


