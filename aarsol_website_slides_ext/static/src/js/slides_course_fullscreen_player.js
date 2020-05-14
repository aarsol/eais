odoo.define('aarsol_website_slides_ext.fullscreen.ext', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var config = require('web.config');
    var QWeb = core.qweb;
    var _t = core._t;

    var session = require('web.session');

    var Quiz = require('website_slides.quiz').Quiz;

    var Dialog = require('web.Dialog');

    require('website_slides.course.join.widget');



    var Fullscreen = require('website_slides.fullscreen');


    Fullscreen.include({

        /*_preprocessSlideData: function (slidesDataList) {
            slidesDataList.forEach(function (slideData, index) {
                // compute hasNext slide
                slideData.hasNext = index < slidesDataList.length-1;
                // compute embed url
                if (slideData.type === 'assignment') {
                    slideData.embedUrl = $(slideData.embedCode).attr('src');
                }
                });
            return slidesDataList;
        },*/

        /**
         * Render the current slide content using specific mecanism according to slide type:
         * - simply append content (for webpage)
         * - template rendering (for image, document, ....)
         * - using a sub widget (quiz and video)
         *
         * @private
         * @returns Deferred
         */
        _renderSlide: function () {
            var slide = this.get('slide');
            var $content = this.$('.o_wslides_fs_content');
            $content.empty();

            // display quiz slide, or quiz attached to a slide
            if (slide.type === 'quiz' || slide.isQuiz) {
                $content.addClass('bg-white');
                var QuizWidget = new Quiz(this, slide, this.channel);
                return QuizWidget.appendTo($content);
            }

            // render slide content
            if (_.contains(['assignment', 'document', 'presentation', 'infographic'], slide.type)) {
                $content.html(QWeb.render('website.slides.fullscreen.content', {widget: this}));
                }
            return Promise.resolve();
        },

        _renderSlide: function (){
        var def = this._super.apply(this, arguments);
        var $content = this.$('.o_wslides_fs_content');
        if (this.get('slide').type === "certification"){
            $content.html(QWeb.render('website.slides.fullscreen.content',{widget: this}));
        }
        return Promise.all([def]);
    },



    });

    publicWidget.registry.websiteSlidesFullscreenPlayer = publicWidget.Widget.extend({
        selector: '.o_wslides_fs_main',
        xmlDependencies: ['/aarsol_website_slides_ext/static/src/xml/website_slides_fullscreen.xml', '/aarsol_website_slides_ext/static/src/xml/website_slides_share.xml'],

    });

});
