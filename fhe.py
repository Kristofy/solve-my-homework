import requests
import os
import urllib.request
import textract
import pprint
from bs4 import BeautifulSoup

pp = pprint.PrettyPrinter()

class Tuple:
    def __init__(self, id, data, name):
        self.id = id
        self.data = data
        self.name = name

def getlinks(is_logging=True):
    if(is_logging):
        print("\npulling links")
    URLBASE = "https://www.tortenelemtanarok.hu/"
    URL = "https://www.tortenelemtanarok.hu/erettsegi-feladatok/kozepszintu-erettsegi-feladatsorok-es-megoldasok"
    rawdata = requests.get(URL)
    page = BeautifulSoup(rawdata.content, 'html.parser')
    main = page.find('table', {'class':'color_table'})

    rows = main.find_all('tr')

    res = list()

    for i, row in enumerate(rows):
        data = row.find_all('a')
        for d in data:
            if("feladatlap" in d.text):
                href = d['href']
                print(URLBASE + href)
                res.append(Tuple(i, URLBASE + href, d.text))
    if(is_logging):
        print('done geting links')
        print(str(len(res)) + " links found\n")
    return res

def construct_loaded_set(is_logging=True):
    loaded = set()
    if(is_logging):
        print("\nloading already downloaded file names")
    for filename in os.listdir(os.getcwd()+"/resources"):
        if(not filename.endswith('.pdf')):
            continue
        realname = filename[filename.find('-')+1:]
        if(is_logging):
            print(realname)
        loaded.add(realname)
    if(is_logging):
        print("loading completed\n")
    return loaded


def download(data, is_logging=True):
    if(is_logging):
        print("\ndownloading")
    is_up_to_date = True
    loaded_files = construct_loaded_set()

    links = list(map(lambda x: x.data, data))
    ids = list(map(lambda x: x.id, data))

    for i, (link, uid) in enumerate(zip(links, ids)):
        name = link.split('/')[-1]
        if(name in loaded_files):
            if(is_logging):
                print(str(i+1)+". " + name + " already loaded")
        else:
            is_up_to_date = False
            urllib.request.urlretrieve(link, 'resources/'+str(uid)+"-"+name)
            if (is_logging):
                print(str(i+1)+". done " + str(len(links)-i-1) + " to go ->  " + name + " has been downloaded into the resources folder")
    if (is_up_to_date):
        print("you are up to date")
    if(is_logging):
        print("done downloading\n")
    return is_up_to_date


def convert_to_text(file_path):
    # get data utf-8 encoded
    text = textract.process(file_path, "UTF-8")
    # decode utf-8 in order to get special caracters
    text = text.decode("UTF-8")
    # remove empty lines
    text = "".join([s for s in text.strip().splitlines(True) if s.strip()])
    return text

def find(text, metadata = None, is_logging = True):
    if(is_logging):
        print("\nstart searching...")
    for filename in os.listdir(os.getcwd()+"/resources"):
        if(not filename.endswith(".txt")):
            continue
        data = ""
        with open("resources/"+filename,'r') as in_file:
            data = in_file.read()

        res = data.find(text)
        if(res != -1):
            print("\n"+"#"*20)
            print("találat: a "+filename+" fileban")
            if(metadata):
                uid = filename.split('-')[0]
                exdata = next((d for d in metadata if d.id == int(uid)), "undefined filename")
                print(exdata.name)
                print(exdata.data)
                i = res
                while(i>=0):
                    if(
                        data[i] == '\n' and data[i+1].isnumeric()):
                        if(data[i+2]=='.' or (data[i+2].isnumeric() and data[i+3]=='.')):
                            print(data[i+1:data.find('.',i+1)] + '. feladat')
                            break
                    i-=1
                
            print("#"*20+"\n")
    if(is_logging):
        print("done searching\n")

def construct_db(data, is_logging=True):
    if(is_logging):
        print('\nConstructing db')
    for filename in os.listdir(os.getcwd()+"/resources"):
        if(not filename.endswith(".pdf")):
            continue
        text = convert_to_text("resources/"+filename)
        with open('resources/'+filename[:filename.rfind('.')]+'.txt', 'w+') as out_file:
            out_file.write(text)
        if(is_logging):
            print(filename[:filename.rfind('.')]+'.txt created')

    if(is_logging):
        print('\ndb done')

data = getlinks()

is_up_to_date = download(data)
if(not is_up_to_date):
    construct_db(data)

string = input("Add meg a szöveg egy részét: ")

find(string, data)

