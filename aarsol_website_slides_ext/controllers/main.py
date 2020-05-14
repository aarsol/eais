# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import json
import logging
import werkzeug
import math

from odoo import http, tools, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_profile.controllers.main import WebsiteProfile
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import AccessError, UserError
from odoo.http import request
from odoo.osv import expression
from datetime import date, datetime
import odoo.addons.website_slides.controllers.main as main

from odoo.addons.website_slides.controllers.main import WebsiteSlides

_logger = logging.getLogger(__name__)
import pdb
from datetime import datetime, date

class WebsiteSlides(WebsiteSlides):


    def _get_slide_quiz_data(self, slide):
        slide_completed = slide.user_membership_id.sudo().completed
        values = {
            'slide_questions': [{
                'id': question.id,
                'question': question.question,
                'answer_ids': [{
                    'id': answer.id,
                    'text_value': answer.text_value,
                    'is_correct': answer.is_correct if slide_completed else None
                } for answer in question.sudo().answer_ids],
            } for question in slide.question_ids]
        }
        values.update(self._get_slide_quiz_partner_info(slide))
        return values

    @http.route('/student/submit/assignment', type='json', auth='user', methods=['POST'], website=True)
    def student_submit_assignment(self, **post):

        partner = request.env.user.partner_id

        slide_id = post.get('slide_id')
        file = post.get('image_1920')

        if file:
            file_size = len(file) * 3 / 4  # base64
            if (file_size / 1024.0 / 1024.0) > 25:
                return {'error': _('File is too big. File size cannot exceed 25MB')}

        slide = request.env['slide.slide'].browse(int(slide_id))
        if not slide:
            return {'error': _('Invalid Content ID')}

        slide_partner = request.env['slide.slide.partner'].search([('partner_id','=',partner.id),('slide_id','=',slide.id)])
        if not slide_partner:
            return {'error': _('You are not allowed to submit the document!')}

        data = {
            'assignment_file': file,
            'submission_date': date.today(),
        }
        slide_partner.write(data)

        return {'success': _('Data Successfully submitted!')}

    def _channel_remove_session_answers(self, channel, slide=False):
        """ Will remove the answers saved in the session for a specific channel / slide. """

        if 'slide_answer_quiz' not in request.session:
            return

        slides_domain = [('channel_id', '=', channel.id)]
        if slide:
            slides_domain = expression.AND([slides_domain, [('id', '=', slide.id)]])
        slides = request.env['slide.slide'].search_read(slides_domain, ['id'])

        session_slide_answer_quiz = json.loads(request.session['slide_answer_quiz'])
        for slide in slides:
            session_slide_answer_quiz.pop(str(slide['id']), None)
        request.session['slide_answer_quiz'] = json.dumps(session_slide_answer_quiz)

    @http.route(['/slides/channel/tag/group/search_read'], type='json', auth='user', methods=['POST'], website=True)
    def slide_channel_tag_group_search_read(self, fields, domain):
        can_create = request.env['slide.channel.tag.group'].check_access_rights('create', raise_exception=False)
        return {
            'read_results': request.env['slide.channel.tag.group'].search_read(domain, fields),
            'can_create': can_create,
        }

    @http.route('/slides/channel/tag/add', type='json', auth='user', methods=['POST'], website=True)
    def slide_channel_tag_add(self, channel_id, tag_id=None, group_id=None):
        """ Adds a slide channel tag to the specified slide channel.
        :param integer channel_id: Channel ID
        :param list tag_id: Channel Tag ID as first value of list. If id=0, then this is a new tag to
                            generate and expects a second list value of the name of the new tag.
        :param list group_id: Channel Tag Group ID as first value of list. If id=0, then this is a new
                              tag group to generate and expects a second list value of the name of the
                              new tag group. This value is required for when a new tag is being created.
        tag_id and group_id values are provided by a Select2. Default "None" values allow for
        graceful failures in exceptional cases when values are not provided.
        :return: channel's course page
        """

        # handle exception during addition of course tag and send error notification to the client
        # otherwise client slide create dialog box continue processing even server fail to create a slide
        try:
            channel = request.env['slide.channel'].browse(int(channel_id))
            can_upload = channel.can_upload
            can_publish = channel.can_publish
        except (UserError, AccessError) as e:
            _logger.error(e)
            return {'error': e.name}
        else:
            if not can_upload or not can_publish:
                return {'error': _('You cannot add tags to this course.')}

        if tag_id:
            # handle creation of new channel tag
            if tag_id[0] == 0:
                if group_id:
                    # handle creation of new channel tag group
                    if group_id[0] == 0:
                        tag_group = request.env['slide.channel.tag.group'].create({
                            'name': group_id[1]['name'],
                        })
                        group_id = tag_group.id
                    # use existing channel tag group
                    else:
                        group_id = group_id[0]
                else:
                    return {'error': _('Missing "Tag Group" for creating a new "Tag".')}

                request.env['slide.channel.tag'].create({'name': tag_id[1]['name'],
                                                         'channel_ids': [channel.id],
                                                         'group_id': group_id,
                                                         })
            else:
                # use existing channel tag
                request.env['slide.channel.tag'].browse(tag_id[0]).write({'channel_ids': [(4, channel.id, 0)]})
        return {'url': "/slides/%s" % (slug(channel))}

    @http.route('/slides/slide/quiz/question_add_or_update', type='json', methods=['POST'], auth='user', website=True)
    def slide_quiz_question_add_or_update(self, slide_id, question, sequence, answer_ids, existing_question_id=None):
        """ Add a new question to an existing slide. Completed field of slide.partner
        link is set to False to make sure that the creator can take the quiz again.
        An optional question_id to udpate can be given. In this case question is
        deleted first before creating a new one to simplify management.
        :param integer slide_id: Slide ID
        :param string question: Question Title
        :param integer sequence: Question Sequence
        :param array answer_ids: Array containing all the answers :
                [
                    'sequence': Answer Sequence (Integer),
                    'text_value': Answer Title (String),
                    'is_correct': Answer Is Correct (Boolean)
                ]
        :param integer existing_question_id: question ID if this is an update
        :return: rendered question template
        """
        fetch_res = self._fetch_slide(slide_id)
        if fetch_res.get('error'):
            return fetch_res
        slide = fetch_res['slide']
        if existing_question_id:
            request.env['slide.question'].search([
                ('slide_id', '=', slide.id),
                ('id', '=', int(existing_question_id))
            ]).unlink()

        request.env['slide.slide.partner'].search([
            ('slide_id', '=', slide_id),
            ('partner_id', '=', request.env.user.partner_id.id)
        ]).write({'completed': False})

        data = {
            'sequence': sequence,
            'question': question,
            'slide_id': slide_id,
        }
        slide_question = request.env['slide.question'].create(data)
        for answer in answer_ids:
            data2 =  {
                    'question_id': slide_question.id,
                    'text_value': answer[0]['text_value'],
                    'is_correct': answer[0]['is_correct'],
                    # 'comment': answer[0]['comment']
                    # 'sequence': answer[0]['sequence'],
            }
            request.env['slide.answer'].create(data2)

        return request.env.ref('aarsol_website_slides_ext.lesson_content_quiz_question').render({
            'slide': slide,
            'question': slide_question,
        })

    @http.route('/slides/slide/quiz/reset', type="json", auth="user", website=True)
    def slide_quiz_reset(self, slide_id):
        fetch_res = self._fetch_slide(slide_id)
        if fetch_res.get('error'):
            return fetch_res
        request.env['slide.slide.partner'].search([
            ('slide_id', '=', fetch_res['slide'].id),
            ('partner_id', '=', request.env.user.partner_id.id)
        ]).write({'completed': False, 'quiz_attempts_count': 0})



    @http.route('''/slides/slide/<model("slide.slide"):slide>''', type='http', auth="public", website=True, sitemap=True)
    def slide_view(self, slide, **kwargs):
        if not slide.channel_id.can_access_from_current_website() or not slide.active:
            raise werkzeug.exceptions.NotFound()
        self._set_viewed_slide(slide)

        values = self._get_slide_detail(slide)
        # quiz-specific: update with karma and quiz information
        if slide.question_ids:
            values.update(self._get_slide_quiz_data(slide))
        # sidebar: update with user channel progress
        values['channel_progress'] = self._get_channel_progress(slide.channel_id, include_quiz=True)

        # Allows to have breadcrumb for the previously used filter
        values.update({
            'search_category': slide.category_id if kwargs.get('search_category') else None,
            'search_tag': request.env['slide.tag'].browse(int(kwargs.get('search_tag'))) if kwargs.get('search_tag') else None,
            'slide_types': dict(request.env['slide.slide']._fields['slide_type']._description_selection(request.env)) if kwargs.get('search_slide_type') else None,
            'search_slide_type': kwargs.get('search_slide_type'),
            'search_uncategorized': kwargs.get('search_uncategorized')
        })

        values['channel'] = slide.channel_id
        values = self._prepare_additional_channel_values(values, **kwargs)
        values.pop('channel', None)

        values['signup_allowed'] = request.env['res.users'].sudo()._get_signup_invitation_scope() == 'b2c'

        slide_partner_comments = request.env['slide.slide.forum'].sudo().search([('partner_id','=',request.env.user.partner_id.id),('slide_id', '=', slide.id)])

        values['slide_partner_comments'] = slide_partner_comments
        values['slide_partner_comments_count'] = len(slide_partner_comments)

        can_live_question = False
        if slide.live_time_start and slide.live_time_end :
            if datetime.now() >= slide.live_time_start and datetime.now() <= slide.live_time_end:
                can_live_question = True
        values['can_live_question'] = can_live_question



        if kwargs.get('fullscreen') == '1':
            return request.render("website_slides.slide_fullscreen", values)
        return request.render("website_slides.slide_main", values)

    @http.route('/save/live/message', type='http', methods=['POST'], auth='public', website=True)
    def save_live_message(self, **kw):

        slide_id = kw.get('slide_id')
        live_message = kw.get('live_message')

        slide = request.env['slide.slide'].sudo().search([('id', '=', int(slide_id))])
        slide_partner = request.env['slide.slide.partner'].sudo().search([('partner_id', '=', request.env.user.partner_id.id),('slide_id', '=', int(slide_id))])

        if not slide_partner:
            slide_partner.create({
                                'partner_id':request.env.user.partner_id.id,
                                'slide_id': int(slide_id),
                                  })
        data = {
            'slide_partner_id': slide_partner.id,
            'comment': live_message,
            'comment_time': datetime.now(),
        }

        if datetime.now() >= slide.live_time_start and datetime.now() <= slide.live_time_end:
            slide_partner_comments = request.env['slide.slide.forum'].sudo().create(data)


        return request.redirect("/slides/slide/%s" % ( slug(slide) ))

    # link for slides: slides/slide/ same as below in xml if you don't want to go to fullscreen directly
    @http.route('''/slides/slide/live/question/<model("slide.slide"):slide>''', type='http', auth="user", website=True, sitemap=True)
    def slide_live_questions(self, slide, **kwargs):
        if not slide.channel_id.can_access_from_current_website() or not slide.active:
            raise werkzeug.exceptions.NotFound()

        slide_partner_id = request.env['slide.slide.partner'].sudo().search([('id', '=', 1)])

        slide_partners_comments = request.env['slide.slide.forum'].sudo().search([('slide_id', '=', slide.id)])
        if slide.channel_id.user_id != request.env.user:
            slide_partners_comments = slide_partners_comments.filtered(lambda l: l.partner_id.id == request.env.user.partner_id.id)


        data = {
            'channel': slide.channel_id,
            'slide': slide,
            'slide_partner': slide_partner_id,
            'slide_partners_comments': slide_partners_comments,
        }

        return request.env.ref('aarsol_website_slides_ext.website_slide_live_questions').render(data)

