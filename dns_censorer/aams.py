import hashlib
import logging
import string
import time
from string import Template

import requests

from dns_censorer.censorer import BindCensorer


_ZONE_TEMPLATE = Template('zone "$name" {type master; file "db.aams"; };')


class AAMSBind(BindCensorer):
    def __init__(self, url, url_checksum, conf_file=None,
                 template=string.Template('zone "$zone" {type master; file "db.aams"; };'),
                 spool_dir='/tmp', name=None):
        """
        Constructor
        :param url:
        :param url_checksum:
        :param conf_file:
        :param template:
        :param spool_dir:
        :param name:
        """
        super().__init__(conf_file, template, spool_dir, name)
        self.__logger = logging.getLogger(__name__)
        self.url = url
        self.url_checksum = url_checksum

    def download(self):
        """
        Download new file and verify hash
        :return:
        """
        r = requests.get(self.url, timeout=10, verify=False)
        if r.ok:
            with open('%s/%s' % (self.spool_dir, self.name), 'wb') as out:
                out.write(r.content)
            with open('%s/%s' % (self.spool_dir, self.name), 'rb') as file:
                file_content = file.read()
                file_hash = hashlib.sha256(file_content).hexdigest()
            r = requests.get(self.url_checksum, timeout=10, verify=False)
            if r.ok and r.text == file_hash:
                return file_hash, int(time.time())

    def apply(self, version_tuple):
        with open('%s/%s' % (self.spool_dir, self.name), 'r') as txt:
            lines = txt.readlines()
            with open(self.conf_file, 'w') as out:
                out.write('//SERIAL:%s//TIMESTAMP:%s\n' % version_tuple)
                for line in lines:
                    out.write(self.template.substitute(zone=line.rstrip()))
                    out.write('\n')
                self.notify_observers(version_tuple)

    def updated(self, version_tuple):
        """
        Compare version tuple with vcurrent version
        :param version_tuple:
        :return: true on changes
        """
        serial, ts = self.current_version()
        if serial == version_tuple[0]:
            return False
        else:
            return True