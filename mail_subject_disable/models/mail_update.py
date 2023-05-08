# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo.tools import email_normalize

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_by_email_get_base_mail_values(self, message, additional_values=None):
        """ Add model-specific values to the dictionary used to create the
        notification email. Its base behavior is to compute model-specific
        headers.

        :param dict base_mail_values: base mail.mail values, holding message
        to notify (mail_message_id and its fields), server, references, subject.
        """
        mail_subject = message.subject or (
                message.record_name and 'Re: %s' % message.record_name)  # in cache, no queries
        # Replace new lines by spaces to conform to email headers requirements
        mail_subject = ' '.join(('' or '').splitlines())
        # compute references: set references to the parent and add current message just to
        # have a fallback in case replies mess with Messsage-Id in the In-Reply-To (e.g. amazon
        # SES SMTP may replace Message-Id and In-Reply-To refers an internal ID not stored in Odoo)
        message_sudo = message.sudo()
        if message_sudo.parent_id:
            references = f'{message_sudo.parent_id.message_id} {message_sudo.message_id}'
        else:
            references = message_sudo.message_id
        # prepare notification mail values
        base_mail_values = {
            'mail_message_id': message.id,
            'mail_server_id': message.mail_server_id.id,
            # 2 query, check acces + read, may be useless, Falsy, when will it be used?
            'references': references,
            'subject': mail_subject,
        }
        if additional_values:
            base_mail_values.update(additional_values)

        headers = self._notify_by_email_get_headers()
        if headers:
            base_mail_values['headers'] = repr(headers)
        return base_mail_values
