#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2014 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from mailer import send_html_mail
#from user_profile.models import User
from mod_mailer.constants import MAILSPOOLER_TYPE
from dialer_contact.models import Contact


class MailTemplate(models.Model):
    """
    This table store the Mail Template
    """
    label = models.CharField(max_length=75, verbose_name=_('label'),
                             help_text=_('mail template name'))
    template_key = models.CharField(max_length=30, unique=True, verbose_name=_('template key'),
                                    help_text=_('unique name used to pick some template for recurring action, such as activation or warning'))
    from_email = models.EmailField(max_length=75, verbose_name=_('from_email'),
                                   help_text=_('sender email'))
    from_name = models.CharField(max_length=75, verbose_name=_('from_name'),
                                 help_text=_('sender name'))
    subject = models.CharField(max_length=200, verbose_name=_('subject'),
                               help_text=_('email subject'))
    message_plaintext = models.TextField(max_length=5000, verbose_name=_('message plaintext'),
                                         help_text=_('plain text version of the email'))
    message_html = models.TextField(max_length=5000, verbose_name=_('message_html'),
                                    help_text=_('HTML version of the Email'))
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Mail template')
        verbose_name_plural = _('Mail templates')

    def __unicode__(self):
        return force_unicode(self.template_key)


class MailSpooler(models.Model):
    """
    This table store the Mail Spooler
    """
    mailtemplate = models.ForeignKey(MailTemplate, verbose_name=_('mail template'))
    contact_email = models.EmailField(verbose_name=_('contact email'))
    created_date = models.DateTimeField(auto_now_add=True)
    parameter = models.CharField(max_length=1000,
                                 verbose_name=_('parameter'), blank=True, null=True)
    mailspooler_type = models.IntegerField(choices=list(MAILSPOOLER_TYPE),
                                           blank=True, null=True, verbose_name=_("type"),
                                           default=MAILSPOOLER_TYPE.PENDING)

    class Meta:
        verbose_name = _('mail spooler')

    def __unicode__(self):
        return force_unicode(self.id)


def send_email_template(template_key, target_user, ctxt):
    """
    Send email via mail backend
    """
    try:
        mailtemplate = MailTemplate.objects.get(template_key=template_key)
    except:
        #No Mail Template
        return False

    message_plaintext = mailtemplate.message_plaintext
    message_html = mailtemplate.message_html

    # Replace tags
    for ctag in ctxt:
        mtag = '%' + ctag + '%'
        vtag = ctxt[ctag]
        message_plaintext = message_plaintext.replace(mtag, vtag.encode('utf-8'))
        message_html = message_html.replace(mtag, vtag.encode('utf-8'))

    send_html_mail(
        mailtemplate.subject,
        message_plaintext,
        message_html,
        mailtemplate.from_email,
        [target_user.email],
        headers={'From': '%s <%s>' % (mailtemplate.from_name, mailtemplate.from_email)},
    )
    #new_mailspooler = MailSpooler(mailtemplate=mailtemplate, user=target_user)
    #new_mailspooler.save()
