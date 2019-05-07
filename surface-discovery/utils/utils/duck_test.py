import logging
from utils.conf import surfacediscovery



def whois_customer(customer, name, street, city, state, zip_code):
    """
    Returns whether or not this company should be included in results

    This function compares the object to a global list of elements that should be compared.

    Arguments:
        parameter name: The name of the customer that is being tested
            precondition: name is a string
        parameter street: The street address of the customer that is being tested
            precondition: street is a string
        parameter city: The city of the cusotmer that is being tested
            precondition: city is a string
        parameter state: The state of the customer that is being tested
            precondition: state is a string
        parameter zip_code: The zip/postal code of the customer that is being tested
            precondition: zip_code is a string
    """
    if surfacediscovery['duck_test_accuracy'] == 0:
        logging.info('{0: <8} {1: <12}: Threshold is 0'.format('Customer', customer))
        return True

    score = 0
    items_checked = 0
    valid_items = []

    # Check name
    if name != '':
        name = name.title()
        items_checked += 1
        if surfacediscovery['company'] in name:
            valid_items.append('name')
            score += 1
        else:
            for alias in surfacediscovery['profile']['aliases']:
                if alias in name:
                    valid_items.append('name')
                    score += 1
                    break

    # Check street
    if street != '':
        street = street.title()
        items_checked += 1
        for drive in surfacediscovery['profile']['addresses']['streets']:
            if drive in street:
                valid_items.append('street')
                score += 1
                break
    # Check city
    if city != '':
        city = city.title()
        items_checked += 1
        for town in surfacediscovery['profile']['addresses']['cities']:
            if town in city:
                valid_items.append('city')
                score += 1
                break
    # Check state
    if state != '':
        state = state.upper()
        items_checked += 1
        for province in surfacediscovery['profile']['addresses']['states']:
            if state in province:
                valid_items.append('state')
                score += 1
                break
    # Check zip code
    if zip_code != '':
        items_checked += 1
        for postal_code in surfacediscovery['profile']['addresses']['zip codes']:
            if postal_code in zip_code:
                valid_items.append('zip_code')
                score += 1
                break

    # Log what was valid
    if len(valid_items) == 1:
        logging.info('{0: <8} {1: <12}: {2} is valid'.format('Customer', customer, valid_items[0]))
    elif len(valid_items) > 1:
        valid_items.insert(-1, 'and')
        message = ' '.join(valid_items)
        logging.info('{0: <8} {1: <12}: {2} are all valid'.format('Customer', customer, message))
    else:
        logging.info('{0: <8} {1: <12}: nothing is valid'.format('Customer', customer))


    # Divide & return
    if items_checked > 0:
        rating = score / items_checked

        return (rating > surfacediscovery['duck_test_accuracy'])
    else:
        return True


def whois_poc(poc, name, street, city, state, zip_code, email):
    """
    Returns whether or not this company should be included in results

    This function compares the object to a global list of elements that should be compared.

    Arguments:
        parameter name: The name of the customer that is being tested
            precondition: name is a string
        parameter street: The street address of the customer that is being tested
            precondition: street is a string
        parameter city: The city of the cusotmer that is being tested
            precondition: city is a string
        parameter state: The state of the customer that is being tested
            precondition: state is a string
        parameter zip_code: The zip/postal code of the customer that is being tested
            precondition: zip_code is a string
        parameter email: The email address of the customer that is being tested
            precondition: email is a string
    """
    if surfacediscovery['duck_test_accuracy'] == 0:
        logging.info('{0: <8} {1: <12}: Threshold is 0'.format('POC', poc))
        return True

    score = 0
    items_checked = 0
    valid_items = []

    # Check name
    if name != '':
        name = name.title()
        items_checked += 1
        if surfacediscovery['company'] in name:
            valid_items.append('name')
            score += 1
        else:
            for alias in surfacediscovery['profile']['aliases']:
                if alias in name:
                    valid_items.append('name')
                    score += 1
                    break

    # Check street
    if street != '':
        street = street.title()
        items_checked += 1
        for drive in surfacediscovery['profile']['addresses']['streets']:
            if drive in street:
                valid_items.append('street')
                score += 1
                break
    # Check city
    if city != '':
        city = city.title()
        items_checked += 1
        for town in surfacediscovery['profile']['addresses']['cities']:
            if town in city:
                valid_items.append('city')
                score += 1
                break
    # Check state
    if state != '':
        state = state.upper()
        items_checked += 1
        for province in surfacediscovery['profile']['addresses']['states']:
            if state in province:
                valid_items.append('state')
                score += 1
                break
    # Check zip code
    if zip_code != '':
        items_checked += 1
        for postal_code in surfacediscovery['profile']['addresses']['zip codes']:
            if postal_code in zip_code:
                valid_items.append('zip_code')
                score += 1
                break
    # Check email
    if email != '':
        items_checked += 1
        domain = email[email.find('@') + 1:]
        if domain in surfacediscovery['profile']['website']:
            valid_items.append('email')
            score += 1

    # Log what was valid
    if len(valid_items) == 1:
        logging.info('{0: <8} {1: <12}: {2} is valid'.format('POC', poc, valid_items[0]))
    elif len(valid_items) > 1:
        valid_items.insert(-1, 'and')
        message = ' '.join(valid_items)
        logging.info('{0: <8} {1: <12}: {2} are all valid'.format('POC', poc, message))
    else:
        logging.info('{0: <8} {1: <12}: nothing is valid'.format('POC', poc))

    # Divide & return
    if items_checked > 0:
        rating = score / items_checked

        return (rating > surfacediscovery['duck_test_accuracy'])
    else:
        return True


