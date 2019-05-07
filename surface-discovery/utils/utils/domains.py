"""
File providing the methods to get all of a companies domains using various tools
"""
import logging
import requests
import urllib
from utils.conf import surfacediscovery
from utils import duck_test


def clearbit_domains(companies):
    """
    Returns a dictionary of domains mapped to a list of company names

    This function returns a list of domains that companies use, mapped to a list of companies
    in which the domain is associated with in clearbit. The companies whose domains are
    The domains are found using the clearbit company API.

    Arguments:
        parameter companies: The companies whose domains should be found
            precondition: companies is a list of strings
    """
    logging.info('Finding domains using clearbit')
    api_key = surfacediscovery['credentials']['clearbit']['api_key']

    domains = {}

    for company in companies:
        # Format the URL appropriately
        url = "https://company.clearbit.com/v1/companies/search?query=name:{}".format(
            urllib.request.pathname2url(company))

        # Make the request and ensure that it was valid
        response = requests.get(url, auth=(api_key, api_key))
        if response.status_code != 200:
            continue

        # Parse the response dict, and ensure that there is info on the company
        response_dict = response.json()

        if response_dict["total"] <= 0:
            continue

        for result in response_dict["results"]:
            if duck_test.domains_clearbit():
                if result['domain'] in domains:
                    domains[result['domain']].append(company)
                else:
                    domains[result['domain']] = [company]

                for domain in result['domainAliases']:
                    if domain in domains:
                        domains[domain].append(company)
                    else:
                        domains[domain] = [company]

    return domains


def clearbit_company(domain):
    logging.info('Finding company names using clearbit')
    api_key = surfacediscovery['credentials']['clearbit']['api_key']
    url = "https://company.clearbit.com/v1/companies/search?query=domain:{}".format(domain)

    # Make the request and ensure that it was valid
    response = requests.get(url, auth=(api_key, api_key))
    if response.status_code != 200:
        return ''

    # Parse the response dict, and ensure that there is info on the company
    response_json = response.json()

    if response_json["total"] <= 0:
        return ''

    return response_json['results'][0]['legalName']

