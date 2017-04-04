#!/usr/bin/env python3

from pyzotero import zotero
from sys import stderr as cerr

def zoteroDebug(apikey,libid, collid):
    zot = zotero.Zotero( libid, "user", apikey )
    items = zot.collection_items(collid)
    import pdb
    pdb.set_trace()




class ZoteroDispatch:

    def __init__(self, zconf, titlemap, pdf_settings, personal_only = False, debug = False):

        self.__userzot    = ZoteroEdit(  "user",  zconf, titlemap, pdf_settings, debug )

        if not personal_only:
            self.__grpzot = ZoteroSync( zconf['group'], "group", zconf['api_key'], titlemap, pdf_settings, debug )



class ZoteroEdit:

    def __init__(self, libraryType, zconfig, titlemap, pdf_settings, debug = False):

        collname         = zconfig[libraryType]['collection_name']
        self.__debug     = debug
        self.__tmap      = titlemap

        self.__zot       = zotero.Zotero( zconfig[libraryType]['lib_id'], libraryType, zconfig['api_key'])
        self.__collID   = self.findCollectionID( collname )
        
        self.__log       = open('zotero_edit.'+libraryType+'.'+collname+'.log','a')
        self.__log.write("\n\n\n======================\n")

        self.attach_pdf  = False
        self.url_set     = False
        self.url_clear   = False
        self.url_is_used = False

        if self.__debug:
            print("Debug mode in use", file=cerr)

        self.retrieveFilesFromServer();

    def logthis(self, *args):
        print(*args,file=cerr)
        print(*args,file=self.__log)



    def forItem_retrieveChildFiles(self, item):
        children = self.__zot.children(item['key'])

        if len(children) > 0:
            self.logthis("Retrieving child for %s:" % item['data']['title'])
        
        for child in children:
            if child['data']['linkMode'] == 'imported_file':
                filename = child['data']['filename']
                self.logthis("  - Saving", filename)
                self.__zot.dump(child['key'], filename, './')
                    
        return (1,1)
        
        
    def retrieveFilesFromServer(self):
   
        self.__iterateItemsInCollection(
            self.ItemRetrieveChildFiles, "Done: %d"
        )
        exit(0)
            
    
    def processItems(self, collectionID, work_mode ):
        """Attaches or sets URL"""

        format_string = "Processed %d items"

        if work_mode["attach_pdf"]:
            self.attach_pdf = True
            format_string += ", attached %d URL items "

        if work_mode["url_set"]:
            self.url_set = True
            format_string += ", set %d URL fields"

        if work_mode["url_clear"]:
            self.url_clear = True
            format_string += ", cleared %d URL fields"

        format_string += "           "


        if self.url_set and self.url_clear:
            print("Cannot use 'url_set' and 'url_clear' at the same time.",
                  "Please change in your config.", file=cerr)
            exit(-1)

        if self.url_set or self.url_clear:
            self.url_is_used = True

        self.__iterateItemsInCollection(
            self.__dummyProcess if self.__debug else self.__itemProcess,
            format_string
        )
      
  

    def ____itemAttachUrlChild(self, item, map_data):
        """Attaches an URL as a child item to the current item. Supports multiple attachments"""

        newlink  = map_data['link']
        children = self.__zot.children(item['key'])
        
        for child in children:
            try:
                if child['data']['title'] == "Google Drive":
                    if child['data']['url'] == newlink:
                        print("Link already exists, doing nothing.",
                              child, newlink, item, file=self.__log)
                        return 0

                    else:
                        # Google Drive link but the link doesn't match
                        # - 1. it's the same file and google has updated the link (unlikely!)
                        # - 2. or it's another PDF linking to the same item (e.g. supplemental data)
                        #if not self.overwrite_all_links:
                        #    # Removes all
                        #    # 
                        #    return 0
                        #else:
                        #    child['data']['url'] = newlink
                        #    self.__zot.update_item( child['data'] )
                        #    return 1

                        # We assume it's a new PDF that needs linking
                        print("GoogleDrive attachment exists,",
                          "attaching a new one under the assumption of supplemental data.",
                              child, newlink, item, file=self.__log)


            except KeyError:
                pass

        # Handled existing links, now the case for new ones
        #
        tree = {'itemType': 'attachment', 'linkMode': 'linked_url', 'title': "Google Drive",
                'accessDate': '', 'url': newlink, 'note': '', 'tags': [], 'relations': {},
                'contentType': '', 'charset': ''}

        res = self.__zot.create_items([tree], item['key']  )  # bind attachment to parentID
           
        if len(res['successful']) > 0:
            print("Successfully attached",
                  item, map_data['link'], file=self.__log)
            return 1

        print("Failed to attach",
              item, map_data['link'], file=self.__log)
        return 0
            

    

    def ____itemDirectUrlSet(self,item, map_data):
        """Sets a Google Drive link in the URL field of an item"""
        
        if len(item['data']['url'].strip()) < 10:
            print("Updating", item, map_data['link'], file=self.__log)

            item['data']['url'] = map_data['link']
            self.__zot.update_item(item['data'])

            return 1

        print("Url not changed, one already exists", item['data']['url'], file=self.__log)
        return 0


    
    
    def ____itemDirectUrlClear(self, item):
        """Clears a Google Drive link in the URL field of an item"""

        if  item['data']['url'].startswith("https://drive.google"):
            item['data']['url'] = ""

            self.__zot.update_item( item['data'] )

            print("Cleared Google Drive URL in",
                  item['key'], item['data']['title'], file=self.__log)
            return 1

        print("Left URL alone", item['key'], item['data']['title'], file=self.__log)
        return 0



    def __dummyProcess(self, item):
        """Pretends to work, but does nothing -- for debugging"""
        return (1,1)
    
       
    def __itemProcess(self, item):
        """Performs an action upon an item, one or many of:
              __itemDirectUrlClear
              __itemDirectUrlSet
              __itemAttachUrlChild
        """
        data = item['data']

        url_action = 0
        attached   = 0

        try:
            title   = data['title'].lower()
            #authors = data['creators'].lower()
            
            if title in self.titlemap:
                map_data = self.titlemap[title]

                if self.url_set:
                    url_action += self.__itemDirectUrlSet( item, map_data)  # These two are
                elif self.url_clear:                                        # mutually-
                    url_action += self.__itemDirectUrlClear( item )         # exclusive

                if self.attach_pdf:
                    attached += self.__itemAttachUrlChild( item, map_data )

            else:
                print("Could not map title", title, file=self.__log)

        except KeyError as e:
            print( "No title in ", data, file=self.__log)

        return (url_action, attached)


    
    
    def __iterateItemsInCollection(self, callback, progmessage):
        """Iterate through all items in the collection and perform callback upon each item"""
        # Can handle 100 at a time
        start_it = 0
        limit_vl = 100

        total_processed = 0
        total_attach    = 0
        total_url       = 0


        while True:
            items = self.__zot.collection_items_top(self.__collID, start=start_it, limit = limit_vl)
            start_it += limit_vl

            len_items = len(items)
            if len_items == 0:
                break

            for item in items:
                num_url, num_attach = callback(item)
                total_attach += num_attach
                total_url    += num_url
               
                self.__progress(progmessage, total_processed, total_attach, total_url)

            total_processed += len_items
            self.__progress(progmessage, total_processed, total_attach, total_url)

        # Fin
        self.__progress(progmessage, total_processed, total_attach, total_url)


        

    def __progress(self, format_message, total, attach, url):
        """Displays progress"""

        tup = None
        if self.attach_pdf:
            tup = (total, attach, url) if self.url_is_used else (total, attach)

        elif self.url_is_used:
            tup = (total, url)

        if tup != None:
            print(format_message % tup, end='\r', file=cerr)

    
  

    def findCollectionID(self, name = ""):
        """Finds the collectionID for a collection name"""
        res = {}
        for zz in self.__zot.collections():
            if name == "" or (name != "" and (zz['data']['name'] == name)):

                title = zz['data']['name']
                value = zz['key']

                if title not in res:
                    res[title] = []
                res[title].append( value )


        if len(res) == 1:
            if len(res[name]) == 1:
                return res[name][0]       

        print("Multiple collections found:\n%s" % res, file=cerr)
        exit(-1)



    # Debug
    def getAllItems(self):
        """Prints out all items"""
        self.__iterateItemsInCollection(
            self.printItem,
            "Processed %d of which %d are printed"
        )
    def printItem(self,item):
        print(item)
        return 1



