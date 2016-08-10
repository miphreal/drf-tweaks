import json
from uuid import UUID
from django.contrib.sessions.serializers import JSONSerializer as BaseJSONSerializer


def _default(o):
    if isinstance(o, UUID):
        return o.hex
    raise TypeError('Cannot be serialized: %r' % o)


class JSONSerializer(BaseJSONSerializer):

    def dumps(self, obj):
        return json.dumps(obj, separators=(',', ':'), default=_default).encode('latin-1')
