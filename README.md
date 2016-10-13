
django-upthor
========

`django-upthor` provides a django application for simple ajax file uploads. We use
https://github.com/blueimp/jQuery-File-Upload for the upload functionality.

**Warning:** This isn't close to being a complete app, but it's getting there.


Usage
===========================================


Step 1. Install
-------------------------------------

- `pip install git+https://github.com/Jyrno42/django-upthor.git`

Now you have two options:

- If you want to encrypt FQ values, install pycrypto. `pip install pycrypto==2.6.1`
- Or you can, disable FQ encryption by adding `THOR_DISABLE_FQ_ENCRYPT = True` to your settings file.



Step 2. (Django 1.6+)
-------------------------------------
Add 'upthor' to your installed apps in settings.py:

```
INSTALLED_APPS = (
    ...
    "upthor",
)
```

Then:

```
python manage.py migrate
```


Step 3. Use it in your app's models.
----------------------------------------

```

import os
import uuid

from django.db import models
from upthor import fields as thor_fields


def random_upload_path(instance, filename):
    # Split the uuid into two parts so that we won't run into subdirectory count limits. First part has 3 hex chars,
    #  thus 4k possible values.
    uuid_hex = uuid.uuid4().hex
    return os.path.join(uuid_hex[:3], uuid_hex[3:], filename)


def post_example_file_link(real_instance, temporary_instance, raw_file):
    """
        A callback called after linking the temporary file with the model.
        
        **Warning**: Don't call instances save method from here, cause it will cause an recursion error.
    
        @:param real_instance An instance of the model the file is attached to
        @:param temporary_instance An instance of TemporaryFileWrapper that the form links to.
        @:param raw_file The raw file that is being uploaded.

        @:return bool If True, the uploaded temporary file is removed once the linking is complete.
    """
    return True


def get_file_image(file_path):
    """ An optional function that returns the display image html for files after uploading is complete"""
    
    return '<i class="fa fa-file"></i>'


class ExampleModelWithFile(models.Model):
    name = models.CharField(max_length=50)
    file = thor_fields.ThorFileField(upload_to=random_upload_path,
                                   allowed_types=['*'], widget=thor_fields.ThorSingleUploadWidget,
                                   post_link=post_product_file_link,
                                   get_upload_image=get_file_image)
```


Step 4. Make sure to include form media.
------------------------------------------

Make sure you include the media files for the form in your templates:

E.g. Add the following codes where form is the context 
object of your modelform that uses the uploader fields.

```
    {{ form.media.css }}
    
    {{ form.media.js }}
```


Step 5. Add the upload url to your project urls.
------------------------------------------

```
    url(r'', include('upthor.urls')),
```


Step 6. Optional stuff
------------------------------------------

#### Temporary file cleanup

If you want to clean up temporary files automatically, you'll need to install [django-cron](https://github.com/Tivix/django-cron) and add `upthor.cron.CleanTemporaryFiles` to your cron classes in settings.

Alternatively to clean up manually you can use the management command `clean_temporary_files`.

#### Custom upload widget template

You can override `ThorSingleUploadWidget.render_template` to return your own widget template instead of the [hardcoded one defined in widgets.py](upthor/widgets.py). Although the structure (including most classes) has to remain the same, there are a few data attributes on `.file-upload` that you can use to customize behavior:

| Data Attribute Name | Type    | Description                              |
| ------------------- | ------- | ---------------------------------------- |
| upload-url          | string  | **Required:** URL to POST temporary files to, defaults to reverse of `thor-file-upload`. |
| max-size            | number  | **Required:** Maximum allowed file size in bytes, defaults to `THOR_MAX_FILE_SIZE`. |
| size-error          | string  | **Required:** Text to display if the file doesn't meet the size requirements, defaults to ` "Uploaded file too large"`. |
| use-background      | boolean | Whether or not to use `background-image` instead of `img` elements, defaults to false. |


Backends
========

Currently it only supports local file backend, but we plan to add other backends when we reach a stable state.


Settings
========

The following settings are customizable using your django project settings file.

### THOR_UPLOAD_TO ###

Path where the upload files will be stored. Defaults to "temp-files".

### THOR_EXPIRE_TIME ###

How long are the temporary files kept in the database and on disk. Defaults to "60*60*24", e.g. 24 hours.

### THOR_LINKED_EXPIRE_TIME ###

How long are the linked temporary files kept in the database and on disk. Defaults to "60*60*6", e.g. 6 hours.

### THOR_MAX_FILE_SIZE ###

Whats the max file size of uploaded files. Defaults to "2*1024*1024", e.g. 2 MB. 

### THOR_DISABLE_FQ_ENCRYPT ###

Disable the FQ Encryption, if this is False you need to install pycrypto since that is used for encryption. Defaults to "False".

### THOR_ENABLE_ADMIN ###

Should TemporaryFileWrapper model be shown in the admin interface. Defaults to "True".
