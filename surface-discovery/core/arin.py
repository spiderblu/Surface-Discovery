"""
foo
"""
import logging
import netaddr
import requests
import urllib
from bs4 import BeautifulSoup
from utils.conf import surfacediscovery


def arin_company(company_search_list, company_searched_list, customer_search_list,
        customer_searched_list, org_search_list, ip_search_list, poc_search_list, asn_search_list,
        new_customers, new_orgs, new_ips, new_pocs, new_asns):
    # For every company in the company search list
    for company in company_search_list:
        # if its not in searched list
        if company not in company_searched_list:
            logging.info('Searching for company {} in ARIN'.format(company))
            # Add it to the searched list
            company_searched_list.append(company)

            # Get the URL
            # If duck test is 0, do not do fuzzy search to prevent missing results
            if surfacediscovery['fuzzy_search']:
                query = '{}*'.format(company)
            else:
                query = '{}'.format(company)

            response = requests.post('https://whois.arin.net/ui/query.do',
                data={'queryinput': query})

            # If the url was not gotten properly
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.findAll('tr')
            # Get all customers, orgs, networks, and POCs by checking each row in the table
            for row in table:
                if row.find('th'):
                    current = row.find('th').text
                    continue
                if current == 'Customers':
                    value = row.find('td').find('a').text
                    if value and value not in customer_search_list and value not in customer_searched_list:
                        customer_search_list.append(value)
                        new_customers.append(value)
                elif current == 'Organizations':
                    value = row.find('td').find('a').text
                    org_search_list.append(value)
                    new_orgs.append(value)
                elif current == 'Networks':
                    value = row.findAll('td')[1].text.split(' - ')
                    cidr = str(netaddr.iprange_to_cidrs(value[0], value[1])[0])
                    ip_search_list.append(cidr)
                    new_ips.append(cidr)
                elif current == 'Points of Contact':
                    value = row.find('td').find('a').text
                    poc_search_list.append(value)
                    new_pocs.append(value)
                elif current == 'Autonomous System Numbers':
                    value = row.find('td').find('a').text[2:]
                    asn_search_list.append(value)
                    new_asns.append(value)
                else:
                    continue

    return (company_searched_list, customer_search_list, customer_searched_list, org_search_list,
    ip_search_list, poc_search_list, asn_search_list, new_customers, new_orgs, new_ips, new_pocs,
    new_asns)


def arin_customer(customer):
    logging.info('Searching ARIN for CUSTOMER {}'.format(customer))

    customer_info = {}
    customer_info['name'] = ''
    customer_info['nets'] = set()
    customer_info['metadata'] = {}
    customer_info['metadata']['street'] = ''
    customer_info['metadata']['city'] = ''
    customer_info['metadata']['state'] = ''
    customer_info['metadata']['zip_code'] = ''
    customer_info['metadata']['country'] = ''

    if customer in surfacediscovery['ignore']['arin_poc']:
        return customer_info

    # Get the Customer's info
    url = 'https://whois.arin.net/rest/customer/{}'.format(customer)
    customer_info['url'] = url
    try:
        response = requests.get(url, headers={'accept': 'application/json'})
    except:
        return customer_info

    if response.status_code != 200:
        return customer_info
    response_json = response.json()

    # Parse the customer info
    if 'name' in response_json['customer']:
        customer_info['name'] = response_json['customer']['name']['$']
    if 'streetAddress' in response_json['customer']:
        addr = response_json['customer']['streetAddress']['line']
        cases = {list: lambda x: x[0]['$'], dict: lambda x: x['$']}
        customer_info['metadata']['street'] = cases[type(addr)](addr)
    if 'city' in response_json['customer']:
        customer_info['metadata']['city'] = response_json['customer']['city']['$']
    if 'iso3166-2' in response_json['customer']:
        customer_info['metadata']['state'] = response_json['customer']['iso3166-2']['$']
    if 'postalCode' in response_json['customer']:
        customer_info['metadata']['zip_code'] = response_json['customer']['postalCode']['$']
    if 'iso3166-1' in response_json['customer']:
        customer_info['metadata']['country'] = response_json['customer']['iso3166-1']['name']['$']



    # Get the NET url & info
    url = 'https://whois.arin.net/rest/customer/{}/nets'.format(customer)
    try:
        response = requests.get(url, headers={'accept': 'application/json'})
    except:
        return customer_info
    if response.status_code == 200:
        response_json = response.json()

        # Get all NETs
        if 'netRef' in response_json['nets']:
            if isinstance(response_json['nets']['netRef'], list):
                for item in response_json['nets']['netRef']:
                    start_addr = item['@startAddress']
                    end_addr = item['@endAddress']
                    for item in netaddr.iprange_to_cidrs(start_addr, end_addr):
                        ip = str(item)
                        customer_info['nets'].add(ip)

            else:
                start_addr = response_json['nets']['netRef']['@startAddress']
                end_addr = response_json['nets']['netRef']['@endAddress']
                for item in netaddr.iprange_to_cidrs(start_addr, end_addr):
                    ip = str(item)
                    customer_info['nets'].add(ip)

    return customer_info


