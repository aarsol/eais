import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class SlideSurveyAttendeesReport(models.AbstractModel):
    _name = 'report.aarsol_website_slides_ext.slide_survey_attendees_report'
    _description = 'Slide Survey Attendees Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        slide_id = data['form']['slide_id'] and data['form']['slide_id'][0] or False
        type = data['form']['type'] or False

        slide_id = self.env['slide.slide'].search([('id', '=', slide_id),('slide_type', '=', 'certification')])
        if not slide_id:
            raise UserError(_("Paper in not valid"))

        attendees = self.env['res.partner']
        channel_partners = self.env['slide.channel.partner'].search([('channel_id', '=', slide_id.channel_id.id)]).mapped('partner_id')
        user_input_partners = self.env['survey.user_input'].search([('slide_id', '=', slide_id.id),('survey_id', '=', slide_id.survey_id.id)]).mapped('partner_id')

        if type == 'present':
            attendees = user_input_partners
        elif type == 'absent':
            attendees = channel_partners - user_input_partners



        report = self.env['ir.actions.report']._get_report_from_name('aarsol_website_slides_ext.survey_attendees_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'date': str(fields.Datetime.now()),
            'attendees': attendees,
        }
        return docargs
