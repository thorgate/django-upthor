from django.db.models.fields.files import ImageFieldFile, ImageFileDescriptor, FileDescriptor, FieldFile
from django.test import TestCase

from upthor.fields import ThorFileField, ThorImageField
from upthor.models import FqCrypto, get_upload_path, get_expiry_time, get_linked_expiry_time, fq_encrypt_disabled, \
    get_max_file_size, show_in_admin


class TestThorUpload(TestCase):

    FQ_VAL = 'FQ:test.ExampleModel.content'
    FQ_ENC = 'T4VqvMwM4iq8LvrC4N8VQCwJi2nwQ8TEGKd2vpVEkoc='
    FQ_ENC_LONG = 'xK8nzpQR90HzBJPGOSM4nbGEnuBsQJWRQgITiNkxTE0='

    def test_fq_encrypt(self):
        with self.settings(SECRET_KEY='F00BA4', THOR_DISABLE_FQ_ENCRYPT=False):
            encoded = FqCrypto.encode(self.FQ_VAL)
            self.assertEquals(encoded, self.FQ_ENC)
            self.assertEquals(FqCrypto.decode(encoded), self.FQ_VAL)

    def test_fq_encrypt_disable(self):
        with self.settings(SECRET_KEY='F00BA4', THOR_DISABLE_FQ_ENCRYPT=True):
            encoded = FqCrypto.encode(self.FQ_VAL)
            self.assertEquals(encoded, self.FQ_VAL)
            self.assertEquals(FqCrypto.decode(encoded), self.FQ_VAL)

    def test_fq_long_encrypt(self):
        with self.settings(SECRET_KEY='F00Basddsasasedqweqwasdeqweqwgkdfkdslfksflqi'
                                      'weuwiqeuqwieuiqweasdswqeqwewqeqweasds'
                                      'dasddasdsaasdasdsaddasA4', THOR_DISABLE_FQ_ENCRYPT=False):
            encoded = FqCrypto.encode(self.FQ_VAL)
            self.assertEquals(encoded, self.FQ_ENC_LONG)
            self.assertEquals(FqCrypto.decode(encoded), self.FQ_VAL)

    def test_settings_overwrite(self):
        with self.settings(THOR_UPLOAD_TO='other-path'):
            self.assertEquals(get_upload_path(), 'other-path')

        with self.settings(THOR_EXPIRE_TIME=500):
            self.assertEquals(get_expiry_time(), 500)

        with self.settings(THOR_LINKED_EXPIRE_TIME=666):
            self.assertEquals(get_linked_expiry_time(), 666)

        with self.settings(THOR_MAX_FILE_SIZE=666):
            self.assertEquals(get_max_file_size(), 666)

        with self.settings(THOR_DISABLE_FQ_ENCRYPT=True):
            self.assertEquals(fq_encrypt_disabled(), True)

        with self.settings(THOR_ENABLE_ADMIN=False):
            self.assertEquals(show_in_admin(), False)


class TestFieldAttrs(TestCase):

    def test_upthor_filefield_attrs(self):
        self.assertEquals(ThorFileField.attr_class, FieldFile)
        self.assertEquals(ThorFileField.descriptor_class, FileDescriptor)

    def test_upthor_imagefield_attrs(self):
        self.assertEquals(ThorImageField.attr_class, ImageFieldFile)
        self.assertEquals(ThorImageField.descriptor_class, ImageFileDescriptor)
