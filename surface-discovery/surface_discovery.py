#! /usr/bin/env python3

import logging
import networkx
import time
from core import arin
from utils.conf import surfacediscovery
# from utils import acquisitions
from utils import asns
from utils import domains
from utils import output


def main():
    """
    function main(): The driving force behind the program

    This function runs the actual script. It first creates arguments and attempts to get them. If
    they are not present, it will create a prompt for the user. It then follows the general flow of
    the program. It first attempts to get all acquisitions, then gets domains and hosts while also
    searching through WHOIS, TCPIP Utils and The BGP Toolkit.

    Arguments:
        None
    """
    # Begin timing
    start_time = time.time()

    # Configure Logging
    logging.basicConfig(filename=surfacediscovery['logs']['log_file'],
            level=surfacediscovery['logs']['log_level'],
            format='%(message)s')
    logging.getLogger("requests").setLevel(logging.WARNING)

    # Initialize company search list, and main company name
    company_search_dict = dict((alias, True) for alias in surfacediscovery['profile']['aliases'])
    main_company = ''
    # Check the company domain and get its legal name
    if surfacediscovery['profile']['website']:
        company_name = domains.clearbit_company(surfacediscovery['profile']['website'])
        if company_name != '':
            company_search_dict[company_name] = True
            main_company = company_name
    if surfacediscovery['company']:
        company_search_dict[surfacediscovery['company']] = True
        main_company = surfacediscovery['company']
    if not company_search_dict:
        logging.info('We need a name, or a domain to search for, and were unable to find a name for\
                the specified information!')
        return

    graph = networkx.Graph()

    # Search through Crunchbase
    # company_list = acquisitions.crunchbase_main(company_search_dict)
    # company_list += company_search_dict.keys()
    # company_list = ['MindMeld', 'Saggezza', 'Viptela', 'AppDynamics', 'Worklife', 'ContainerX', 'CloudLock', 'Synata', 'Leaba Semiconductor', 'CliQr Technologies', 'Jasper Technologies', 'Acano Limited', 'Mainstream', 'Lancope', 'ParStream', 'Portcullis', 'Pawaa', 'MaintenanceNet', 'OpenDNS', 'Piston Cloud Computing', 'Tropo', 'Embrane', 'Neohapsis', 'Memoir Systems', 'Metacloud', 'Assemblage', 'Tail-f Systems', 'ThreatGRID', 'Collaborate.com', 'WHIPTAIL', 'Sourcefire', 'Composite Software', 'JouleX', 'Ubiquisys', 'SolveDirect', 'Cognitive Security', 'Intucell', 'BroadHop', 'Cariden Technologies', 'Meraki', 'Cloupia', 'vCider', 'ThinkSmart Technologies', 'Virtuata', 'Truviso', 'ClearAccess', 'NDS Group Ltd.', 'Lightwire', 'BNI Video', 'Versly', 'AXIOSS Software and Talent', 'newScale', 'Inlet Technologies', 'Pari Networks', 'LineSider Technologies', 'Set-Top Box Business of DVN (Holdings) Ltd.', 'ScanSafe', 'Starent Networks', 'Tandberg', 'Tidal Software', 'Pure Digital Technologies', 'Richards-Zeta Building Intelligence', 'Jabber', 'PostPath', 'WebEx Communications', 'NeoPath Networks', 'IronPort Systems', 'Greenfield Networks', 'Orative', 'Arroyo Video Solutions', 'Meetinghouse Data Communications', 'Metreos', 'Audium', 'SyPixx Networks', 'Intellishield Alert Manager', 'Scientific-Atlanta', 'Sipura Technology', 'Topspin Communications', 'Protego Networks', 'BCN Systems', 'Jahi Networks', 'Perfigo', 'dynamicsoft', 'NetSolve', 'P-Cube', 'Parc Technologies, Ltd.', 'Actona Technologies', 'Procket Network', 'Riverhead Networks', 'Twingo Systems', 'Latitude Communications', 'Linksys Group', 'SignalWorks', 'Okena', 'Psionic Software', 'Hammerhead Networks', 'AuroraNetics', 'Active Voice', 'CAIS Software Solutions', 'PixStream', 'IPmobile', 'NuSpeed Internet Systems', 'Komodo Tehnology', 'Netiverse, Ltd.', 'HyNEX, Ltd.', 'ArrowPoint Communications', 'Seagull Semiconductor, Ltd.', 'PentaCom Ltd.', 'SightPath', 'infoGear Technology', 'JetCell', 'Growth Networks', 'Altiga Networks', 'Compatible Systems', 'Pirelli Optical Systems', 'Internet Engineering Group', 'Worldwide Data Systems', 'V-Bits', 'Aironet Wireless Communications', 'Tasmania Network Systems', 'Cocom A/S', 'Cerent', 'Monterey Networks', 'MaxComm Technologies', 'Calista', 'StratumOne Communications', 'TransMedia Communications', 'Amteva Technologies', 'GeoTel Communications', 'Fibex Systems', 'Pipelinks', 'Selsius Systems', 'American Internet', 'Summa Four', 'CLASS Data Systems', 'Precept Software', 'NetSpeed', 'WheelGroup', 'LightSpeed International', 'Dagaz (Integrated Network', 'Ardent Communications', 'SkyStone Systems', 'Telesend', 'Metaplex', 'TGV Software', 'Internet Junction', 'Kalpana', 'Crescendo Communications']
    company_list = ['Anthem']
    # Invariant: We have found every acquisition (Assuming we didn't hit a distil firewall)

    # Search through clearbit to find all domains
    domain_dict = domains.clearbit_domains(company_list)
    for domain, companies in domain_dict.items():
        if graph.has_node(domain):
            graph.node[domain]['sources'].add('Clearbit')
        else:
            graph.add_node(domain, origin='Clearbit found the domain in a search for {}'.format(
                ', '.join(companies)), sources=set(['Clearbit']),
                    name=domain, visited=[], object_type='DOMAIN',
                    url=domain)

    # Search through Potaroo to find all ASNs
    asn_dict = asns.potaroo_asns(company_list)
    for asn, asn_tuple in asn_dict.items():
        if graph.has_node(asn):
            graph.node[asn]['sources'].add('Potaroo')
        else:
            graph.add_node(asn, origin='Potaroo found the domain in a search for {}'.format(
                ', '.join(asn_tuple[1])), sources=set(['Potaroo']),
                    name=asn_tuple[0], visited=[], object_type='ASN', url='')


    # Work on the core

    # Create the list of things to search for
    company_search_set = set(company_list)
    arin_searched = set()

    repeat = True
    logging.info('Beginning the core')
    while repeat:
        repeat = False

        # ARIN
        arin_sent = graph.number_of_nodes()
        graph = arin.whois_arin_main(graph, company_search_set, arin_searched)
        arin_received = graph.number_of_nodes()
        repeat = repeat or arin_received > arin_sent


    # Do something with the output
    output.write_output(main_company, graph, company_list)

    logging.info('Running for {} took {} seconds'.format(main_company, time.time() - start_time))
    return graph


if __name__ == '__main__':
    main()

