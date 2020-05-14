import pdb
import time
import datetime
from openerp import api, fields, models,_
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import math


class SlideAssignChannelWiz(models.TransientModel):
	_name ='slide.assign.channel.wiz'
	_description = 'Assign Channel Wizard'

	# @api.model
	# def _get_channels(self):
	# 	if self.env.context.get('active_model', False) == 'slide.channel' and self.env.context.get('active_ids', False):
	# 		return self.env.context['active_ids']

	function = fields.Char('Class')  #In res_partner function field with String Job Position

	# channel_ids = fields.Many2many('slide.channel', string='Channels',  compute='_get_channels', store=True)
	# partner_ids = fields.Many2many('res.partner', compute='_get_partners', store=True)

	channel_ids = fields.Many2many('slide.channel', string='Channels')
	partner_ids = fields.Many2many('res.partner')

	@api.depends('function')
	def _get_channels(self):
		channel_ids = self.env['slide.channel'].search([('function', '=', self.function)])
		if channel_ids:
			self.channel_ids = [(6, 0, channel_ids.ids)]
		else:
			self.channel_ids = [(6, 0, [0])]

	@api.depends('function')
	def _get_partners(self):
		partner_ids = self.env['res.partner'].search([('function', '=', self.function)])
		if partner_ids:
			self.partner_ids = [(6, 0, partner_ids.ids)]
		else:
			self.partner_ids = [(6, 0, [0])]




	def assign_channels(self):
		channel_ids = self.env['slide.channel'].search([('id','in',self.channel_ids.mapped('id'))])
		partner_ids = self.env['res.partner'].search([('id', 'in', self.partner_ids.mapped('id'))])

		if not channel_ids or not partner_ids:
			raise UserError('Select both Course and Students')

		slide_partner_ids = self.env['slide.channel.partner']

		for channel in channel_ids:
			for partner in partner_ids:
				slide_partner_id = self.env['slide.channel.partner'].search([('channel_id','=',channel.id),('partner_id','=',partner.id)])
				if not slide_partner_id:
					data = {
						'channel_id': channel.id,
						'partner_id': partner.id,
					}
					slide_partner_ids += self.env['slide.channel.partner'].create(data)


		if slide_partner_ids:
			reg_list = slide_partner_ids.mapped('id')
			return {
				'domain': [('id', 'in', reg_list)],
				'name': _('Slide Partners'),
				'view_mode': 'tree',
				'res_model': 'slide.channel.partner',
				'view_id': False,
				# 'context': {'default_class_id': self.id},
				'type': 'ir.actions.act_window'
			}
		else:
			return {'type': 'ir.actions.act_window_close'}



