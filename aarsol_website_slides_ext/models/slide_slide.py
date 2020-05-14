# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import Warning, UserError, AccessError
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import url_for
import pdb


class Slide(models.Model):
    _inherit = 'slide.slide'

    slide_type = fields.Selection(selection_add=[('assignment', 'Assignment')])
    nbr_assignment = fields.Integer("Number of Assignments", compute='_compute_slides_statistics', store=True)
    is_live = fields.Boolean("Is Live Session?", default=False)
    live_time_start = fields.Datetime("Live Session Start?")
    live_time_end = fields.Datetime("Live Session End?")
    attendance_required = fields.Boolean("Must Attend?", default=False)

    @api.depends('document_id', 'slide_type', 'mime_type')
    def _compute_embed_code(self):
        base_url = request and request.httprequest.url_root or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url[-1] == '/':
            base_url = base_url[:-1]
        for record in self:
            if record.datas and (not record.document_id or record.slide_type in ['assignment','document', 'presentation']):
                slide_url = base_url + url_for('/slides/embed/%s?page=1' % record.id)
                record.embed_code = '<iframe src="%s" class="o_wslides_iframe_viewer" allowFullScreen="true" height="%s" width="%s" frameborder="0"></iframe>' % (slide_url, 315, 420)
            elif record.slide_type == 'video' and record.document_id:
                if not record.mime_type:
                    # embed youtube video
                    record.embed_code = '<iframe src="//www.youtube.com/embed/%s?theme=light" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id)
                else:
                    # embed google doc video
                    record.embed_code = '<iframe src="//drive.google.com/file/d/%s/preview" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id)
            else:
                record.embed_code = False

    def action_publish(self):
        self.is_published = True

    def action_private(self):
        self.is_published = False


class SlidePartnerRelation(models.Model):
    _inherit = 'slide.slide.partner'
    _rec_name = 'partner_id'

    assignment_file = fields.Binary('Assignment File', attachment=True)
    submission_date = fields.Date('Submission Date')
    can_submit = fields.Boolean('Can Submit', default=False)

    user_in_time = fields.Datetime("User in Time")
    user_out_time = fields.Datetime("User out Time")
    user_attendance_time = fields.Datetime("User out Time")

    comments_ids = fields.One2many("slide.slide.forum", 'slide_partner_id', string="Comments")