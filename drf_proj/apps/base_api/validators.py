import base64
import binascii
import imghdr
import mimetypes
import uuid

from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .codes import Codes
from .exceptions import ApiValidationError


class BaseValidator(serializers.Serializer):
    pass


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            mime_type, tmp, base64_data = data.partition(';base64,')
            mime_type = mime_type[5:]

            if base64_data:
                try:
                    decoded_file = base64.b64decode(base64_data)
                except (TypeError, binascii.Error):
                    pass
                else:
                    file_name = '{}{}'.format(uuid.uuid4().hex, self.get_extension(decoded_file, mime_type))
                    data = ContentFile(decoded_file, name=file_name)
                    return super(Base64ImageField, self).to_internal_value(data)

        raise ApiValidationError(_('Please upload a valid image.'), code=Codes.ValidationAliases.INVALID_IMAGE)

    def to_representation(self, value):
        return value.name

    def get_extension(self, data, mime_type):
        ext = imghdr.what(None, data)

        if not ext:
            ext = mimetypes.guess_extension(mime_type)
        else:
            ext = '.' + ext

        return ext