import logging
import random
import re
import string
from abc import abstractmethod, ABC


class BindCensorer(ABC):
    def __init__(self,
                 conf_file=None,
                 template=string.Template('zone "$zone" {type master; file "db.aams"; };'),
                 spool_dir='/tmp',
                 name=None):
        """
        Constructor
        :param conf_file: bind config file for poisoning
        :param template: bind config string template line, param "zone" will be populated
        :param spool_dir: spool directory for lists download and manupulation
        :param name: name for this censorer (default random string)
        """
        self._observers = list()
        self.conf_file = conf_file
        f = open(self.conf_file, 'a')
        try:
            if not f.writable():
                raise PermissionError('config file %s not writable' % self.conf_file)
        finally:
            f.close()
        self.template = template
        if not name:
            self.name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
        else:
            self.name = name
        self.spool_dir = spool_dir
        f = open('%s/%s' % (self.spool_dir, self.name), 'a')
        try:
            if not f.writable():
                raise PermissionError('spool file %s not writable' % self.spool_dir)
        finally:
            f.close()
        self.__logger = logging.getLogger(__name__)

    def current_version(self):
        """
        Return current version
        :return: (serial, timestamp)
        """
        try:
            with open(self.conf_file, 'r') as f:
                firstline = f.readline().rstrip()
                match = re.search('\/\/SERIAL:(.*)\/\/TIMESTAMP:(.*)', firstline)
                if match:
                    return match.group(1), match.group(2)
            return 0, 0
        except FileNotFoundError:
            self.__logger.warning('%s Bind config file error' % self.name)
            return 0, 0

    def updated(self, version_tuple):
        """
        Compare version tuple with vcurrent version
        :param version_tuple:
        :return: true on changes
        """
        serial, ts = self.current_version()
        if serial == version_tuple[0] and ts == version_tuple[1]:
            return False
        else:
            return True

    def register_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, message):
        for observer in self._observers:
            observer.notify(self, message)

    def download_and_apply_if_updated(self):
        version = self.download()
        if version and self.updated(version):
            self.apply(version)

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def apply(self, version_tuple):
        pass

