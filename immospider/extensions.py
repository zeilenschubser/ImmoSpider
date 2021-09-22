try:
    import sendgrid
    from sendgrid.helpers.mail import *
except:
    sendgrid = None
try:
    #!/usr/bin/python3
    from envelopes import Envelope, SMTP
except:
    Envelope, SMTP = None, None
import os
import logging
from scrapy import signals


logger = logging.getLogger(__name__)

if sendgrid and 'SENDGRID_API_KEY' in os.environ:
    class SendMail(object):

        def __init__(self, fromaddr, to, sendgrid_key):
            self.fromaddr = fromaddr
            self.toaddr = to
            self.sendgrid_key = sendgrid_key
            self.items = []

        @classmethod
        def from_crawler(cls, crawler):

            settings = crawler.settings
            fromaddr = settings.get("FROM")
            toaddr = settings.get("TO")
            sendgrid_key = settings.get("SENDGRID_API_KEY")

            ext = cls(fromaddr, toaddr, sendgrid_key)

            crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
            crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)

            return ext

        def spider_closed(self, spider):

            if len(self.items) > 0:

                sg = sendgrid.SendGridAPIClient(self.sendgrid_key)

                from_email = Email(self.fromaddr)
                to_email = Email(self.toaddr)
                subject = "New Items from Immospider"

                # message = "Hi there,\r\n\r\nhere are all new items from Immospider:\r\n"
                # message += "\r\n".join([str(item["url"]) +" "+ str(item["rent"]) +"€ "+ str(item["title"]) for item in sorted(self.items, key = lambda item: float(item["rent"]), reverse=True)])
                # # for pure plain text messages one has to deactivate auto-convert to html in sendgrid mail settings
                # # https://github.com/sendgrid/sendgrid-nodejs/issues/623
                # content = Content("text/plain", message)

                html = "Hi there,<br /><br />here are all new items from Immospider:<br />"
                html += "<br />".join(
                    ["<a href=\"" + str(item["url"]) + "\">" + str(item["rent"]) + "€ " + str(item["title"]) + "</a>" for
                     item in sorted(self.items, key=lambda item: float(item["rent"]), reverse=True)])

                content = Content("text/html", html)

                mail = Mail(from_email, subject, to_email, content)

                response = sg.client.mail.send.post(request_body=mail.get())
                logger.info(response.status_code)
                logger.info(response.body)
                logger.info(response.headers)
            else:
                logger.info("No new items found. No email sent.")

        def item_scraped(self, item, spider):
            self.items.append(item)

elif Envelope and SMTP and 'SMTP_MAIL_HOST' in os.environ:
    class SendMail(object):

        def __init__(self, fromaddr, to, sendgrid_key):
            self.fromaddr = fromaddr
            self.toaddr = to
            self.items = []

        @classmethod
        def from_crawler(cls, crawler):

            settings = crawler.settings
            fromaddr = settings.get("FROM")
            toaddr = settings.get("TO")

            ext = cls(fromaddr, toaddr, "")

            crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
            crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)

            return ext

        def spider_closed(self, spider):

            if len(self.items) > 0:

                smtp = SMTP(host=os.environ['SMTP_MAIL_HOST'], 
                             port=int(os.environ['SMTP_MAIL_PORT']),
                             login=os.environ['SMTP_MAIL_USER'], 
                             password=os.environ['SMTP_MAIL_PASS'],
                             tls=True, # no tls means you're beyond the line
                             timeout=None
                            )

                from_email = Email(self.fromaddr)
                to_email = Email(self.toaddr)
                subject = "New Items from Immospider"

                html = "Hi there,<br /><br />here are all new items from Immospider:<br />"
                html += "<br />".join(
                    ["<a href=\"" + str(item["url"]) + "\">" + str(item["rent"]) + "€ " + str(item["title"]) + "</a>" for
                     item in sorted(self.items, key=lambda item: float(item["rent"]), reverse=True)])

                content = Content("text/html", html)

                mail = Mail(from_email, subject, to_email, content)
                envelope = Envelope(
                    from_addr=(os.environ['SMTP_MAIL_USER'], u'Immospooder'),
                    to_addr=(os.environ['SMTP_MAIL_USER_TO'], u'spoooooder'),
                    subject=subject,
                    html_body=html,
                    text_body="New items from immospider"
                )

                response = smtp.send(envelope)
                logger.info(response)
            else:
                logger.info("No new items found. No email sent.")

        def item_scraped(self, item, spider):
            self.items.append(item)

else:
    raise Exception("no mail configured!")