### Example of attachment using zotero storage:
# {'key': 'PSZA7XPI', 'version': 14, 'library': {'type': 'user', 'id': 3808237, 'name': 'mtekman', 'links': {'alternate': {'href': 'https://www.zotero.org/mtekman', 'type': 'text/html'}}}, 'links': {'self': {'href': 'https://api.zotero.org/users/3808237/items/PSZA7XPI', 'type': 'application/json'}, 'alternate': {'href': 'https://www.zotero.org/mtekman/items/PSZA7XPI', 'type': 'text/html'}, 'up': {'href': 'https://api.zotero.org/users/3808237/items/JQZPDSGU', 'type': 'application/json'}, 'enclosure': {'type': 'application/pdf', 'href': 'https://api.zotero.org/users/3808237/items/PSZA7XPI/file/view', 'title': 'allegro.pdf', 'length': 90942}}, 'meta': {}, 'data': {'key': 'PSZA7XPI', 'version': 14, 'parentItem': 'JQZPDSGU', 'itemType': 'attachment', 'linkMode': 'imported_file', 'title': 'Gudbjartsson et al_2005_Allegro version 2.pdf', 'accessDate': '', 'url': '', 'note': '', 'contentType': 'application/pdf', 'charset': '', 'filename': 'Gudbjartsson et al_2005_Allegro version 2.pdf', 'md5': '11e622b16099f9a64a562e9e2a3d94af', 'mtime': 1470313393000, 'tags': [], 'relations': {}, 'dateAdded': '2016-08-04T12:23:13Z', 'dateModified': '2017-03-17T13:34:14Z'}}

### Example of same attachment using external storage:
# {'key': 'LARDKYJA', 'version': 2793, 'parentItem': '2FWFTHJN', 'itemType': 'attachment', 'linkMode': 'linked_file', 'title': '2011_Cliodynamics_Baker_demographic-str-theory-Rome.pdf', 'accessDate': '', 'url': '', 'note': '', 'contentType': 'application/pdf', 'charset': '', 'path': 'W:\\hstanesc\\info\\articles\\2011_Cliodynamics_Baker_demographic-str-theory-Rome.pdf', 'tags': [], 'relations': {}, 'dateAdded': '2017-03-03T10:01:13Z', 'dateModified': '2017-03-03T10:01:13Z'}

# Problem is that external storage does NOT have md5s to work with, and must use title
