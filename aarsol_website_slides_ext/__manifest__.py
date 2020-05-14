# -*- coding: utf-8 -*-
{
    'name': 'AARSOL Website E-Learning',
    'version': '1.0',
    'sequence': 10,
    'summary': 'Manage and publish an eLearning platform',
    'website': 'https://www.aarsol.com/',
    'category': 'Website/Website',
    'description': """
Create Online Courses
=====================

Featuring

 * Integrated course and lesson management
 * Fullscreen navigation
 * Support Youtube videos, Google documents, PDF, images, web pages
 * Test knowledge with quizzes
 * Filter and Tag
 * Statistics
""",
    'depends': ['website_slides','survey','website_slides_survey'],
    'data': [

        'views/templates/assets.xml',
        'views/templates/website_slides_templates_homepage.xml',
        'views/templates/website_slides_templates_course.xml',
        'views/templates/website_slides_templates_course_inherit.xml',
        'views/templates/website_slides_templates_lesson.xml', #this is for normal screen slides view
        # 'views/templates/website_slides_templates_lesson_inherit.xml', #this is for normal screen slides view
        'views/templates/website_slides_templates_lesson_embed.xml',
        'views/templates/website_slides_templates_lesson_fullscreen.xml',
        'views/templates/website_slides_templates_profile.xml',
        'views/templates/website_slides_templates_utils.xml',
        'views/templates/website_slides_templates_live_questions.xml',
        'views/templates/survey_templates.xml',

        'views/menus.xml',

        'views/slide_channel_views.xml',
        'views/slide_slide_views.xml',
        'views/survey_question_views.xml',
        'views/survey_survey_views.xml',

        'wizard/assign_channels_view.xml',

        'security/ir.model.access.csv',

    ],

    'demo': [
    ],
    'installable': True,
    'application': True,
}
