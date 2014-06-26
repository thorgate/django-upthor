import base64
import hashlib
import os
import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.defaultfilters import filesizeformat
from django.utils.encoding import force_text, force_bytes
from django.utils.translation import ugettext_lazy as _


def get_upload_path():
    return getattr(settings, 'THOR_UPLOAD_TO', 'temp-files')


def get_expiry_time():
    return getattr(settings, 'THOR_EXPIRE_TIME', 60*60*24)


def get_linked_expiry_time():
    return getattr(settings, 'THOR_LINKED_EXPIRE_TIME', 60*60*6)


def get_max_file_size():
    return getattr(settings, 'THOR_MAX_FILE_SIZE', 2*1024*1024)


def fq_encrypt_disabled():
    return getattr(settings, 'THOR_DISABLE_FQ_ENCRYPT', False)


def show_in_admin():
    return getattr(settings, 'THOR_ENABLE_ADMIN', True)


def get_size_error():
    return force_text(_("Uploaded file too large ( > %s )") % filesizeformat(get_max_file_size()))


def thor_upload_file_name(instance, filename):
    if len(filename) > 40:
        filename = filename[-40:]

    uuid_hex = uuid.uuid4().hex
    # This removes "False" from the filename, which helps us to distinct between empty values in widgets. :)
    filename = filename.replace('False', uuid_hex[3:8])
    return os.path.join(get_upload_path(), uuid_hex[:3], uuid_hex[3:], filename)


def human_readable_types(types):
    ret = ['.%s' % (x.split('/')[-1] if "/" in x else x) for x in types]
    return ', '.join(ret)


class TemporaryFileWrapper(models.Model):
    """ Holds an arbitrary file and notes when it was last accessed
    """
    file = models.FileField(upload_to=thor_upload_file_name)

    modified = models.DateTimeField(auto_now=True)
    md5sum = models.CharField(max_length=36, unique=True)

    content_type = models.CharField('content_type', max_length=128, default='application/unknown')
    linked = models.BooleanField(default=False)

    def __str__(self):
        return '%s%s' % (
            '[LINKED] ' if self.linked else '',
            self.file.name,
        )

    def get_hash(self):
        md5 = hashlib.md5()
        for chunk in self.file.chunks():
            md5.update(chunk)

        return md5.hexdigest()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.md5sum = self.get_hash()

        if not self.pk or TemporaryFileWrapper.objects.exclude(id=self.pk).filter(md5sum=self.md5sum).exists():
            try:
                # If replacing pk, we mark the file as unlinked.
                self.linked = False
                self.pk = TemporaryFileWrapper.objects.exclude(id=self.pk).get(md5sum=self.md5sum).pk
            except TemporaryFileWrapper.DoesNotExist:
                pass

        return super(TemporaryFileWrapper, self).save(force_insert, force_update, using, update_fields)

    @staticmethod
    def get_image_from_id(img_id, field_query):
        try:
            img_id = int(img_id)
        except (ValueError, TypeError):
            return None
        else:
            model = field_query[0]

            try:
                instance = model.objects.get(id=img_id)
            except model.DoesNotExist:
                return None
            else:
                return getattr(instance, field_query[1])


@receiver(post_delete, sender=TemporaryFileWrapper)
def cleanup_temporary_files(sender, instance, **kwargs):
    instance.file.close()
    storage, path = instance.file.storage, instance.file.path
    try:
        storage.delete(path)
    except IOError:
        pass


class FqCrypto(object):
    BLOCK_SIZE = 32
    PADDING = '{'

    @classmethod
    def _pad(cls, s):
        return s + (cls.BLOCK_SIZE - len(s) % cls.BLOCK_SIZE) * cls.PADDING

    @classmethod
    def _encode_aes(cls, c, s):
        return base64.b64encode(c.encrypt(cls._pad(s)))

    @classmethod
    def _decode_aes(cls, c, e):
        e = force_bytes(e, 'utf-8')
        pad = force_bytes(cls.PADDING, 'utf-8')

        return c.decrypt(base64.b64decode(e)).rstrip(pad)

    @classmethod
    def _cipher(cls):
        secret = settings.SECRET_KEY

        if len(secret) < cls.BLOCK_SIZE:
            secret = cls._pad(secret)
        else:
            secret = secret[:cls.BLOCK_SIZE]

        from Crypto.Cipher import AES
        return AES.new(secret)

    @classmethod
    def decode(cls, value):
        if fq_encrypt_disabled():
            return force_text(value)

        return force_text(cls._decode_aes(cls._cipher(), value))

    @classmethod
    def encode(cls, value):
        if fq_encrypt_disabled():
            return value

        return force_text(cls._encode_aes(cls._cipher(), value))