def whois_org(org, name, street, city, state, zip_code):
    """
    Returns whether or not this company should be included in results

    This function compares the object to a global list of elements that should be compared.

    Arguments:
        parameter name: The name of the customer that is being tested
            precondition: name is a string
        parameter street: The street address of the customer that is being tested
            precondition: street is a string
        parameter city: The city of the cusotmer that is being tested
            precondition: city is a string
        parameter state: The state of the customer that is being tested
            precondition: state is a string
        parameter zip_code: The zip/postal code of the customer that is being tested
            precondition: zip_code is a string
    """
    if surfacediscovery['duck_test_accuracy'] == 0:
        logging.info('{0: <8} {1: <12}: Threshold is 0'.format('ORG', org))
        return True

    score = 0
    items_checked = 0
    valid_items = []

    # Check name
    if name != '':
        name = name.title()
        items_checked += 1
        if surfacediscovery['company'] in name:
            valid_items.append('name')
            score += 1
        else:
            for alias in surfacediscovery['profile']['aliases']:
                if alias in name:
                    valid_items.append('name')
                    score += 1
                    break

    # Check street
    if street != '':
        street = street.title()
        items_checked += 1
        for drive in surfacediscovery['profile']['addresses']['streets']:
            if drive in street:
                valid_items.append('street')
                score += 1
                break
    # Check city
    if city != '':
        city = city.title()
        items_checked += 1
        for town in surfacediscovery['profile']['addresses']['cities']:
            if town in city:
                valid_items.append('city')
                score += 1
                break
    # Check state
    if state != '':
        state = state.upper()
        items_checked += 1
        for province in surfacediscovery['profile']['addresses']['states']:
            if state in province:
                valid_items.append('state')
                score += 1
                break
    # Check zip code
    if zip_code != '':
        items_checked += 1
        for postal_code in surfacediscovery['profile']['addresses']['zip codes']:
            if postal_code in zip_code:
                valid_items.append('zip_code')
                score += 1
                break

    # Log what was valid
    if len(valid_items) == 1:
        logging.info('{0: <8} {1: <12}: {2} is valid'.format('ORG', org, valid_items[0]))
    elif len(valid_items) > 1:
        valid_items.insert(-1, 'and')
        message = ' '.join(valid_items)
        logging.info('{0: <8} {1: <12}: {2} are all valid'.format('ORG', org, message))
    else:
        logging.info('{0: <8} {1: <12}: nothing is valid'.format('ORG', org))

    # Divide & return
    if items_checked > 0:
        rating = score / items_checked

        return (rating > surfacediscovery['duck_test_accuracy'])
    else:
        return True


