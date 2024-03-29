import logging
import re
import string

import requests

from dns_censorer.censorer import BindCensorer


class CNCPOBind(BindCensorer):
    def __init__(self, url, certificate=None, key=None,  conf_file=None,
                 template=string.Template('zone "$zone" {type master; file "db.cncpo"; };'),
                 spool_dir='/tmp', name=None):
        """
        Constructor
        :param certificate: client certificate
        :param key: private key
        :param url:
        :param conf_file:
        :param template:
        :param spool_dir:
        :param name:
        """
        self.certificate = certificate
        self.key = key
        self.url = url
        self.__logger = logging.getLogger(__name__)
        super().__init__(conf_file, template, spool_dir, name)

    def download(self):
        """
        Download CNCPO DB
        :return: (version, timestamp)
        """
        try:
            if self.certificate:
                self.__logger.info("Trying certificate authentication on %s" % self.url)
                response = requests.get(self.url, cert=(self.certificate, self.key), timeout=10, verify=False)
            else:
                self.__logger.info("Trying anonymous download from %s" % self.url)
                response = requests.get(self.url, timeout=10, verify=False)
        except requests.exceptions.RequestException as e:
            self.__logger.warning("%s Download exception: %s" % (self.name, e))
            return None
        if response.ok:
            with open('%s/%s' % (self.spool_dir, self.name), 'w') as out:
                out.write(response.text)
            with open('%s/%s' % (self.spool_dir, self.name), 'r') as csv:
                line = csv.readline()
                match = re.search('^\s*(\d+)\s*;\s*(\d+)\s*;', line)
                if match:
                    return match.group(1), match.group(2)
                else:
                    self.__logger.warning('%s file format error' % self.name)
        else:
            self.__logger.warning('%s Download issue: %s' % (self.name, response.text))

    def apply(self, version_tuple, ignored_zones=None):
        """
        Generate configuration from downloaded file
        :param version_tuple:
        :param ignored_zones:
        :return:
        """
        if ignored_zones is None:
            ignored_zones = list()
        zones = list()
        with open('%s/%s' % (self.spool_dir, self.name), 'r') as csv:
            lines = csv.readlines()
            lines.pop(0)
            self.__logger.info("Applying %s version %s" % (self.name, version_tuple[0]))
            with open(self.conf_file, 'w') as out:
                out.write('//SERIAL:%s//TIMESTAMP:%s\n' % version_tuple)
                for line in lines:
                    parts = line.split(';')
                    zone = parts[1].strip()
                    if zone and zone not in zones and zone not in ignored_zones:
                        zones.append(zone)
                        self.__logger.info("Adding zone %s for %s" % (zone, self.name))
                    else:
                        self.__logger.info("Skipping zone %s for %s" % (zone, self.name))
                for zone in zones:
                    out.write(self.template.substitute(zone=zone))
                    out.write('\n')
            self.notify_observers(version_tuple)
        self.zones = zones
