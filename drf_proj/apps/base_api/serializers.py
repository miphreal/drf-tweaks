from collections import OrderedDict
import logging

from django.conf import settings
from rest_framework import serializers
from rest_framework.serializers import Serializer


logger = logging.getLogger(__name__)


class BaseSerializer(Serializer):
    depends_on_extra_object_attrs = ()

    def get_fields(self):
        if self.parent and self.parent.field_name:
            self._field_name_prefix = '{}__{}__'.format(self.parent.field_name, self.field_name)
        elif self.field_name:
            self._field_name_prefix = self.field_name + '__'
        else:
            self._field_name_prefix = ''

        output_fields = frozenset()

        if 'view' in self.context:
            view = self.context['view']
            output_fields = getattr(view, 'fetching_fields_external', output_fields)

        if self._field_name_prefix:
            output_fields = set(
                f for f in output_fields
                if f.startswith(self._field_name_prefix)
            )

        if output_fields:
            d = OrderedDict()
            for name, f in super(BaseSerializer, self).get_fields().items():
                name_path = self._field_name_prefix + name
                if name_path in output_fields:
                    d[name] = f

            return d

        return super(BaseSerializer, self).get_fields()

    @classmethod
    def get_model_fields(cls):
        model_fields = [decl.source or f for f, decl in cls._declared_fields.items() if decl.source != '*']
        model_fields.extend(cls.depends_on_extra_object_attrs)
        return set(model_fields)


class BaseModelSerializer(BaseSerializer, serializers.ModelSerializer):
    pass


class PaginationSerializerMixin(object):
    SERIALIZATION_OFFSET_PARAM = settings.PAGINATE_OFFSET_PARAM
    SERIALIZATION_PAGE_PARAM = settings.PAGINATE_PAGE_PARAM
    SERIALIZATION_LIMIT_PARAM = settings.REST_FRAMEWORK.get('PAGINATE_BY_PARAM', 'limit')

    class DummyPaginator(object):
        def __init__(self, object_list):
            self.object_list = object_list
            self.count = len(object_list)
            self.num_page = 1
            self.per_page = self.count

    class DummyOnePage(object):
        def __init__(self, object_list):
            self.object_list = object_list
            self.paginator = PaginationSerializerMixin.DummyPaginator(object_list)
            self.number = 1

        def __repr__(self):
            return '<Page 1 of 1>'

        def __len__(self):
            return len(self.object_list)

        def __getitem__(self, index):
            if not isinstance(index, (slice,)):
                raise TypeError
            if not isinstance(self.object_list, list):
                self.object_list = list(self.object_list)
            return self.object_list[index]

        def has_next(self):
            return False

        def has_previous(self):
            return False

        def has_other_pages(self):
            return False

        def next_page_number(self):
            return None

        def previous_page_number(self):
            return None

        def start_index(self):
            if not len(self):
                return 0
            return 1

        def end_index(self):
            return len(self)

    def serialized_pagination_page(self, page):
        return self.pagination_meta_format(
            count_items=page.paginator.count,
            limit=page.paginator.per_page,
            offset=page.paginator.count - page.paginator.per_page
        )

    def pagination_meta_format(self, offset, limit, count_items=None):
        page = 0
        if isinstance(offset, int) and offset > 0 and isinstance(limit, int) and limit:
            page = offset / limit

        return {
            'count': count_items,
            self.SERIALIZATION_LIMIT_PARAM: limit,
            self.SERIALIZATION_PAGE_PARAM: page,
            self.SERIALIZATION_OFFSET_PARAM: offset,
        }

