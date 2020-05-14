# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import Warning, UserError, AccessError
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import url_for
import pdb


class Survey(models.Model):

    _inherit = 'survey.survey'

    questions_time_option = fields.Selection([
        ('each_question', 'Time for each question'),
        ('all_question', 'Time for All Questions(Combined)')],
        string="Time Limit", required=True, default='all_question')

    auto_next_ques = fields.Boolean("Auto Move to Next Question")
    time_from_section = fields.Boolean("Time From Section", help='If checked, system will pick time for question from section.')

