
from ast import Str
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
        self.soup = BeautifulSoup(getData(url.getUrl()),'html.parser')
    def getData(url:str): 
        r = requests.get(url) #opens link
        return r.text #return html for link's webpage
    def download(self,fileName):   
        file = open(fileName,"w") #open file to write  code to
        file.write(self.soup.prettify()) #write code to file
        file.close() #save file
    def getData(self):
        return self.soup
    
    

site_url = URL("https://skyline3567870.wordpress.com/")
dict={} #dictionary for all links and respective local file names
def getLocation(link_address:str):
    return link_address.split('?')[0]
def generateFilename(url:str):
    return url.split('/')[-1]
def getData(url:str): 
    r = requests.get(url) #opens link
    return r.text #return html for link's webpage

def localiseLinks(tagsForLinks): #function to make links refer to local '.html' files
    for tag in tagsForLinks: #all tags in current webpage
        if tag['href'] in dict: #if url has name generated already
            tag['href'] = dict[tag['href']] #then localise it
        else:
            dict[tag['href']] = genName(tag['href']) #generate local file name
            tag['href'] = dict[tag['href']]#localise 
def removeOnlineReferences(tag):
    attrs_to_delete =[]
    for attr in tag.attrs:
        if 'http' in tag[attr]:
            attrs_to_delete.append(attr)
    for attr in attrs_to_delete:
        del tag[attr]
def localiseMedia(soup):
    for tag in soup.find_all('img'):
        if tag.get('src'):
            media = Media(tag['src'], tag.name)
            if not os.path.isdir(str(media.getDirectory())):
                os.makedirs(media.getDirectory())
            filename = generateFilename(getLocation(media.getURL()))
            filepath = media.getDirectory() +'/' +filename
            #print(tag['src'])
            # downloadMedia(filepath,media)
            media.download(filepath)
            tag['src'] = filepath
        removeOnlineReferences(tag)

def download(data,fileName):   
    file = open(fileName,"w") #open file to write  code to
    file.write(data.prettify()) #write code to file
    file.close() #save file

def generateSoup(pageData):
    return BeautifulSoup(pageData,'html.parser') #returns beautiful soup instance

def isSiteLink(url:str):
    if len(url)>20:
        if site_url.getUrl() in str(url): #check if url is wordpress bundled site
            return True
    return False

def traverse(url:URL,links_object):
    if not links_object.checkExists(url.getUrl()) : #checks if url in the set of encountered links
        links_object.addLink(url.getUrl()) #adds link url to encountered urls
        # pageData = getData(url.getUrl())
        # soup_object = generateSoup(pageData) #create BeautifulSoup object
        page = Page(url)
        listOfUrls = [] #list of all links in page
        listoftags =[]
        name = genName(url.getUrl())
        for tag in tqdm(page.getData().find_all('a')):
            if tag.get('href'):
                if tag.get('href')[0:4]=="http" and isSiteLink(tag.get('href')): #if http link and is user website link not wordpress bundled link
                    listOfUrls.append(URL(tag.get('href')))
                    listoftags.append(tag)
        for link in listOfUrls: #access all links found in page while depth is less that depth    
            traverse(link,links_object)#recursively download webpage for that file
                #link = filename
        localiseLinks(listoftags)
        localiseMedia(page.getData())
        page.download(name)
        # download(page.getData(),name)

def genName(url):
    if url in dict: #if name for local html for link has been generated
        return dict[url]
    name = getName(url) #generate name
    dict[url] =name #add to global dictionary
    return name
# This function returns the rightful name that we going to use to name the file that contains
# all the content from the downloaded link
# it takes a single link address and returns the appropriate name
def getName(link):
    length = len(site_url.getUrl())
    link_url = link[length:]
    link_url = link_url.split('/')
    if link_url[0]=='':
        link_url[0]="home"
    file_name = "_".join(link_url)+'.html'
    return file_name

the_links = Links()

traverse(site_url,the_links)

# def main():
#     the_links = Links()
#     site_url = "https://skyline3567870.wordpress.com/"
#     traverse(site_url,the_links)


# if __name__ == "__main__":
#     main()
