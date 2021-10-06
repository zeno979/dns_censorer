import logging
import smtplib
import string
import subprocess

from dns_censorer.cncpo import CNCPOBind


class CNCPOMailer:
    def __init__(self, smtp_server, sender, recipients, smtp_port=25,
                 subject='Applicazione lista inibizione CNCPO',
                 body='Una nuova lista inibitoria versione $version, timestamp $timestamp e\' stata correttamente applicata al DNS.\nCordiali saluti',
                 smtp_ssl=False, username=None, password=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender = sender
        self.subject = subject
        self.body = body
        self.recipients = recipients
        self.username = username
        self.password = password
        self.smtp_ssl = smtp_ssl
        self.__logger = logging.getLogger(__name__)

    def notify(self, source, version_tuple):
        if not isinstance(source, CNCPOBind):
            return
        try:
            if self.smtp_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.username:
                server.login(self.username, self.password)
            tpl = string.Template("From: %s\n\rTo: %s\n\rSubject: %s\n\r\n\r%s"
                                    % (self.sender, ", ".join(self.recipients), self.subject, self.body))
            message = tpl.substitute(version=version_tuple[0], timestamp=version_tuple[1])
            server.sendmail(self.sender, self.recipients, message)
            server.quit()
        except Exception as e:
            self.__logger.error(e)


class BindReloader:
    def __init__(self, rndc_key='/etc/bind/rndc.key', rndc_path='/usr/sbin/rndc'):
        self.__logger = logging.getLogger(__name__)
        self.rndc_key = rndc_key
        self.rndc_path = rndc_path

    def notify(self, source, version_tuple):
        self.__logger.info("Issuing Bind reload")
        subprocess.call([self.rndc_path, '-k', self.rndc_key, 'reload'])
