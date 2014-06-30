import os

import six

from django.core.urlresolvers import reverse
from django.forms import widgets, CheckboxInput
from django.utils.encoding import force_text
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from upthor.forms import allowed_type
from upthor.models import TemporaryFileWrapper, get_max_file_size, get_size_error, FqCrypto, fq_encrypt_disabled


DELETE_FIELD_HTML = """
            <input type="checkbox" id="id-{clear_checkbox_name}" data-del-field="1" name="{clear_checkbox_name}" value='1' {delete_val} />
"""

HTML = """
    <div class="col-xs-12 col-md-12 well {classes}"
        data-upload-url="{upload_url}" data-max-size="{max_size}" data-size-error="{size_error}">

        <div class="drag-target-overlay">
            <div>
                Drop files to upload
            </div>
        </div>

        <label>
            <span class="image-area">
                <img src="{file_url}">
            </span>

            <span class="file-display">
                {file_upload_icon}
                <span data-file-name="1">{file_name}</span>
            </span>

            <span class="upload-link"><i class="fa fa-cloud-upload"></i></span>

            <div class="progress-area">
                Uploading...
                <div class="progress progress-striped active">
                    <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                </div>
            </div>

            <input type="file" id="{element_id}" name="{name}" />
            <input type="hidden" id="{element_id}_md5sum" name="{md5sum_field_name}" value="{md5sum_field_value}" />
            <input type="hidden" id="{element_id}_FQ" name="{fq_field_name}" value='{FQ}' />
            {delete_field}
        </label>

        <button type="button" class="close">&times;</button>
    </div>
"""


