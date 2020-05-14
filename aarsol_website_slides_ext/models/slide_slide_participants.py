# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import Warning, UserError, AccessError
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import url_for
import pdb


class SlideForum(models.Model):
    _name = 'slide.slide.forum'

    slide_partner_id = fields.Many2one('slide.slide.partner', string='Slide Partner')
    partner_id = fields.Many2one('res.partner', string='Partner', related="slide_partner_id.partner_id", store=True, index=True, ondelete='cascade')
    slide_id = fields.Many2one('slide.slide', string = 'Course Content', related="slide_partner_id.slide_id", store=True, index=True, ondelete='cascade')
    channel_id = fields.Many2one('slide.channel', string="Channel", related="slide_id.channel_id", store=True, index=True, ondelete='cascade')
    comment = fields.Text('Comment')
    comment_time = fields.Datetime("Comment Time")

