# DNS Censorer for Bind
A blacklist downloader and applier for ISC Bind DNS server

## Warning
This tool is under heavy development and untested in some of its parts.
Use it at your own risk.
Any form of contribution is welcome.

## Introduction
Italian authorities require ISPs obscure certain sites by blacklisting them on DNS.
This tool automates donwloading and appying blaclists, it can also send email for CNCPO
application, as rules requires.

## Bind Configuration
Bind must be configured by including a zone configuration file for every blacklist, for instance this is my named.conf contents:

    include "/etc/bind/named.conf.options";
    include "/etc/bind/named.conf.public";
    include "/etc/bind/named.conf.local";
    [..]
    include "/etc/dns_censorer/named.conf.cncpo"
    include "/etc/dns_censorer/named.conf.aams"
    [..]

Zone files must be also provided, see db.poison.example for an example

## Installation
TODO

## Configuration
See example.cfg

TODO
