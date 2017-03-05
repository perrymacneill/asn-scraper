#!/usr/bin/env python

import urllib2
import bs4
import re
import json

SITE = 'http://bgp.he.net'

#given url, return soup
def url_to_soup(url):
    # bgp.he.net filters based on user-agent
    req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
    html = urllib2.urlopen(req).read()
    soup = bs4.BeautifulSoup(html)
    return soup

#given soup of the main page, return list of the country subpages
def find_subpages(page):
    subpages = []

    #find every tag with a country link and append to the list
    for link in page.find_all(href=re.compile('/country')):
        subpages.append(link.get('href'))

    return subpages

#given a list of page links, scrape page for ASN data and return as dictionary
def scrape_pages(links):
    mappings = {}

    for link in links:
        #create soup for country page
        country_page = url_to_soup(SITE + link)

        #get the country abbreviation from the URL
        current_country = link.split('/')[2]

        #get each row in the table of ASN data
        for row in country_page.find_all('tr'):
            #get each column of the row
            columns = row.find_all('td')

            #make sure this entry isn't empty
            if len(columns) > 0:
                #strip out the 'AS' from each ASN entry using regex
                current_asn = re.findall(r'\d+', columns[0].string)[0]

                #get the info from the columns
                name = columns[1].string
                routes_v4 = columns[3].string
                routes_v6 = columns[5].string

                #add entry to dictionary with ASN as key, info dictionary as value
                mappings[current_asn] = {'Country': current_country,
    					                 'Name': name,
    					                 'Routes v4': routes_v4,
    					                 'Routes v6': routes_v6}
    return mappings

#given dictionary of ASN mappings, output json to file
def create_json(mapping):
    with open('asndata.txt', 'w') as out_file:
        #write the dicitonary to file as valid aJSON
        json.dump(mapping, out_file)

def main():
    main_page = url_to_soup(SITE + '/report/world')
    
    #get the links to the country pages
    country_links = find_subpages(main_page)
    
    #scrape each country page in the list for ASN info
    asn_mappings = scrape_pages(country_links)
    
    #write the mappings of ASN info to a JSON file
    create_json(asn_mappings)

main()
