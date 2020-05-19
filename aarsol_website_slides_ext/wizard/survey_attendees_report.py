import pdb
import time
import datetime
from openerp import api, fields, models,_
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import math


class SlideSurveyAttendeesWiz(models.TransientModel):
	_name ='slide.survey.attendees.wiz'
	_description = 'Slide Survey Attendees Wizard'

	channel_id = fields.Many2one('slide.channel', string='Course')
	slide_id = fields.Many2one('slide.slide', string='Content/Paper')
	type = fields.Selection([('present','Present'),('absent','Absent')], default='absent')

	def print_report(self):
		self.ensure_one()
		[data] = self.read()
		datas = {
			'ids': [],
			'model': 'slide.channel.partner',
			'form': data
		}

		return self.env.ref('aarsol_website_slides_ext.action_report_slide_survey_attendees').with_context(landscape=False).report_action(self, data=datas, config=False)




