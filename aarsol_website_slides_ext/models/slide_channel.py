# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Channel(models.Model):
    """ A channel is a Course of slides. """
    _inherit = 'slide.channel'

    nbr_assignment = fields.Integer("Number of Assignments", compute='_compute_slides_statistics', store=True)


    def action_publish(self):
        self.is_published = True

    def action_private(self):
        self.is_published = False