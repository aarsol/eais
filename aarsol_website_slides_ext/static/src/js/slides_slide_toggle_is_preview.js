odoo.define('aarsol_website_slides_ext.slide.preview', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.websiteSlidesSlideToggleIsPreview = publicWidget.Widget.extend({
        selector: '.o_wslides_js_slide_toggle_is_preview',
        xmlDependencies: ['/aarsol_website_slides_ext/static/src/xml/slide_management.xml'],
        events: {
            'click': '_onPreviewSlideClick',
        },

        _toggleSlidePreview: function($slideTarget) {
            this._rpc({
                route: '/slides/slide/toggle_is_preview',
                params: {
                    slide_id: $slideTarget.data('slideId')
                },
            }).then(function (isPreview) {
                if (isPreview) {
                    $slideTarget.removeClass('badge-light badge-hide border');
                    $slideTarget.addClass('badge-success py-1');
                } else {
                    $slideTarget.removeClass('badge-success py-1');
                    $slideTarget.addClass('badge-light badge-hide border');
                }
            });
        },

        _onPreviewSlideClick: function (ev) {
            ev.preventDefault();
            this._toggleSlidePreview($(ev.currentTarget));
        },
    });

    return {
        websiteSlidesSlideToggleIsPreview: publicWidget.registry.websiteSlidesSlideToggleIsPreview
    };

});