def arin_poc(poc):
    logging.info('Searching ARIN for POC {}'.format(poc))
    poc_info = {}
    poc_info['name'] = ''
    poc_info['orgs'] = set()
    poc_info['metadata'] = {}
    poc_info['metadata']['company'] = ''
    poc_info['metadata']['street'] = ''
    poc_info['metadata']['city'] = ''
    poc_info['metadata']['state'] = ''
    poc_info['metadata']['zip_code'] = ''
    poc_info['metadata']['country'] = ''
    poc_info['metadata']['email'] = ''


    # Get the POC's information
    url = 'https://whois.arin.net/rest/poc/{}'.format(poc)
    poc_info['url'] = url
    try:
        response = requests.get(url, headers={'accept': 'application/json'})
    except:
        return poc_info

    if response.status_code != 200:
        return poc_info
    response_json = response.json()

    # Parse the POC's information
    if 'firstName' in response_json['poc']:
        poc_info['name'] += response_json['poc']['firstName']['$']
    if 'lastName' in response_json['poc']:
        poc_info['name'] += ' '
        poc_info['name'] += response_json['poc']['lastName']['$']
    if 'companyName' in response_json['poc']:
        poc_info['metadata']['company'] += response_json['poc']['companyName']['$']
    if 'streetAddress' in response_json['poc']:
        addr = response_json['poc']['streetAddress']['line']
        cases = {list: lambda x: x[0]['$'], dict: lambda x: x['$']}
        poc_info['metadata']['street'] = cases[type(addr)](addr)
    if 'city' in response_json['poc']:
        poc_info['metadata']['city'] = response_json['poc']['city']['$']
    if 'iso3166-2' in response_json['poc']:
        poc_info['metadata']['state'] = response_json['poc']['iso3166-2']['$']
    if 'postalCode' in response_json['poc']:
        poc_info['metadata']['zip_code'] = response_json['poc']['postalCode']['$']
    if 'iso3166-1' in response_json['poc']:
        poc_info['metadata']['country'] = response_json['poc']['iso3166-1']['name']['$']
    if 'emails' in response_json['poc']:
        cases = {list: lambda x: x[0]['$'], dict: lambda x: x['$']}
        email = response_json['poc']['emails']['email']
        poc_info['metadata']['email'] = cases[type(email)](email)



    # Get the ORG url & info
    url = 'https://whois.arin.net/rest/poc/{}/orgs'.format(poc)
    try:
        response = requests.get(url, headers={'accept': 'application/json'})
    except:
        return poc_info

    if response.status_code != 200:
        return poc_info
    response_json = response.json()

    # Get all ORGS
    if 'orgPocLinkRef' in response_json['orgs']:
        if isinstance(response_json['orgs']['orgPocLinkRef'], list):
            org_list = set([d['@handle'] for d in response_json['orgs']['orgPocLinkRef']])
            for org in org_list:
                poc_info['orgs'].add(org)
        else:  # It's a dictionary
            org = response_json['orgs']['orgPocLinkRef']['@handle']
            poc_info['orgs'].add(org)
    return poc_info


