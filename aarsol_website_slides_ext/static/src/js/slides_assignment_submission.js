odoo.define('aarsol_website_slides_ext.submit.assignment', function (require) {
'use strict';

var core = require('web.core');
var Dialog = require('web.Dialog');
var publicWidget = require('web.public.widget');
var utils = require('web.utils');

var QWeb = core.qweb;
var _t = core._t;

var AssignmentSubmissionDialog = Dialog.extend({
    template: 'student.assignment.submission.modal',
    events: _.extend({}, Dialog.prototype.events, {
        'change input#upload': '_onChangeSlideUpload',
    }),

    /**
     * @override
     * @param {Object} parent
     * @param {Object} options holding channelId and optionally upload and publish control parameters
     * @param {Object} options.modulesToInstall: list of additional modules to
     *      install {id: module ID, name: module short description}
     */

//     Here parent is this element and options is dictionary that will be passed/**/
    init: function (parent, options) {
        options = _.defaults(options || {}, {
            title: _t('Submit Your Assignment'),
            size: 'medium',
            buttons: [{
                text: _t('Upload'),
                classes: 'btn-primary',
                click: this._onClickFormSubmit.bind(this)
            }, {
                text: _t('Discard'),
                close: true
            }]
        });
        this._super(parent, options);
        this._setup();

//        these values will can be get using widget keyword in template: 'student.assignment.submission.modal',
        this.slideId = options.slideId;
        this.channelID = parseInt(options.channelId, 10);
        this.defaultCategoryID = parseInt(options.categoryId,10);
        this.canUpload = options.canUpload === 'True';
        this.canPublish = options.canPublish === 'True';
        this.modulesToInstall = options.modulesToInstall ? JSON.parse(options.modulesToInstall.replace(/'/g, '"')) : null;
        this.modulesToInstallStatus = null;

        this.set('state', '_select');
//        this.on('change:state', this, this._onChangeType);
        this.set('can_submit_form', false);
//        this.on('change:can_submit_form', this, this._onChangeCanSubmitForm);

        this.file = {};
        this.isValidUrl = true;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    _alertDisplay: function (message) {
        this._alertRemove();
        $('<div/>', {
            "class": 'alert alert-warning',
            role: 'alert'
        }).text(message).insertBefore(this.$('form'));
    },
    _alertRemove: function () {
        this.$('.alert-warning').remove();
    },

    _formSetFieldValue: function (fieldId, value) {
        this.$('form').find('#'+fieldId).val(value);
    },
    _formGetFieldValue: function (fieldId) {
        return this.$('#'+fieldId).val();
    },
    _formValidate: function () {
        var form = this.$("form");
        form.addClass('was-validated');
        return form[0].checkValidity() && this.isValidUrl;
    },

//    Get dictionary for controller
    _formValidateGetValues: function (forcePublished) {
        var canvas = this.$('#data_canvas')[0];
        var values = _.extend({
            'slide_id': this._formGetFieldValue('slide_id'),
            'name': this._formGetFieldValue('name'),
            'duration': this._formGetFieldValue('duration'),
        }); // add tags and category



        if (this.file.type === 'application/pdf') {
            _.extend(values, {
//                'image_1920': canvas.toDataURL().split(',')[1],
                'image_1920': this.file.data,
                'slide_type': canvas.height > canvas.width ? 'document' : 'presentation',
                'mime_type': this.file.type,
                'datas': this.file.data
            });
        } else if (values['slide_type'] === 'webpage') {
            _.extend(values, {
                'mime_type': 'text/html',
                'image_1920': this.file.type === 'image/svg+xml' ? this._svgToPng() : this.file.data,
            });
        } else if (/^image\/.*/.test(this.file.type)) {
            if (values['slide_type'] === 'presentation') {
                _.extend(values, {
                    'slide_type': 'infographic',
                    'mime_type': this.file.type === 'image/svg+xml' ? 'image/png' : this.file.type,
                    'datas': this.file.type === 'image/svg+xml' ? this._svgToPng() : this.file.data
                });
            } else {
                _.extend(values, {
                    'image_1920': this.file.type === 'image/svg+xml' ? this._svgToPng() : this.file.data,
                });
            }
        }
        return values;
    },

    /**
     * @private
     */
    _fileReset: function () {
        var control = this.$('#upload');
        control.replaceWith(control = control.clone(true));
        this.file.name = false;
    },

    /**
     * Get value for category_id and tag_ids (ORM cmd) to send to server
     *
     * @private
     */

    _setup: function () {
        this.slide_type_data = {
            presentation: {
                icon: 'fa-file-pdf-o',
                label: _t('Presentation'),
                template: 'website.slide.upload.modal.presentation',
            },
            webpage: {
                icon: 'fa-file-text',
                label: _t('Web Page'),
                template: 'website.slide.upload.modal.webpage',
            },
            video: {
                icon: 'fa-video-camera',
                label: _t('Video'),
                template: 'website.slide.upload.modal.video',
            },
            quiz: {
                icon: 'fa-question-circle',
                label: _t('Quiz'),
                template: 'website.slide.upload.quiz'
            }
        };
    },
    /**
     * Show the preview/right column and resize the modal
     * @private
     */
    _showPreviewColumn: function() {
        this.$('#o_wslides_js_slide_upload_left_column').removeClass('col').addClass('col-md-6');
        this.$('#o_wslides_js_slide_upload_preview_column').removeClass('d-none');
        this.$modal.find('.modal-dialog').addClass('modal-lg');
    },
    /**
     * Hide the preview/right column and resize the modal
     * @private
     */
    _hidePreviewColumn: function () {
        this.$('#o_wslides_js_slide_upload_left_column').addClass('col').removeClass('col-md-6');
        this.$('#o_wslides_js_slide_upload_preview_column').addClass('d-none');
        this.$modal.find('.modal-dialog').removeClass('modal-lg');
    },
    /**
     * @private
     */
    // TODO: Remove this part, as now SVG support in image resize tools is included
    //Python PIL does not support SVG, so converting SVG to PNG
    _svgToPng: function () {
        var img = this.$el.find('img#slide-image')[0];
        var canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        canvas.getContext('2d').drawImage(img, 0, 0);
        return canvas.toDataURL('image/png').split(',')[1];
    },
    //--------------------------------------------------------------------------
    // Handler
    //--------------------------------------------------------------------------

    _onChangeSlideUpload: function (ev) {
        var self = this;
        this._alertRemove();

        var $input = $(ev.currentTarget);
        var preventOnchange = $input.data('preventOnchange');

        var file = ev.target.files[0];
        if (!file) {
            this.$('#slide-image').attr('src', '/website_slides/static/src/img/document.png');
            this._hidePreviewColumn();
            return;
        }
        var isImage = /^image\/.*/.test(file.type);
        var loaded = false;
        this.file.name = file.name;
        this.file.type = file.type;
        if (!(isImage || this.file.type === 'application/pdf')) {
            this._alertDisplay(_t("Invalid file type. Please select pdf or image file"));
            this._fileReset();
            this._hidePreviewColumn();
            return;
        }
        if (file.size / 1024 / 1024 > 25) {
            this._alertDisplay(_t("File is too big. File size cannot exceed 25MB"));
            this._fileReset();
            this._hidePreviewColumn();
            return;
        }

        utils.getDataURLFromFile(file).then(function (buffer) {
            if (isImage) {
                self.$('#slide-image').attr('src', buffer);
            }
            buffer = buffer.split(',')[1];
            self.file.data = buffer;
            self._showPreviewColumn();
        });

        if (file.type === 'application/pdf') {
            var ArrayReader = new FileReader();
            this.set('can_submit_form', false);
            // file read as ArrayBuffer for PDFJS get_Document API
            ArrayReader.readAsArrayBuffer(file);
            ArrayReader.onload = function (evt) {
                var buffer = evt.target.result;
                var passwordNeeded = function () {
                    self._alertDisplay(_t("You can not upload password protected file."));
                    self._fileReset();
                    self.set('can_submit_form', true);
                };
                /**
                 * The following line fixes PDFJS 'Util' global variable.
                 * This is (most likely) related to #32181 which lazy loads most assets.
                 *
                 * That caused an issue where the global 'Util' variable from PDFJS can be
                 * (depending of which libraries load first) overridden by the global 'Util'
                 * variable of bootstrap.
                 * (See 'lib/bootstrap/js/util.js' and 'lib/pdfjs/src/shared/util.js')
                 *
                 * This commit ensures that the global 'Util' variable is set to the one of PDFJS
                 * right before it's used.
                 *
                 * Eventually, we should update or get rid of one of the two libraries since they're
                 * not compatible together, or make a wrapper that makes them compatible.
                 * In the mean time, this small fix allows not refactoring all of this and can not
                 * cause much harm.
                 */
                /*Util = PDFJS.Util;*/
                Util = window.pdfjsLib.Util;
                /*PDFJS.getDocument(new Uint8Array(buffer), null, passwordNeeded).then(function getPdf(pdf) {*/
                PDFJS.getDocument(new Uint8Array(buffer), null, passwordNeeded).then(function getPdf(pdf) {
                    self._formSetFieldValue('duration', (pdf.pdfInfo.numPages || 0) * 5);
                    pdf.getPage(1).then(function getFirstPage(page) {
                        var scale = 1;
                        var viewport = page.getViewport(scale);
                        var canvas = document.getElementById('data_canvas');
                        var context = canvas.getContext('2d');
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        // Render PDF page into canvas context
                        page.render({
                            canvasContext: context,
                            viewport: viewport
                        }).then(function () {
                            var imageData = self.$('#data_canvas')[0].toDataURL();
                            self.$('#slide-image').attr('src', imageData);
                            if (loaded) {
                                self.set('can_submit_form', true);
                            }
                            loaded = true;
                            self._showPreviewColumn();
                        });
                    });
                });
            };
        }

        if (!preventOnchange) {
            var input = file.name;
            var inputVal = input.substr(0, input.lastIndexOf('.')) || input;
            this._formSetFieldValue('name', inputVal);
        }
    },

    _onClickFormSubmit: function (ev) {
        var self = this;
        var $btn = $(ev.currentTarget);
        if (this._formValidate()) {
            var values = this._formValidateGetValues($btn.hasClass('student_assignment_submission_form')); // get info before changing state
            var oldType = this.get('state');
            this.set('state', '_upload');
            return this._rpc({
                route: '/student/submit/assignment',
                params: values,
            }).then(function (data) {
                if (data.error) {
                    self.set('state', oldType);
                    self._alertDisplay(data.error);
                } else {
//                    window.location = data.url;
                    self._alertDisplay(data.success);
                    setTimeout(function(){ self.close(); }, 1000);
                }
            });
        }
    },

});

publicWidget.registry.websiteAssignmentSubmission = publicWidget.Widget.extend({
    selector: '.o_wslides_fs_student_assignment_submission',
    xmlDependencies: ['/aarsol_website_slides_ext/static/src/xml/assignment_management.xml'],
    events: {
        'click': 'onSubmitAssignmentClick',
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    _openDialog: function (slideId) {
        new AssignmentSubmissionDialog(this, {slideId: slideId}).open();
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    onSubmitAssignmentClick: function (ev) {
        ev.preventDefault();
        this._openDialog($(ev.currentTarget).attr('slide_id'));
    },
});

return {
    AssignmentSubmissionDialog: AssignmentSubmissionDialog,
    websiteAssignmentSubmission: publicWidget.registry.websiteAssignmentSubmission
};

});