def whois_asn(asn, name, organization, valid_orgs):
    """
    Returns whether or not this company should be included in results

    This function compares the object to a global list of elements that should be compared.

    Arguments:
        parameter name: The name of the customer that is being tested
            precondition: name is a string
        parameter organization: The organization code of the ASN being tested
            precondition: organization is a string
        parameter valid_orgs: A list of organizations that passed the duck test
            precondition: valid_orgs is a list of strings
    """
    if surfacediscovery['duck_test_accuracy'] == 0:
        logging.info('{0: <8} {1: <12}: Threshold is 0'.format('ASN', asn))
        return True

    score = 0
    items_checked = 0
    valid_items = []

    # Check name
    if name != '':
        name = name.title()
        items_checked += 1
        if surfacediscovery['company'] in name:
            valid_items.append('name')
            score += 1
        else:
            for alias in surfacediscovery['profile']['aliases']:
                if alias in name:
                    valid_items.append('name')
                    score += 1
                    break
    if organization != '':
        organization = organization.title()
        if organization in valid_orgs:
            return True

    # Log what was valid ASN
    if len(valid_items) == 1:
        logging.info('{0: <8} {1: <12}: {2} is valid'.format('ASN', asn, valid_items[0]))
    elif len(valid_items) > 1:
        valid_items.insert(-1, 'and')
        message = ' '.join(valid_items)
        logging.info('{0: <8} {1: <12}: {2} are all valid'.format('ASN', asn, message))
    else:
        logging.info('{0: <8} {1: <12}: nothing is valid'.format('ASN', asn))

    # Divide & return
    if items_checked > 0:
        rating = score / items_checked

        return (rating > surfacediscovery['duck_test_accuracy'])
    else:
        return True



def whois_ip(ip, organization, valid_orgs):
    """
    Returns whether or not this company should be included in results

    This function compares the object to a global list of elements that should be compared.

    Arguments:
        parameter organization: The organization code of the ASN being tested
            precondition: organization is a string
        parameter valid_orgs: A list of organizations that passed the duck test
            precondition: valid_orgs is a list of strings
    """
    if surfacediscovery['duck_test_accuracy'] == 0:
        logging.info('{0: <8} {1: <12}: Threshold is 0'.format('IP', ip))
        return True

    if organization != '':
        if organization in valid_orgs:
            return True
    return True



def tcpip_utils_duck_test():  # TODO
    """
    Returns whether or not this company should be included in results

    This function compares the object to a global list of elements that should be compared.

    Arguments:
    """
    return True


def domains_clearbit(clearbit_dict='', duck_test_object=''):
    """
    Returns the value of the boolean statment "This clearbit result for the target company"

    This function compares the clearbit_dict and the duck_test_object to determine the accuracy of
    this result.

    Arguments:
        parameter clearbit_dict: The clearbit object to compare
            precondition: clearbit_dict is a dictionary representing a clearbit result object
        parameter duck_test_object: The duck test object to compare
            precondition: duck_test_object is a duck test obejct
    """

    """
    The clearbit_dict has keynames mapped to types:
        category: dict
            industry: string
            industryGroup: string
            naicsCode: string
            sector: string
            sicCode: string
            subIndustry: string
        crunchbase: dict
            handle: string
        description: string
        domain: string
        domainAliases: list of strings
        emailProvider: ? if null, holds value False>
        facebook: dict
            handle: ?
            likes: ?
        foundedYear: num
        geo: dict
            city: string
            country: string
            countryCode: string
            lat: num
            lng: num
            postalCode: string
            state: string
            stateCode: string
            streetName: string
            streetNumber: string
            subPremise: ?
        id: string
        indexedAt: string
        legalName: string
        linkedin: dict
            handle: string
        location: string
        logo:   string (link to logo)
        metrics: dict
            alexaGlobalRank: num
            alexaUsRank: num
            annualRevenue: num
            employees: num
            employeesRange: string
            fiscalYearEnd: num
            googleRank: num
            marketCap: num
            raised: ?
        name: string
        phone: string
        similarDomains: list of strings
        site: dict
            emailAddresses: list of strings
            h1: string
            metaAuthor: string
            metaDescription: string
            phoneNumbers: list of strings
            title: string
        tags: list of strings
        tech: list of strings
        ticker: string
        timeZone: string
        twitter: dict
            avatar: string
            bio: string
            followers: num
            following: num
            handle: string
            id: string
            location: string
            site: string
        type: string
        utcOffset: num
    """

    # num_same = 0
    # num_compared = 0
    # Check each parameter in the object against the duck test object, and then see what
    #  percent is the same. That value is greater than the duck_test_accuracy, this object
    #  is the same.



    # return ((num_same / num_compared) > surfacediscovery['duck_test_accuracy'])
    return True


