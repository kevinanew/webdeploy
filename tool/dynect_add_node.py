#!/usr/bin/env python
"""
Dynect API SOAP Examples

Logs into the API, gets a session token, gets a list of all records at the 
root node by using the GetANYRecords command, and then logs out.
"""
import time
from pprint import PrettyPrinter
from optparse import OptionParser

import suds.client


pp = PrettyPrinter(indent=4)

# The path to the Dynect API WSDL file
base_url = 'https://api2.dynect.net/wsdl/current/Dynect.wsdl'

# Create a client instance
client = suds.client.Client(base_url)


def login(customer_name, user_name, password):
    response = client.service.SessionLogin(
        customer_name = customer_name,
        user_name = user_name,
        password = password,
        fault_incompat = 1,
    )
    
    if response.status != 'success':
        print "Login request failed!"
        pp.pprint(response)
        raise SystemExit
    
    token = response.data.token
    
    print "Token: %s" % token
    return token


def has_node(token, zone, domain):
    response = client.service.GetNodeList(
        token = token,
        zone = zone,
    )
    
    if response.status != 'success':
        print "Record request failed!"
        pp.pprint(response)
        raise SystemExit

    if domain in response.data:
        # make sure node isn't empty
        response = client.service.GetARecords(
            fqdn=domain,
            token=token,
            zone=zone,
        )
        
        if hasattr(response, 'data'):
            print "Already has this node", domain
            return True
        else:
            return False
    else:
        return False


def add_node(token, zone, domain, ip_address):
    response = client.service.CreateARecord(
        fqdn=domain,
        rdata={'address': ip_address},
        token=token,
        ttl=3600,
        zone=zone,
    )

    while response.status == "incomplete":
        time.sleep(1)

    if response.status != 'success':
        print "Record add request failed!"
        pp.pprint(response)
        raise SystemExit

    pp.pprint(response)
    print "add node %s -> %s" % (domain, ip_address)


def publish(token, zone):
    response = client.service.PublishZone(
        token=token,
        zone=zone,
    )
 
    if response.status != 'success':
        print "Publish Zone request failed!"
        pp.pprint(response)
        raise SystemExit
    print "Publish Zone:", zone


def log_out(token):
    response = client.service.SessionLogout(
        token = token,
        fault_incompat = 1,
    )
    
    if response.status != 'success':
        print "Logout request failed!"
        pp.pprint(response)
        raise SystemExit
    
    print "Successfully logged out"


def parse_args():
    parser = OptionParser()
    parser.add_option("-c", "--customer", dest="customer",
        help="dynect account's customer name")
    parser.add_option("-u", "--username", dest="username",
        help="dynect account's username")
    parser.add_option("-p", "--password", dest="password",
        help="dynect account's password")
    parser.add_option("-z", "--zone", dest="zone",
        help="zone you want to add in")
    parser.add_option("-d", "--domain", dest="domain",
        help="domain you want to add")
    parser.add_option("-i", "--ip_address", dest="ip_address",
        help="domain's ip address")

    (options, args) = parser.parse_args()
    
    return options

if __name__ == '__main__':
    parser = parse_args()

    token = login(parser.customer, parser.username, parser.password)
    if not has_node(token, parser.zone, parser.domain):
        add_node(token, parser.zone, parser.domain, parser.ip_address)
        publish(token, parser.zone)
    log_out(token)
