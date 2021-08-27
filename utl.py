

from bs4 import BeautifulSoup 
import requests
from links import Links
import urllib.request
import os
from tqdm import tqdm
# site url


class URL:
    def __init__(self,url):
        self.url = url
    def getUrl(self):
        return self.url
class Media:
    def __init__(self,url,name):
        self.localName = ''
        self.dir = name
        self.url = URL(url)
    def getURL(self):
        return self.url.getUrl()
    def getDirectory(self):
        return self.dir
    def setLocalFileName(self,name):
        self.localName = name
    def download(self,filepath:str):
        mediaFile = open(filepath,'wb')
        mediaFile.write(urllib.request.urlopen(self.getURL()).read())
        mediaFile.close()
class Page:
    def __init__(self, url:URL):
        self.url = url
        data = self.getHTMLData(url.getUrl())
        self.soup = BeautifulSoup(data,'html.parser')
        self.dict={}
    def getHTMLData(self,url:str): 
        r = requests.get(url) #opens link
        return r.text #return html for link's webpage
    def download(self,fileName):   
        file = open(fileName,"w") #open file to write  code to
        file.write(self.soup.prettify()) #write code to file
        file.close() #save file
    def getData(self):
        return self.soup
    
    def genName(self,fname):
        if self.url.getUrl() in self.dict: #if name for local html for link has been generated
            return self.dict[self.url.getUrl()]
        # name = getName(self.url.getUrl()) #generate name
        self.dict[self.url.getUrl()] =fname #add to global dictionary
        return fname
    def removeOnlineReferences(self,tag):
        attrs_to_delete =[]
        for attr in tag.attrs:
            if 'http' in tag[attr]:
                attrs_to_delete.append(attr)
        for attr in attrs_to_delete:
            del tag[attr]
    def getDict(self):
        return self.dict
    def getUrl(self):
        return self.url.getUrl()
    def getLocation(self,link_address:str):
        return link_address.split('?')[0]
    def generateFilename(self,url:str):
        return url.split('/')[-1]
    def localiseMedia(self):
        for tag in self.soup.find_all('img'):
            if tag.get('src'):
                media = Media(tag['src'], tag.name)
                if not os.path.isdir(str(media.getDirectory())):
                    os.makedirs(media.getDirectory())
                filename = self.generateFilename(self.getLocation(media.getURL()))
                filepath = media.getDirectory() +'/' +filename
                #print(tag['src'])
                # downloadMedia(filepath,media)
                media.download(filepath)
                tag['src'] = filepath
            self.removeOnlineReferences(tag)
    

class Website:
    def __init__(self,url:str):
        self.site_url = URL(url)
    def getName(self,link):
        length = len(self.site_url.getUrl())
        link_url = link[length:]
        link_url = link_url.split('/')
        if link_url[0]=='':
            link_url[0]="home"
        file_name = "_".join(link_url)+'.html'
        return file_name
    def localiseLinks(self,tagsForLinks,page:Page): #function to make links refer to local '.html' files
        for tag in tagsForLinks: #all tags in current webpage
            newPage = Page(URL(tag['href']))
            # print(newPage.getUrl())
            if newPage.getUrl() in page.getDict(): #if url has name generated already
                tag['href'] =page.getDict()[newPage.getUrl()] #then localise it
            else:
                page.dict[newPage.getUrl()] = newPage.genName(self.getName(newPage.getUrl())) #generate local file name
                tag['href'] = page.getDict()[newPage.getUrl()]#localise
    def isSiteLink(self,url:str):
        if len(url)>20:
            if self.site_url.getUrl() in str(url): #check if url is wordpress bundled site
                return True
        return False
    def traverse(self,url:URL,links_object):
        if not links_object.checkExists(url.getUrl()) : #checks if url in the set of encountered links
            links_object.addLink(url.getUrl()) #adds link url to encountered urls
            # pageData = getData(url.getUrl())
            # soup_object = generateSoup(pageData) #create BeautifulSoup object
            page = Page(url)
            listOfUrls = [] #list of all links in page
            listoftags =[]
            # name = genName(url.getUrl())
            
            for tag in tqdm(page.getData().find_all('a')):
                if tag.get('href'):
                    if tag.get('href')[0:4]=="http" and self.isSiteLink(tag.get('href')): #if http link and is user website link not wordpress bundled link
                        listOfUrls.append(URL(tag.get('href')))
                        listoftags.append(tag)
            for link in listOfUrls: #access all links found in page while depth is less that depth    
                self.traverse(link,links_object)#recursively download webpage for that file
                    #link = filename
            self.localiseLinks(listoftags,page)
            page.localiseMedia()
            fname = self.getName(page.getUrl())
            page.download(page.genName(fname))


the_links = Links()
site = Website("https://skyline3567870.wordpress.com/")
site.traverse(site.site_url,the_links)

