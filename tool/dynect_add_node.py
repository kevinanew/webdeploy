#!/usr/bin/env python
"""
Dynect command for add node
"""
import time
from pprint import PrettyPrinter
from optparse import OptionParser

import suds.client


class DynectAddNode(object):
    printer = PrettyPrinter(indent=4)
    
    # The path to the Dynect API WSDL file
    base_url = 'https://api2.dynect.net/wsdl/current/Dynect.wsdl'
    
    def __init__(self):
        self.client = suds.client.Client(self.base_url)
        self.token = None

    def login(self, customer_name, user_name, password):
        response = self.client.service.SessionLogin(
            customer_name=customer_name,
            user_name=user_name,
            password=password,
            fault_incompat=1,
        )

        if response.status != 'success':
            print "Login request failed!"
            self.printer.pprint(response)
            raise SystemExit
        
        self.token = response.data.token
        
        print "Token: %s" % self.token

    def has_node(self, zone, domain):
        response = self.client.service.GetNodeList(
            token=self.token,
            zone=zone,
        )
        
        if response.status != 'success':
            print "Record request failed!"
            self.printer.pprint(response)
            raise SystemExit
    
        if domain in response.data:
            # make sure node isn't empty
            response = self.client.service.GetARecords(
                fqdn=domain,
                token=self.token,
                zone=zone,
            )
            
            if hasattr(response, 'data'):
                print "Already has this node", domain
                return True
            else:
                return False
        else:
            return False
    
    
    def add_node(self, zone, domain, ip_address):
        print zone
        print domain
        response = self.client.service.CreateARecord(
            fqdn=domain,
            rdata={'address': ip_address},
            token=self.token,
            ttl=3600,
            zone=zone,
        )
    
        while response.status == "incomplete":
            time.sleep(1)
    
        if response.status != 'success':
            print "Record add request failed!"
            self.printer.pprint(response)
            raise SystemExit
    
        self.printer.pprint(response)
        print "add node %s -> %s" % (domain, ip_address)
    
    
    def publish(self, zone):
        response = self.client.service.PublishZone(
            token=self.token,
            zone=zone,
        )
     
        if response.status != 'success':
            print "Publish Zone request failed!"
            self.printer.pprint(response)
            raise SystemExit
        print "Publish Zone:", zone
    
    
    def log_out(self):
        response = self.client.service.SessionLogout(
            token=self.token,
            fault_incompat=1,
        )

        if response.status != 'success':
            print "Logout request failed!"
            self.printer.pprint(response)
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

    dynect_add_node = DynectAddNode()
    dynect_add_node.login(parser.customer, parser.username, parser.password)
    if not dynect_add_node.has_node(parser.zone, parser.domain):
        dynect_add_node.add_node(parser.zone, parser.domain, parser.ip_address)
        dynect_add_node.publish(parser.zone)
    dynect_add_node.log_out()