def arin_org(org):
    logging.info('Searching ARIN for ORG {}'.format(org))
    org_info = {}
    org_info['name'] = ''
    org_info['nets'] = set()
    org_info['asns'] = set()
    org_info['pocs'] = set()
    org_info['metadata'] = {}
    org_info['metadata']['street'] = ''
    org_info['metadata']['city'] = ''
    org_info['metadata']['state'] = ''
    org_info['metadata']['zip_code'] = ''
    org_info['metadata']['country'] = ''

    # Get the ORG's information
    url = 'https://whois.arin.net/rest/org/{}'.format(org)
    org_info['url'] = url
    try:
        response = requests.get(url, headers={'accept': 'application/json'})
    except:
        return org_info

    if response.status_code != 200:
        return org_info
    response_json = response.json()

    # Parse the ORG's information

    if 'name' in response_json['org']:
        org_info['name'] = response_json['org']['name']['$']
    if 'streetAddress' in response_json['org']:
        addr = response_json['org']['streetAddress']['line']
        cases = {list: lambda x: x[0]['$'], dict: lambda x: x['$']}
        org_info['metadata']['street'] = cases[type(addr)](addr)
    if 'city' in response_json['org']:
        org_info['metadata']['city'] = response_json['org']['city']['$']
    if 'iso3166-2' in response_json['org']:
        org_info['metadata']['state'] = response_json['org']['iso3166-2']['$']
    if 'postalCode' in response_json['org']:
        org_info['metadata']['zip_code'] = response_json['org']['postalCode']['$']
    if 'iso3166-1' in response_json['org']:
        org_info['metadata']['country'] = response_json['org']['iso3166-1']['name']['$']


    # Get the NET url & info
    url = 'https://whois.arin.net/rest/org/{}/nets'.format(org)
    try:
        response = requests.get(url, headers={'accept': 'application/json'})
        if response.status_code == 200:
            response_json = response.json()

            # Get all NETs
            if 'netRef' in response_json['nets']:
                if isinstance(response_json['nets']['netRef'], list):
                    for net in response_json['nets']['netRef']:
                        start_addr = net['@startAddress']
                        end_addr = net['@endAddress']
                        for item in netaddr.iprange_to_cidrs(start_addr, end_addr):
                            ip = str(item)
                            org_info['nets'].add(ip)
                else:  # It's a dictionary
                        start_addr = response_json['nets']['netRef']['@startAddress']
                        end_addr = response_json['nets']['netRef']['@endAddress']
                        for item in netaddr.iprange_to_cidrs(start_addr, end_addr):
                            ip = str(item)
                            org_info['nets'].add(ip)
    except:
        return org_info


    # Get the POC url & info
    url = 'https://whois.arin.net/rest/org/{}/pocs'.format(org)
    try:
        response = requests.get(url, headers={'accept': 'application/json'})

        if response.status_code == 200:
            response_json = response.json()

            # Get all POCs
            if 'pocLinkRef' in response_json['pocs']:
                if isinstance(response_json['pocs']['pocLinkRef'], list):
                    poc_list = set([d['@handle'] for d in response_json['pocs']['pocLinkRef']])
                    for poc in poc_list:
                        org_info['pocs'].add(poc)
                else:  # It's a dict
                    poc = response_json['pocs']['pocLinkRef']['@handle']
                    org_info['pocs'].add(poc)
    except:
        return org_info


    # Get the ASN url & info
    url = 'https://whois.arin.net/rest/org/{}/asns'.format(org)
    try:
        response = requests.get(url, headers={'accept': 'application/json'})
        if response.status_code == 200:
            response_json = response.json()

            # Get all ASNs
            if 'asnRef' in response_json['asns']:
                if isinstance(response_json['asns']['asnRef'], list):
                    asn_list = set([d['@handle'][2:] for d in response_json['asns']['asnRef']])
                    for asn in asn_list:
                        org_info['asns'].add(asn)
                else:  # It's a dict
                    asn = response_json['asns']['asnRef']['@handle'][2:]
                    org_info['asns'].add(asn)
    except:
        return org_info

    return org_info


