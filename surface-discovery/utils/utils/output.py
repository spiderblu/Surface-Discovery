import csv
import logging
from utils.conf import surfacediscovery


def write_csv_output(company_name, graph, companies):
    logging.info('Writing CSV Output')

    keepcharacters = (' ', '.', '_')
    company = "".join(c for c in company_name if c.isalnum() or c in keepcharacters).rstrip()

    with open('{}/{}_Domains.csv'.format(surfacediscovery['output dir'], company), 'w',
            newline='') as csvfile:
        domain_writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                quoting=csv.QUOTE_MINIMAL)
        domain_writer.writerow(['Number of Neighbors', 'Domain', 'Origin', 'Sources', 'Neighbors'])

        with open('{}/{}_ASNs.csv'.format(surfacediscovery['output dir'], company), 'w',
                newline='') as csvfile:
            asn_writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                    quoting=csv.QUOTE_MINIMAL)
            asn_writer.writerow(['Number of Neighbors', 'Autonomous System Number', 'Name',
                'Organization', 'Origin', 'Sources', 'URL', 'Neighbors'])

            with open('{}/{}_IPs.csv'.format(surfacediscovery['output dir'], company), 'w',
                    newline='') as csvfile:
                ip_writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)
                ip_writer.writerow(['Number of Neighbors', 'IP Address Prefix', 'Origin', 'Source',
                    'Name', 'URL', 'Neighbors'])

                with open('{}/{}_ORGs.csv'.format(surfacediscovery['output dir'], company), 'w',
                        newline='') as csvfile:
                    org_writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
                    org_writer.writerow(['Number of Neighbors', 'Name', 'Origin', 'Sources',
                        'Handle', 'Street', 'City', 'State', 'Zip Code', 'Country', 'URL', 'Neighbors'])

                    with open('{}/{}_POCs.csv'.format(surfacediscovery['output dir'], company),
                            'w', newline='') as csvfile:
                        poc_writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
                        poc_writer.writerow(['Number of Neighbors', 'Name', 'Email', 'Origin',
                            'Sources', 'Handle', 'Street', 'City', 'State', 'Zip Code', 'Country',
                            'URL', 'Neighbors'])

                        with open('{}/{}_Customers.csv'.format(surfacediscovery['output dir'],
                                company), 'w', newline='') as csvfile:
                            customer_writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
                            customer_writer.writerow(['Number of Neighbors', 'Name', 'Origin',
                                'Sources', 'Handle', 'Street', 'City', 'State', 'Zip Code',
                                'Country', 'URL', 'Neighbors'])

                            for node_name in graph.nodes_iter():
                                node = graph.node[node_name]

                                if node['object_type'] == 'DOMAIN':
                                    num_neighbors = len(graph.neighbors(node_name))
                                    domain_writer.writerow([num_neighbors,  # Number of Neighbors
                                        node_name,  # Domain name
                                        node['origin'],  # Origin
                                        ', '.join(node['sources']),  # Sources
                                        ', '.join(graph.neighbors(node_name))])  # Neighbors


                                elif node['object_type'] == 'NET':
                                    num_neighbors = len(graph.neighbors(node_name))
                                    ip_writer.writerow([num_neighbors,  # Number of Neighbors
                                        node_name,  # Prefix
                                        node['origin'],  # Origin
                                        ', '.join(node['sources']),  # Sources
                                        node['name'],  # Name
                                        node['url'],  # URL
                                        ', '.join(graph.neighbors(node_name))])  # Neighbors

                                elif node['object_type'] == 'ORG':
                                    num_neighbors = len(graph.neighbors(node_name))
                                    org_writer.writerow([num_neighbors,
                                        node['name'],  # Name
                                        node['origin'],  # Origin
                                        ', '.join(node['sources']),  # Sources
                                        node_name,  # Handle
                                        node['info']['street'],  # Street
                                        node['info']['city'],  # City
                                        node['info']['state'],  # State
                                        node['info']['zip_code'],  # Zip Code
                                        node['info']['country'],  # Country
                                        node['url'],  # URL
                                        ', '.join(graph.neighbors(node_name))])  # Neighbors

                                elif node['object_type'] == 'CUSTOMER':
                                    num_neighbors = len(graph.neighbors(node_name))
                                    customer_writer.writerow([num_neighbors,  # Number of Neighbors
                                        node['name'],  # Name
                                        node['origin'],  # Origin
                                        ', '.join(node['sources']),  # Sources
                                        node_name,  # Handle
                                        node['info']['street'],  # Street
                                        node['info']['city'],  # City
                                        node['info']['state'],  # State
                                        node['info']['zip_code'],  # Zip Code
                                        node['info']['country'],  # Country
                                        node['url'],  # URL
                                        ', '.join(graph.neighbors(node_name))])  # Neighbors

                                elif node['object_type'] == 'ASN':
                                    num_neighbors = len(graph.neighbors(node_name))
                                    asn_writer.writerow([num_neighbors,  # Number of Neighbors
                                        node_name,  # ASN
                                        node['name'],  # Name
                                        node['info']['organization'],  # Organization
                                        node['origin'],  # Origin
                                        ', '.join(node['sources']),  # Sources
                                        node['url'],  # URL
                                        ', '.join(graph.neighbors(node_name))])  # Neighbors

                                elif node['object_type'] == 'POC':
                                    num_neighbors = len(graph.neighbors(node_name))
                                    poc_writer.writerow([num_neighbors,  # Number of neighbors
                                        node['name'],  # Name
                                        node['info']['email'],  # email
                                        node['origin'],  # Origin
                                        ', '.join(node['sources']),  # Sources
                                        node_name,  # Handle
                                        node['info']['street'],  # Street
                                        node['info']['city'],  # City
                                        node['info']['state'],  # State
                                        node['info']['zip_code'],  # Zip Code
                                        node['info']['country'],  # Country
                                        node['url'],  # URL
                                        ', '.join(graph.neighbors(node_name))])  # Neighbors


    with open('{}/{}_Companies.csv'.format(surfacediscovery['output dir'], company), 'w',
            newline='') as csvfile:
        company_writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                quoting=csv.QUOTE_MINIMAL)
        company_writer.writerow(['Company'])
        for company in companies:
            company_writer.writerow([company])




def write_json_output(company, graph, companies):
    pass


def write_output(company, graph, companies):
    if 'csv' in surfacediscovery['output']:
        write_csv_output(company, graph, companies)
    if 'json' in surfacediscovery['output']:
        write_json_output(company, graph, companies)



