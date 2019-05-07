"""
File providing the methods to get all of a companies acquisitions
"""
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from utils.conf import surfacediscovery


def parse_owler(search_list, searched_list):
    """
    Returns a list of companies sourced from Owler

    This helper function scrapes Owler to get all of the acquisitions for
    a single url. It uses Selenium to visit the argument URL then parses it
    to find a list of all acquired companies.

    Arguments:
        None
    """
    # Sets webpage for Owler in Firefox- which does not trigger Captcha
    owldriver = webdriver.Firefox()
    owldriver.get('https://owler.com/')

    # Drives to Sign-in button, username, credentials, and signin
    sleep(5)
    # signin = owldriver.find_element_by_id('signInLink')
    signin = owldriver.find_element_by_id('hp_sign_up_link')
    signin.click()
    sleep(5)
    linkedinclick = owldriver.find_element_by_id('signinLinkedinRegister')
    linkedinclick.click()

    # LinkedIn Signin Window is selected to enter credentials
    sleep(2)
    owldriver.switch_to_window(owldriver.window_handles[1])
    linkedin_user = owldriver.find_element_by_id('session_key-oauthAuthorizeForm')

    # sleep to mitigate captcha triggering
    sleep(4)
    linkedin_user.send_keys(surfacediscovery['credentials']['linkedin']['username'])
    sleep(0.5)
    linkedin_pw = owldriver.find_element_by_id('session_password-oauthAuthorizeForm')
    linkedin_pw.send_keys(surfacediscovery['credentials']['linkedin']['password'])
    sleep(0.9)
    owldriver.find_element_by_css_selector('input[name="authorize"]').click()


    # Create a list of new companies to search for
    acquisition_list = []

    # Iteratively search through each company, and find its acquisitions, and each of their's...
    while search_list:
        temp_search_list = []
        for company in search_list:
            if company in searched_list:
                continue

            # Mark the company as searched
            searched_list.append(company)

            # Search for company in Owler
            select_company_searchbox = owldriver.find_element_by_id('headerBasicSearch')
            select_company_searchbox.sendkeys(company)
            owldriver.find_element_by_id('headerBasicSearch').click()
            owldriver.find_element_by_id('basicSearchSuggestionBox-0').click()

            # Interpret the company's Owler page
            soup = BeautifulSoup(owldriver.page_source, 'html.parser')

            # Find the acquisitons for this company
            for div in soup.findAll('div', {'class': 'cp-acquisition-td-c2'}):
                child = div.find('div', {'class': 'cp-acquisition-td-child'})
                logo_div = child.find('div', {'class': 'cp-logo'})
                image = logo_div.find('img')
                acquisition = image.get('alt')
                acquisition_list.append(acquisition)

                # Add the acquisition to the search list, if not already present
                if acquisition not in search_list:
                    temp_search_list.append(acquisition)
        search_list = temp_search_list

    owldriver.quit()
    return acquisition_list


def parse_crunchbase(url):
    """
    Returns a list of companies

    This helper function scrapes crunchbase to get all acquisitions for a single url. It uses
    selenium to visit the argument url, and then parses it to find a list of all acquired companies

    Arguments:
        parameter url: The crunchbase URL to visit
            precondition: url is a string and is a valid url
    """
    # Start Selenium
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get(url)
    # Get the webpage
    try:
        response = browser.page_source
    except:
        browser.quit()
        return []

    soup = BeautifulSoup(response, 'html.parser')
    acquisition_list = []

    # Find the divs containing the acquisitions
    result = soup.findAll('div', {'class': 'base info-tab acquisitions'})

    # Find every acquisition
    for div in result:
        table = div.findAll('tr')
        for row in table:
            # Skip the table headers
            if row.findAll('th'):
                continue
            acquisition_list.append(row.findAll('td')[1].text)

    # End Selenium
    browser.quit()

    return acquisition_list


def crunchbase_main(company_dict):
    """
    Returns a list of companies

    This function runs the crunchbase scraper to get all acquisitions for a list of companies.
    It iteratively calls parse_crunchbase, and then recursively calls itself until there are no
    longer any new companies to parse.

    Arguments:
        parameter company_dict: A dictionary containing company names and whether or not to visit
                                 them
            precondition: company_dict is a dictionary mapping strings to booleans
    """
    logging.info('Finding Acquisitions with Crunchbase')
    acquisition_list = []

    # Grab each companies acquisitions
    for company, visit in company_dict.items():
        if visit:
            url = 'https://www.crunchbase.com/organization/{0}/acquisitions'.format(company)
            temp = parse_crunchbase(url)
            logging.info('{}: {}'.format(company, temp))
            acquisition_list += temp
            company_dict[company] = False

    # Invariant: Every company in company_dict has been visited

    # Base case: If there are no new companies, there is nothing new to recursively check
    if not acquisition_list:
        return []

    # Invariant: There were acquisitions found, that may or may not be already checked

    # Recursive case: The new companies need to be checked after being added to the company dict
    for company in acquisition_list:
        if company not in company_dict:
            company_dict[company] = True

    return crunchbase_main(company_dict) + acquisition_list
