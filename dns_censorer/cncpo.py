import logging
import re
import string

import requests

from dns_censorer.censorer import BindCensorer


class CNCPOBind(BindCensorer):
    def __init__(self, certificate, key, url, conf_file=None,
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
            response = requests.get(self.url, cert=(self.certificate, self.key), timeout=10, verify=False)
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

    def apply(self, version_tuple):
        """
        Generate configuration from downloaded file
        :param version_tuple:
        :return:
        """
        with open('%s/%s' % (self.spool_dir, self.name), 'r') as csv:
            lines = csv.readlines()
            lines.pop(0)
            self.__logger.info("Applying %s version %s" % (self.name, version_tuple[0]))
            with open(self.conf_file, 'w') as out:
                out.write('//SERIAL:%s//TIMESTAMP:%s\n' % version_tuple)
                for line in lines:
                    parts = line.split(';')
                    zone = parts[1].strip()
                    out.write(self.template.substitute(zone=zone))
                    out.write('\n')
            self.notify_observers(version_tuple)
