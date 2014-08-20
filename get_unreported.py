# -*- coding: utf-8 -*-
"""
get_unreported.py

scrape the puppet dashboard to find the nodes that have
not recently reported to the puppetmaster.
"""

# <codecell>

import requests
from bs4 import BeautifulSoup

import ConfigParser
import os
import sys

# <codecell>

class netrc_credential(object):
    def __init__(self,machine):
        netrc_file = os.path.join((os.environ['HOME']),'.netrc')
        with open(netrc_file,'r') as f:
            for line in f:
                words = line.split()
                if words[0:2] == ['machine',machine]:
                    if words[2] == 'login' and words[4] == 'password':
                        self.login = words[3]
                        self.password = words[5]
                        break
            try:
                self.login
                self.password
            except NameError:
                message = " ".join("Could not find login and password entries for",
                                   machine,
                                   "in your .netrc file.")
                sys.stderr.write(message)
                sys.stderr.flush()
                sys.exit(1)

# <codecell>

def getnode():
  """return then name of the puppet master, from reading the config file"""
  try:
    configfile = os.environ['GET-UNREPORTED-RC']
  except KeyError:
    configfile = 'puppet-reissue-certs.conf'
  config = ConfigParser.SafeConfigParser()
  config.read(configfile)
  puppetmaster_connection = config.get('main','puppetmaster')
  if '@' in puppetmaster_connection:
    puppetmaster = puppetmaster_connection.split('@')[1]
  else:
    puppetmaster = puppetmaster_connection
  return puppetmaster


def main():
  protocol = 'https:/'
  node = getnode()
  slug = 'nodes/unreported.csv'
  url = '/'.join((protocol,node,slug))
  r = requests.get(url,verify=False)
  soup = BeautifulSoup(r.text)
  forms = soup.findAll('form')
  if not (forms[0].attrs['action'] == "/idp/Authn/UserPassword" and forms[0].attrs['method'] == "post"):
      sys.stderr.write("unexpected response received\n")
      sys.stderr.flush()
      print("unexpected response received\n")
      print forms[0]
      print forms[0].attrs
  else:
      credential = netrc_credential(node)
      #http://www.python-requests.org/en/latest/user/quickstart/#more-complicated-post-requests
      payload = { 'j_username':credential.login, 'j_password':credential.password}
      r2_url = r.url
      r2 = requests.post(r2_url,data=payload,verify=False,cookies=r.cookies)
      soup2 = BeautifulSoup(r2.text)
      soup2forms = soup2.findAll('form')
      soup2inputs = soup2.findAll('input')
      r3url = soup2forms[0].attrs['action']
      inputs = soup2.findAll('input')
      r3payload = dict()
      for i in inputs:
          if i.attrs['type'] == 'hidden':
              r3payload[i.attrs['name']] = i.attrs['value']
      r3 = requests.post(r3url,data=r3payload,verify=False,cookies=r2.cookies)
      soup3 = BeautifulSoup(r3.text)


  unreportedcsv = soup3.find('p').text.split()[1:]
  #only need the first column
  unreported = [x.split(',')[0] for x in unreportedcsv]
  print unreported


if __name__ == "__main__":
  main()
