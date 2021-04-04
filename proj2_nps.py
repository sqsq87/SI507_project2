#################################
##### Name:Qi Sun
##### Uniqname:sqsq
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
from secrets import API_KEY
CACHE_FILE_NAME= 'cache.json'
CACHE_DICT={}

def load_cache():
    '''load the cache
    
    Parameters
    ----------
    None

    Returns
    -------
    dict
        the cache in the python type of dict
    '''
    try:
        cache_file=open(CACHE_FILE_NAME, 'r')
        cache_file_contents=cache_file.read()
        cache=json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache={}
    return cache

def save_cache(cache):
    '''save the cache
    
    Parameters
    ----------
    dict
        the cache to be saved

    Returns
    -------
    none
    '''
    cache_file=open(CACHE_FILE_NAME,'w')
    contents_to_write=json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()
    
def make_url_request_use_cache(url,cache, params='none'):
    '''make the request with the help of cache
    
    Parameters
    ----------
    url: string
        the url of the request
    cache: dict
        the saved cache in the python type of dict
    params: dict 
        the parameters required to be sent to the API

    Returns
    -------
    string
        the response text
    '''
    if (params=='none'):
        if (url in cache.keys()):
            print('Using cache')
            return cache[url]
        else:
            print('Fetching')
            rep=requests.get(url)
            cache[url]=rep.text
            save_cache(cache)
            return cache[url]
    else:
        if ((url+str(params)) in cache.keys()):
            print('Using cache')
            return cache[url+str(params)]
        else: 
            print('Fetching')
            rep=requests.get(url,params=params)
            cache[url+str(params)]=json.loads(rep.text)
            save_cache(cache)
            return cache[url+str(params)]
            
           
class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return (self.name+' ('+self.category+'): '+self.address+' '+
              self.zipcode)



def build_state_url_dict():
    
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    url_dict={}
    url=' https://www.nps.gov/index.htm'
    base_url='https://www.nps.gov'
    rep_text=make_url_request_use_cache(url, CACHE_DICT)
    soup=BeautifulSoup(rep_text, 'html.parser')
    ul=soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch')
    all_list=ul.find_all('li')
    for item in all_list:
        state=item.find('a').text.strip().lower()
        state_url=base_url+item.find('a')['href']
        url_dict[state]=state_url
    
    return url_dict



def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    rep_text = make_url_request_use_cache(site_url,CACHE_DICT)
    soup = BeautifulSoup(rep_text, 'html.parser')
    name = soup.find('a', class_='Hero-title').text.strip()
    try:
        address = soup.find(
            'span', itemprop='addressLocality').text.strip() + ', ' + soup.find(
                'span', itemprop='addressRegion').text.strip()
    except:
        address = 'no address'
    try:
        zipcode = soup.find('span', itemprop='postalCode').text.strip()
    except:
        zipcode ='no zipcode'
    try: 
        phone = soup.find('span', itemprop='telephone').text.strip()
    except: 
        phone='no phone'
    try:
        category = soup.find('span', class_='Hero-designation').text.strip()
    except:
        category =''
    return NationalSite(category, name, address, zipcode, phone)



def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    rep_text=make_url_request_use_cache(state_url,CACHE_DICT)
    soup=BeautifulSoup(rep_text, 'html.parser')
    all_sites=soup.find_all('div',class_='col-md-9 col-sm-9 col-xs-12 table-cell list_left')
    base_url='https://www.nps.gov'
    instance_all=[]
    for item in all_sites:
        url=base_url+item.find('h3').find('a')['href']+'index.htm'
        instance_all.append(get_site_instance(url))
    return instance_all


    



def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    url='http://www.mapquestapi.com/search/v2/radius'
    params = {
    'key': API_KEY,
    'origin': site_object.zipcode,
    'radius': 10,
    'maxMatches':10,
    'ambiguities':'ignore',
    'outFormat':'json'
}
    req = make_url_request_use_cache(url,CACHE_DICT,params=params)
    all_place=req
    return all_place

def display_nearby_place_result(all_place):
    '''return the list of printed version of the nearby places

    iterate through the list of instances of NationalSite
    for each site, find its names, address, category and city
    
    Parameters
    ----------
    all_place: dict
        a converted result return from MapQuest API 


    Returns
    -------
    list:
        a list of the printed version of each nearby place
    '''
    return_list = []
    for item in all_place['searchResults']:
        if item['fields']['group_sic_code_name'] == '':
            category = 'no category'
        else:
            category = item['fields']['group_sic_code_name']
        if item['fields']['address'] == '':
            address = 'no address'
        else:
            address = item['fields']['address']
        if item['fields']['city'] == '':
            city = 'no city'
        else:
            city = item['fields']['city']
        object_return = '- ' + item[
            'name'] + ' (' + category + '): ' + address + ', ' + city
        return_list.append(object_return)
    return return_list

def prompt_user_state():
    '''prompt the user the input a state
    
    if the user inputs a 'exit', exit the program
    if the user inputs a correct state, output all tha national sites in it
    if the user inputs a inproper thing, let the user input again 

    
    
    Parameters
    ----------
    None


    Returns
    -------
    dict:
        a dict of all instances of nationalSite
    '''
    while(True):
        state_name = input('Enter a state name(e.g. Michigan, michigan) or "exit": ')
        if state_name.lower() == 'exit':
            exit()
        else:
            all_state_url = build_state_url_dict()
            if state_name.lower() in all_state_url.keys():
                instance_all = get_sites_for_state(
                    all_state_url[state_name.lower()])
                print('-'*len('List of national sites in '+state_name.lower()))
                print('List of national sites in '+state_name.lower())
                print('-'*len('List of national sites in '+state_name.lower()))
                index=1
                instance_all_dict={}
                for item in instance_all:
                    print('['+str(index)+'] '+item.info())
                    instance_all_dict[str(index)]=item
                    index=index+1
                return instance_all_dict
            else:
                print('[Error] Enter proper state name')




if __name__ == "__main__":
    CACHE_DICT = load_cache()
    instance_all_dict=prompt_user_state()
    while(True):
        number=input('Choose the number for detail search or "exit" or "back": ')
        number=number.lower()
        if number=='back':
            instance_all_dict=prompt_user_state()
        elif number=='exit':
            exit()
        elif number in instance_all_dict.keys():
            site_instance=get_nearby_places(instance_all_dict[number])
            print('-'*len('Places near '+instance_all_dict[number].name))
            print('Places near '+instance_all_dict[number].name)
            print('-'*len('Places near '+instance_all_dict[number].name))
            for i in display_nearby_place_result(site_instance):
                print(i)
        else:
            print('Invalid input')


        
            
        
    

    
