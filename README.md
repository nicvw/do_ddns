Digital Ocean DynDNS Script
===========================

Description
-----------
Dynamically update an 'A' or 'AAAA' record on a domain managed by Digital Ocean using their v2 API.  There are more complete packages and scripts out there for interacting with the Digital Ocean API, indeed there are other Digital Ocean dynamic DNS scripts too.  So why did I write my own, perhaps so I could reinvent a slightly less-round wheel?

Requirements
------------
It is also written for Python 3 only, because it is 2017 for goodness' sake.  For better or worse this script has some third-party package dependencies, namely:
 - requests
 - ipify

Usage
-----
The script requires three inputs, the domain being managed by Digital Ocean, the name of the record you with to create/update and your API access token available [here](https://cloud.digitalocean.com/settings/applications)

`python3 do_dns.py <domain> <record> <api-token>`

Example
-------
Should I wish to create/update the record for test.example.com

`python3 do_dns.py example.com test apitoken123qwe`
