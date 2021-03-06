#!/usr/bin/python

#TODO: make a task which calls puppet cert {list,clean,sign}, and convert
#      the existing list_puppet_cert and clean_puppet_cert into wrappers.

import get_unreported

from fabric.api import env, hosts, run, settings, task

import ConfigParser
import os

try:
  configfile = os.environ['PUPPET-REISSUE-CERTS-RC']
except KeyError:
  configfile = 'puppet-reissue-certs.conf'

config = ConfigParser.SafeConfigParser()
config.read(configfile)


nodefile = config.get('main','nodefile')

env.roledefs['puppetmaster'] = config.get('main','puppetmaster')
puppetuser = config.get('main','puppetuser')

@task
def get_nodes(filename=nodefile, prepend_user=False, user=puppetuser):
  """given a file name, return a list of the nodes in that file.
  prepend 'puppetuser@' to each node name. 'puppetuser' should be root.
  """
  out = list()
  with open (filename, 'r') as f:
    for line in f:
      if len(line) > 1:
        if '@' not in line and prepend_user:
          out.append(user + '@' + line.split(',')[0])
        else:
          out.append(line.split(',')[0])
  return out

@task
def get_unreported_nodes(prepend_user=True, user=puppetuser):
  """use get_unreported.py to scrape the puppet dashboard to find those nodes
  that are not reporting, return a list of them, if prepend_user, then
  return the list as a list that can be used as connection strings by fabric.
  """
  unreported = get_unreported.get_unreported()
  out = list()
  if prepend_user and len(unreported) > 0:
    for i in unreported:
      out.append(user + '@' + i)
  else:
    out = unreported
  return out


@task
@hosts(get_nodes(prepend_user=True))
def get_puppet_status(user=puppetuser):
  """Log into hosts from the pre-existing list of files in the nodefile,
  and check that the puppet service is running."""
  with settings(warn_only=True):
    run('service puppet status')

@task
@hosts(get_unreported_nodes())
def get_puppet_status2(user=puppetuser):
  """Log into those nodes that the puppet dashboard reports as unreported,
  and check that the puppet service is running."""
  with settings(warn_only=True):
    run('service puppet status')

@task
def remove_puppet_ssl():
  """Remove puppet /var/lib/ssl for a node, then rerun puppet to generate
  a new certificate and submit it for signing."""
  #settings imported from fabric.api. Do not abort on nonzero exit status.
  with settings(warn_only=True):
    #run imported from fabric.api
    run('service puppet stop')
    run('killall puppet')
    run('rm -rf /var/lib/puppet/ssl')
    run('puppet agent -t')

@task
@hosts(env.roledefs['puppetmaster'])
def list_puppet_cert(qn=None):
  """Run 'puppet cert list $querynode' on the puppetmaster 
  querynode could/should be defined in the commmand line like
  fab --set querynode=host.example.com list_puppet_cert
  """
  if qn is None:
    qn = env.querynode
  command = "puppet cert list " + qn
  run(command)

@task
@hosts(env.roledefs['puppetmaster'])
def list_all_certs():
  """do puppet cert list X, for X in get_nodes()
  (which reads the nodes in from a file)"""
  for n in get_nodes():
    list_puppet_cert(n)

@task
@hosts(env.roledefs['puppetmaster'])
def clean_puppet_cert(client=None):
  """clean client's certificate from the puppetmaster
  'fab --set clientnode=host.example.com clean_puppet_cert should
  run 'puppet cert clean host.example.com on the puppetmaster'.
  """
  if client is None:
    client = env.clientnode
  command = "puppet cert clean " + client
  run(command)
  pass

def main():
  print (get_nodes())

if __name__ == "__main__":
  main()
