# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class SurveyQuestion(models.Model):

    _inherit = 'survey.question'

    time_limit = fields.Float("Time limit (minutes)", default=1)
    ques_time_limit = fields.Float("Time limit For Questions", default=1)
    re_arange_ans = fields.Boolean("Auto Re-Arrange Answers")
    questions_time_option = fields.Selection(string="Time Limit", related='survey_id.questions_time_option', store=True)


class SurveyLabel(models.Model):
    """ A suggested answer for a question """
    _inherit = 'survey.label'

    description = fields.Html('Description', help="Use this field to add additional explanations about your answer", translate=True)
