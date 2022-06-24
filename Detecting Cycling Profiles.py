# from selenium import webdriver
import requests
import pandas as pd
from bs4 import BeautifulSoup


def get_worldtour_pages(year, n):
    """Input : a year to start from, a number of years back to get pages for
      Output : url pages"""
    
    worldtour_pages = []

    for i in range(0,n):
        worldtour_pages.append(f'https://www.procyclingstats.com/races.php?year={year-i}&circuit=1&class=&filter=Filter')

    return worldtour_pages



def get_race_links(races_url, root_url):
    """Input : races_url with races on it from PSC -> e.g https://www.procyclingstats.com/, root url to append on
       Output : get a list of race links from page"""
    
    races = requests.get(races_url)
    soup = BeautifulSoup(races.content, "html.parser")
    
    # filter out first tr tag which is empty
    parsed = soup.find_all('tr')[1:]
    
    # get 3rd element in td tag and extract href - insert on root_url at front
    return [root_url + a.find_all('td')[2].a['href'] for a in parsed]




def get_profile_pg(race_url, try_gc):
    """Input : a url for a stage race, a substring which checks to see if gc profile page works -> /gc/stages/all-stage-profiles
       Output : a url of the right profile page to scrape"""
    
    response = requests.get(race_url + try_gc)
    soup = BeautifulSoup(response.content, "html.parser")
    
    if soup.find('img') is None:
        return race_url + '/result/today/profiles'
    
    return race_url + try_gc




def get_gc_profile_imgs(profiles_url):
    """Input : a url with race profiles across stages
       Output : a list of domains for all the stage profile images for the race"""

    response = requests.get(profiles_url)
    soup = BeautifulSoup(response.content, "html.parser")

    result = soup.find_all('img')
    
    # the if statement throws away all the src tags that dont exist
    return ['https://www.procyclingstats.com/' + i['src'] for i in result if i['src'] is not None]




def get_profile_img(profile_url):
    """Input : a url with race profile for race
       Output : a domain for the profile image for the race"""

    response = requests.get(profile_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # is there a better way for this error handling type thingy?
    if soup.find('img') == None:
        return None
    else:
        return 'https://www.procyclingstats.com/' + soup.find('img')['src']




def download_image(img_url):
    # Is there a better way to do this? In terms of saving images - probably is will worry about this later
    """Input : an img_url
       Output : the image is saved as a file"""
    img_data = requests.get(image_url).content
    with open(f'{img_name}.jpg', 'wb') as handler:
        handler.write(img_data)





# need to research in general best style of ingesting data. here my functions are very functional, they have a single input and produce
# several outputs or one output. there isn't much care on the holistic flow of data - it could probs be cleaner. should a fn applied to many
# handle a many to many (rather than the current one to one which is looped over)? (The for loop scrapes are also v slow)
# might be worth having some data structure of race-year during the scraping process - another option is to have a cleaning script after based
# on the domains we have for the images

def main():
    wt_pages =  get_worldtour_pages(2022, 10)
    
    # loop over pages with races, store each race link in big list
    races = []
    
    for page in wt_pages:
        race_links = get_race_links(page, 'https://www.procyclingstats.com/')
        races.extend(race_links)
    
    # loop over races to get profile pages for each individual race
    profiles = []
    
    for race in races:
        profile = get_profile_pg(race,'/gc/stages/all-stage-profiles')
        profiles.append(profile)
    
    # get domains for images for all stages (both gc and single)
    gc_profiles = [y for x in profiles for y in get_gc_profile_imgs(x) if 'gc/stages' in x]
    single_profiles = [get_profile_img(x) for x in profiles if 'gc/stages' not in x]
    
    profile_imgs = gc_profiles + single_profiles
        
    return profile_imgs




if __name__ == '__main__':
    
    profiles = main()
    
    #   # download images
    #     for i in profiles:
    #         download_image(i)
    





