"""
File providing the methods to get all of a company's ASNs using Potaroo
"""
import logging
import re
import requests
from bs4 import BeautifulSoup


def potaroo_asns(company_list):
    """
    Returns a dictionary of ASNs mapping to tuples with the type (ASN name, list of companies
    it was found in).

    This function grabs a list of ASNs from potaroo, and parses it to find all
    ASNs that have a description contiaining the company name. This method does
    not do any result validation.

    Arguments:
        company_list: A list of companies to find ASNs for
            precondition: company_list is a list of strings
    """
    logging.info('Finding ASNs Using Potaroo')
    # Grab the ASN list
    potaroo_url = 'http://bgp.potaroo.net/cidr/autnums.html'
    response = requests.get(potaroo_url)
    if response.status_code != 200:
        return {}

    asns = {}
    webpage = response.text.lower()

    # Check every company we have so far
    for item in company_list:
        company = item.lower().replace('(', '').replace(')', '')
        logging.info(company)
        temp = '.*{}.*'.format(company)
        results = re.findall(temp, webpage)

        # Create a regex for error checking
        regex_string = '.*{0}[a-zA-Z0-9].*|.*[a-zA-Z0-9]{0}.*'.format(company)
        regex = re.compile(regex_string)

        # Check every result that potaroo has containing this company name
        for result in results:
            soup = BeautifulSoup(result, 'html.parser')

            asn = str("".join(soup.findAll('a')[0].strings))[2:]
            name = str(soup.text[soup.text.find(' '):].strip())

            # Filter out everything that is not the exact company
            if not regex.match(name):
                if asn in asns:
                    asns[asn][1].append(item)
                else:
                    asns[asn] = (name, [item])
    return asns

