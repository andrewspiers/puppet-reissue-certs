puppet-reissue-certs
====================
Reissue puppet certs, explore how fabric works.


Usage examples


$fab --set clientnode=hostname.example.com clean_puppet_cert
[root@puppet.example.com] Executing task 'clean_puppet_cert'
[root@puppet.example.com] run: puppet cert clean hostname.example.com
[root@puppet.example.com] out: err: Could not call revoke: Could not find a serial number for hostname.example.com

# get a list of nodes from the nonresponding nodes file,
#with correct username appended
$fab get_nodes:prepend_user=True

#check the puppet status of the nodes that are in the nodelist file.
#(ie is puppet running?)
$fab get_puppet_status


Example configuration file
==========================

[main]
domain: 'example.com'
puppetmaster: root@puppet.example.com
nodefile: non-reporting
puppetuser: root