def arin_asn(asn):
    logging.info('Searching ARIN for ASN {}'.format(asn))
    asn_info = {}
    asn_info['name'] = ''
    asn_info['pocs'] = set()
    asn_info['orgs'] = set()
    asn_info['metadata'] = {}
    asn_info['metadata']['organization'] = ''

    # Get the ASN's info
    url = 'https://whois.arin.net/rest/asn/AS{}'.format(asn)
    asn_info['url'] = url
    try:
        response = requests.get(url, headers={'accept': 'application/json'})
    except:
        return asn_info

    if response.status_code != 200:
        return asn_info
    response_json = response.json()

    # Parse the ASN's info
    if 'name' in response_json['asn']:
        asn_info['name'] = response_json['asn']['name']['$']
    if 'orgRef' in response_json['asn']:
        asn_info['metadata']['organization'] = response_json['asn']['orgRef']['@name']
        asn_info['orgs'].add(response_json['asn']['orgRef']['@handle'])

    # Get the POC url & info
    url = 'https://whois.arin.net/rest/asn/AS{}/pocs'.format(asn)
    try:
        response = requests.get(url, headers={'accept': 'application/json'})

        if response.status_code != 200:
            return asn_info
        response_json = response.json()

        # Get all POCs
        if 'pocLinkRef' in response_json['pocs']:
            if isinstance(response_json['pocs']['pocLinkRef'], list):
                poc_list = set([d['@handle'] for d in response_json['pocs']['pocLinkRef']])
                for poc in poc_list:
                    asn_info['pocs'].add(poc)
            else:  # It's a dict
                poc = response_json['pocs']['pocLinkRef']['@handle']
                asn_info['pocs'].add(poc)
    except:
        return asn_info

    return asn_info


def arin_net(net):
    logging.info('Searching ARIN for NET {}'.format(net))
    net_info = {}
    net_info['name'] = ''
    net_info['customers'] = set()

    # Get the NET's info
    handle = net[0:net.find('/')].replace('.', '-')
    url = 'https://whois.arin.net/rest/net/NET-{}-1'.format(handle)
    net_info['url'] = url
    try:
        response = requests.get(url, headers={'accept': 'application/json'})
    except:
        return net_info

    if response.status_code != 200:
        return net_info
    response_json = response.json()

    # Parse the ASN's info
    if 'name' in response_json['net']:
        net_info['name'] = response_json['net']['name']['$']
    if 'customerRef' in response_json['net']:
        net_info['customers'].add(response_json['net']['customerRef']['@handle'])

    return net_info