class ThorSingleUploadWidget(widgets.FileInput):
    class Media:
        js = (
            'upthor/js/jquery.iframe-transport.js',
            'upthor/js/jquery.ui.widget.js',
            'upthor/js/jquery.fileupload.js',
            'upthor/js/upthor-fileupload.js',
        )
        css = {
            'all': ('upthor/css/font-awesome.css', 'upthor/css/main.css', ),
        }

    widget_class = 'single-uploader'
    is_thor_widget = True

    def __init__(self, fq, is_image, attrs=None):
        self.field_query = fq
        self.is_image = is_image
        self.force_delete_field = False

        super(ThorSingleUploadWidget, self).__init__(attrs)

    @staticmethod
    def clear_checkbox_name(name):
        if '-' not in name:
            return '%s-DELETE' % name

        return '%s-DELETE' % '-'.join(name.split('-')[:-1])

    @staticmethod
    def fq_field_name(name):
        return '%s_FQ' % name

    @staticmethod
    def md5sum_field_name(name):
        return '%s_md5sum' % name

    def get_fq(self):
        fq = [
            force_text(self.field_query[0]._meta.app_label),
            force_text(self.field_query[0]._meta.object_name),
            self.field_query[1],
        ]

        fq_val = 'FQ:%s' % '.'.join(fq)

        if fq_encrypt_disabled():
            return fq_val
        else:
            return FqCrypto.encode(fq_val)

    def get_required_state(self):
        return self.is_required

    def value_from_datadict(self, data, files, name):
        upload = data.get(self.md5sum_field_name(name), None)
        fq = data.get(self.fq_field_name(name), None)

        if isinstance(upload, six.string_types) and upload[:3] == 'id:':
            # Pre uploaded linked file.
            return TemporaryFileWrapper.get_image_from_id(upload[3:], self.field_query)

        if fq != self.get_fq():
            raise Exception(force_text('For some reason FQ value is wrong...'))

        was_deleted = CheckboxInput().value_from_datadict(data, files, self.clear_checkbox_name(name))

        if not self.get_required_state() and was_deleted:
            # If isn't required and delete is checked
            if not upload:
                # False signals to clear any existing value, as opposed to just None
                return False

        if upload:
            try:
                real_file = TemporaryFileWrapper.objects.get(md5sum=upload)
            except TemporaryFileWrapper.DoesNotExist:
                pass
            else:
                upload = real_file.file

        return upload

    def render_delete_field(self, name, delete_val):
        return DELETE_FIELD_HTML.format(
            clear_checkbox_name=self.clear_checkbox_name(name),
            delete_val=delete_val
        )

    def get_is_image(self, value):
        if self.is_image:
            # Don't use the file type guesser if it's a image.
            return True

        if value:
            from upthor.fields import ThorFileField

            if hasattr(value, 'instance') and isinstance(value.instance, TemporaryFileWrapper):
                # Case 1: Temporary-file in form.
                return allowed_type(value.instance.content_type, ThorFileField.handle_allowed_types(['type:image']))
            elif hasattr(value, "url"):
                # Case 2: Pre existing linked-file in form.
                func = getattr(value.instance, 'is_upthor_image', None)

                if func and callable(func):
                    return func(self.get_fq())
                else:
                    return bool(func)

        return False

    def render_template(self, **kwargs):
        return force_text(HTML).format(**kwargs)

    def render(self, name, value, attrs=None):
        element_id = 'id'
        md5sum_field_value = ''
        file_url = ''
        file_path = ''

        if value:
            if hasattr(value, 'instance') and isinstance(value.instance, TemporaryFileWrapper):
                # Case 1: Pre existing temporary-file in form.
                md5sum_field_value = value.instance.md5sum
                file_url = force_text(value.instance.file.url)
                file_path = force_text(value.instance.file.path)
            elif hasattr(value, "url") and value.name != 'False':
                # Case 2: Pre existing linked-file in form.
                file_url = force_text(value.url)
                file_path = force_text(value.path)
                md5sum_field_value = 'id:%s' % value.instance.id

        classes = ['file-uploader', self.widget_class, 'has-image' if file_url else '']

        if file_url and not self.get_is_image(value):
            classes.append('is-file')

        upload_url = reverse('thor-file-upload')
        delete_val = '' if file_url else 'checked="checked"'

        file_name = os.path.split(value.name)[-1] if value and hasattr(value, "name") else 'Uploaded.pdf'

        delete_field = self.render_delete_field(name, delete_val)

        output = self.render_template(
            name=name,
            file_url=self.get_file_upload_url_func(file_url),
            element_id=element_id,
            classes=' '.join(classes),
            upload_url=upload_url,
            FQ=self.get_fq(),
            md5sum_field_name=self.md5sum_field_name(name),
            fq_field_name=self.fq_field_name(name),
            md5sum_field_value=md5sum_field_value,
            delete_field=delete_field,
            file_name=file_name,
            max_size=get_max_file_size(),
            size_error=get_size_error(),
            value=value,
            file_path=file_path,
            file_upload_icon=self.get_file_upload_icon_func(file_path),
        )

        return mark_safe(force_text(output))

    def get_file_upload_icon_func(self, file_path):

        for field in self.field_query[0]._meta.fields:
            if field.name == self.field_query[1]:
                if hasattr(field, 'get_upload_image'):
                    if field.get_upload_image is not None:
                        if callable(field.get_upload_image):
                            return field.get_upload_image(file_path)
                        else:
                            return force_text(field.get_upload_image)

        return '<i class="fa fa-file"></i>'

    def get_file_upload_url_func(self, file_url):

        for field in self.field_query[0]._meta.fields:
            if field.name == self.field_query[1]:
                if hasattr(field, 'get_upload_image_url'):
                    if field.get_upload_image_url is not None:
                        if callable(field.get_upload_image_url):
                            return field.get_upload_image_url(file_url)
                        else:
                            return force_text(field.get_upload_image_url)

        return file_url


class ThorMultiUploadWidget(ThorSingleUploadWidget):
    widget_class = 'multi-uploader'

    def render_delete_field(self, name, delete_val):
        if self.force_delete_field:
            return super(ThorMultiUploadWidget, self).render_delete_field(name, delete_val)

        return ''