def whois_arin_main(graph, company_search_set, company_searched_set):
    """
    Returns a dictionary of companies, ASNs, IPs, and domains

    This function scrapes the ARIN whois database (https://www.arin.net) to find various companies,
    ASNs, IPs, customers, POCs, and organiztions when given each of these things. If more items are
    found, it will call itself recursively until no further items are found. It returns the items
    that it found as a dictionary with the following specification:
        {
         companies: [strings]
         ASNs: [integers]
         IPs: [strings]
         domains: [strings],
         customers: [strings],
         POCs: [strings],
         ORGs: [strings]
        }
    If an error occurs, this function returns the specified dictionaries with empty lists as values.

    Arguments:
        parameter search_info: A dictionary containing the information to search for in ARIN
            precondition: search info is a dictionary with the following specifictaion:
                {companies: [strings],
                 ASNs: [integers],
                 IPs: [strings],
                 domains: [strings],
                 customers: [strings],
                 POCs: [strings],
                 ORGs: [strings]}
        parameter visited_info: A dictionary containing the information to exclude from a search in
         ARIN
            precondition: search info is a dictionary with the following specifictaion:
                {companies: [strings],
                 ASNs: [integers],
                 IPs: [strings],
                 domains: [strings],
                 customers: [strings],
                 POCs: [strings],
                 ORGs: [strings]}
    """
    logging.info('Running whois ARIN')
    for company in company_search_set:

        if company in company_searched_set:
            continue

        company_searched_set.add(company)

        for obj_type in ['ORG', 'CUSTOMER', 'NET', 'ASN', 'POC']:
            logging.info('Searching ARIN {} objects for {}'.format(obj_type, company))
            obj_name = obj_type.lower()
            obj = obj_type.lower() + 's'

            url = 'https://whois.arin.net/rest/{};name={}'.format(obj,
                    urllib.request.pathname2url(company))
            if surfacediscovery['fuzzy_search']:
                url += '*'

            try:
                response = requests.get(url, headers={'accept': 'application/json'})
            except:
                continue

            if response.status_code != 200:
                continue
            response_json = response.json()

            ref = '{}Ref'.format(obj_name)

            if obj_type == 'NET':
                if not isinstance(response_json[obj][ref], list):
                    result = response_json[obj][ref]
                    link = result['$']
                    name = result['@name']
                    start_addr = result['@startAddress']
                    end_addr = result['@endAddress']
                    for item in netaddr.iprange_to_cidrs(start_addr, end_addr):
                        handle = str(item)
                        if graph.has_node(handle) and 'ARIN' in graph.node[handle]['visited']:
                            continue
                        graph.add_node(handle, origin='ARIN search for {}'.format(company),
                                sources=set(['ARIN']), name=name, visited=[], object_type=obj_type,
                                url=link)
                else:
                    for result in response_json[obj][ref]:
                        link = result['$']
                        name = result['@name']
                        start_addr = result['@startAddress']
                        end_addr = result['@endAddress']

                        for item in netaddr.iprange_to_cidrs(start_addr, end_addr):
                            handle = str(item)
                            if graph.has_node(handle) and 'ARIN' in graph.node[handle]['visited']:
                                continue
                            graph.add_node(handle, origin='ARIN search for {}'.format(company),
                                    sources=set(['ARIN']), name=name, visited=[], object_type=obj_type,
                                    url=link)
            else:
                if not isinstance(response_json[obj][ref], list):
                    result = response_json[obj][ref]
                    handle = result['@handle']
                    if obj_type == 'ASN':
                        handle = handle[2:]
                    if obj_type == 'POC' and handle in surfacediscovery['ignore']['arin_poc']:
                        continue
                    link = result['$']
                    name = result['@name']
                    if graph.has_node(handle) and 'ARIN' in graph.node[handle]['visited']:
                        continue

                    graph.add_node(handle, origin='ARIN search for {}'.format(company),
                            sources=set(['ARIN']), name=name, visited=[], object_type=obj_type,
                            url=link)
                else:
                    for result in response_json[obj][ref]:
                        handle = result['@handle']
                        if obj_type == 'ASN':
                            handle = handle[2:]
                        if obj_type == 'POC' and handle in surfacediscovery['ignore']['arin_poc']:
                            continue
                        link = result['$']
                        name = result['@name']

                        if graph.has_node(handle) and 'ARIN' in graph.node[handle]['visited']:
                            continue

                        graph.add_node(handle, origin='ARIN search for {}'.format(company),
                                sources=set(['ARIN']), name=name, visited=[], object_type=obj_type,
                                url=link)

    items_added = True
    while items_added:
        items_added = False
        for node_name in graph.nodes():
            node = graph.node[node_name]
            if 'ARIN' in node['visited']:
                continue
            node['visited'].append('ARIN')

            if node['object_type'] == 'DOMAIN':
                continue

            elif node['object_type'] == 'NET':
                net_info = arin_net(node_name)
                node['sources'].add('ARIN')
                node['name'] = net_info['name']
                node['url'] = net_info['url']
                for customer in net_info['customers']:
                    if graph.has_node(customer):
                        graph.add_edge(node_name, customer)
                        graph.node[customer]['sources'].add('ARIN')
                        continue
                    graph.add_node(customer, origin='ARIN, linked from NET {} ({})'.format(node_name,
                            node['name']), sources=set(['ARIN']), name='', visited=[],
                            object_type='CUSTOMER', url='')
                    graph.add_edge(node_name, customer)
                    items_added = True



            elif node['object_type'] == 'ORG':
                org_info = arin_org(node_name)
                node['info'] = org_info['metadata']
                node['sources'].add('ARIN')
                node['name'] = org_info['name']
                node['url'] = org_info['url']
                for net in org_info['nets']:
                    if graph.has_node(net):
                        graph.add_edge(node_name, net)
                        graph.node[net]['sources'].add('ARIN')
                        continue
                    graph.add_node(net, origin='ARIN, linked from ORG {} ({})'.format(node['name'],
                            node_name), sources=set(['ARIN']), name='', visited=[],
                            object_type='NET', url='')
                    graph.add_edge(node_name, net)
                    items_added = True
                for asn in org_info['asns']:
                    if graph.has_node(asn):
                        graph.add_edge(node_name, asn)
                        graph.node[asn]['sources'].add('ARIN')
                        continue
                    graph.add_node(asn, origin='ARIN, linked from ORG {} ({})'.format(node['name'],
                            node_name), sources=set(['ARIN']), name='', visited=[],
                            object_type='ASN', url='')
                    graph.add_edge(node_name, asn)
                    items_added = True
                for poc in org_info['pocs']:
                    if poc in surfacediscovery['ignore']['arin_poc']:
                        continue
                    if graph.has_node(poc):
                        graph.add_edge(node_name, poc)
                        graph.node[poc]['sources'].add('ARIN')
                        continue
                    graph.add_node(poc, origin='ARIN, linked from ORG {} ({})'.format(node['name'],
                            node_name), sources=set(['ARIN']), name='', visited=[],
                            object_type='POC', url='')
                    graph.add_edge(node_name, poc)
                    items_added = True

            elif node['object_type'] == 'CUSTOMER':
                customer_info = arin_customer(node_name)
                node['info'] = customer_info['metadata']
                node['sources'].add('ARIN')
                node['name'] = customer_info['name']
                node['url'] = customer_info['url']
                for net in customer_info['nets']:
                    if graph.has_node(net):
                        graph.add_edge(node_name, net)
                        graph.node[net]['sources'].add('ARIN')
                        continue
                    graph.add_node(net, origin='ARIN, linked from CUSTOMER {} ({})'.format(
                            node['name'], node_name), sources=set(['ARIN']), name='', visited=[],
                            object_type='NET', url='')
                    graph.add_edge(node_name, net)
                    items_added = True

            elif node['object_type'] == 'ASN':
                asn_info = arin_asn(node_name)
                node['info'] = asn_info['metadata']
                node['sources'].add('ARIN')
                node['name'] = asn_info['name']
                node['url'] = asn_info['url']
                for org in asn_info['orgs']:
                    if graph.has_node(org):
                        graph.add_edge(node_name, org)
                        graph.node[org]['sources'].add('ARIN')
                        continue
                    graph.add_node(org, origin='ARIN, linked from ASN {} ({})'.format(node['name'],
                            node_name), sources=set(['ARIN']), name='', visited=[],
                            object_type='ORG', url='')
                    graph.add_edge(node_name, org)
                    items_added = True
                for poc in asn_info['pocs']:
                    if poc in surfacediscovery['ignore']['arin_poc']:
                        continue
                    if graph.has_node(poc):
                        graph.add_edge(node_name, poc)
                        graph.node[poc]['sources'].add('ARIN')
                        continue
                    graph.add_node(poc, origin='ARIN, linked from ASN {} ({})'.format(node['name'],
                            node_name), sources=set(['ARIN']), name='', visited=[],
                            object_type='POC', url='')
                    graph.add_edge(node_name, poc)
                    items_added = True

            elif node['object_type'] == 'POC':
                poc_info = arin_poc(node_name)
                node['info'] = poc_info['metadata']
                node['sources'].add('ARIN')
                node['name'] = poc_info['name']
                node['url'] = poc_info['url']
                for org in poc_info['orgs']:
                    if graph.has_node(org):
                        graph.add_edge(node_name, org)
                        graph.node[org]['sources'].add('ARIN')
                        continue
                    graph.add_node(org, origin='ARIN, linked from POC {} ({})'.format(node['name'],
                            node_name), sources=set(['ARIN']), name='', visited=[],
                            object_type='ORG', url='')
                    graph.add_edge(node_name, org)
                    items_added = True
    return graph















def arin_org_enumerate(org_list):
    # for org in org_list:
        # determine the ending portion
        # Create the original
        # if the original is in the already checked list, move on
        # Add the original to a list of things I've already enumerated
        # Check the original without an integer
        # Set the timeout counter to 0
        # for i in range(0, surfacediscovery['whois']['org enumeration limit'])
        #   if timeout counter is >=5 break and continue
        #   otherwise, check this element
        #   if this element exists set timeout to 0, otherwise, increase it
    pass
