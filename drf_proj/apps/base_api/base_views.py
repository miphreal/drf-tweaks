from collections import Iterable
import re
from uuid import UUID

from django.conf import settings
from rest_framework import viewsets, exceptions, serializers, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from semantic_version import Version, Spec

from .paginators import OffsetPaginator
from .renderers import camelize
from .serializers import PaginationSerializerMixin


uuid_re = re.compile(r'[a-f0-9]{32}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


class PaginationValidator(serializers.Serializer):
    page = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    offset = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    limit = serializers.IntegerField(min_value=-1, required=False, allow_null=True,
                                     max_value=settings.REST_FRAMEWORK['MAX_PAGINATE_BY'])


class BaseView(viewsets.GenericViewSet, PaginationSerializerMixin):
    ordering_fields = '__all__'
    ordering_aliases = {}
    ordering = ()

    lookup_value_regex = uuid_re.pattern

    page_kwarg = settings.PAGINATE_PAGE_PARAM
    offset_kwarg = settings.PAGINATE_OFFSET_PARAM
    limit_kwarg = settings.PAGINATE_LIMIT_PARAM
    pagination_validator_class = PaginationValidator

    serializer_class = serializers.Serializer
    validator_class = serializers.Serializer

    default_fetching_fields = frozenset()
    fetching_fields_aliases = None  # Map {external alias: internal name}
    fetching_fieldsets = None

    default_limit = None

    rst_doc = None

    def filter_queryset(self, queryset):
        from django.core.exceptions import ValidationError
        try:
            return super(BaseView, self).filter_queryset(queryset=queryset)
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.message_dict)

    def _prepare_response(self, data):
        if isinstance(data, Iterable):
            return self._serialize_collection(data)
        return self._serialize_obj(data)

    def _serialize_collection(self, collection):
        return self._serialize_obj(collection, many=True)

    def _serialize_obj(self, obj, many=False):
        return self.get_serializer_class()(
            instance=obj,
            context=self.get_serializer_context(),
            many=many
        ).data

    def get_validator_class(self):
        return self.validator_class

    def get_validator_context(self):
        return self.get_serializer_context()

    def get_validator(self, instance=None, data=None, many=False, partial=False):
        """Return the validator instance that should be used for validating input"""
        validator_class = self.get_validator_class()
        context = self.get_validator_context()
        return validator_class(
            instance, data=data, many=many, partial=partial, context=context
        )

    def get_object_pk(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        return self.kwargs.get(lookup_url_kwarg, None)

    @property
    def is_collection_api_call(self):
        return self.suffix == 'List'

    def is_pk(self, value):
        if isinstance(value, int):
            return True

        try:
            UUID(value)
            return True
        except ValueError:
            return False

    @property
    def is_json_negotiation(self):
        return self.request.accepted_media_type == 'application/json'

    @property
    def fetching_fields(self):
        if hasattr(self, '_fetching_fields_internal'):
            return self._fetching_fields_internal

        fetching_fields = self.request.query_params.get('fields', '')
        fetching_fields = fetching_fields.replace('.', '__')
        if fetching_fields or self.default_fetching_fields:
            _fields = set()
            fetching_fields = fetching_fields.split(',') if fetching_fields else self.default_fetching_fields

            for f in fetching_fields:
                _fields.add(f)
                if '__' in f:
                    p = f.split('__')
                    while p:
                        _fields.add('__'.join(p))
                        p = p[:-1]
            fetching_fields = _fields
        else:
            fetching_fields = frozenset()

        if self.fetching_fieldsets:
            for field_set, fields in self.fetching_fieldsets.items():
                if field_set in fetching_fields:
                    fetching_fields.discard(field_set)
                    fetching_fields.update(fields)

        self._fetching_fields_external = fetching_fields.copy() or frozenset()

        # replace aliases in `fetching_fields` to use internally
        if self.fetching_fields_aliases:
            _aliases = fetching_fields.intersection(self.fetching_fields_aliases)
            if _aliases:
                for _alias in _aliases:
                    # fetching_fields.remove(_alias)
                    fetching_fields.add(self.fetching_fields_aliases[_alias])

        self._fetching_fields_internal = fetching_fields or frozenset()
        return fetching_fields

    @property
    def fetching_fields_external(self):
        if hasattr(self, '_fetching_fields_external'):
            return self._fetching_fields_external

        self.fetching_fields  # do not remove. it populates `self._fetching_fields_external`
        return self._fetching_fields_external

    @property
    def version(self):
        try:
            return Version(self.request.version, partial=True)
        except AttributeError:
            return Version(settings.REST_FRAMEWORK['DEFAULT_VERSION'])

    def check_version(self, spec):
        return self.version in Spec(spec)


class BaseReadView(BaseView):
    return_total_number = False

    def _prepare_filtered_qs(self, qs):
        return qs

    def retrieve(self, request, *args, **kwargs):
        return Response(data=self._prepare_response(self.get_object()))

    def _get_collection(self):
        qs = self.filter_queryset(self.get_queryset())
        return self._prepare_filtered_qs(qs=qs), qs

    def _get_paginator(self):
        from functools import partial

        page = self.request.query_params.get(self.page_kwarg)
        offset = self.request.query_params.get(self.offset_kwarg)
        limit = self.request.query_params.get(self.limit_kwarg, self.default_limit)

        pagination_validator = self.pagination_validator_class(data={'page': page, 'offset': offset, 'limit': limit})
        pagination_validator.is_valid(raise_exception=True)

        return partial(OffsetPaginator, limit=limit, offset=offset, page=page)

    def _prepare_paginated_response(self, paginator, total_items_count):
        response = Response(data=self._prepare_response(paginator.get_frame()))
        response.extra = dict(
            meta=camelize(self.pagination_meta_format(
                count_items=total_items_count,
                limit=(paginator.end - paginator.start
                       if paginator.end is not None
                       else first(paginator.ALL_ITEMS_FLAGS)),
                offset=paginator.start)))
        return response

    def list(self, request, *args, **kwargs):
        paginator = self._get_paginator()
        collection, all_items = self._get_collection()
        paginator = self.collection_paginator = paginator(collection=collection)

        total_items_count = None
        if all_items is not None and self.return_total_number:
            if hasattr(all_items, 'count'):
                total_items_count = all_items.count()
            else:
                total_items_count = len(all_items)

        return self._prepare_paginated_response(
            paginator=paginator, total_items_count=total_items_count)


class CreationViewMixin(object):
    def perform_create(self, validator):
        return validator.save()

    def create(self, request, *args, **kwargs):
        validator = self.get_validator(data=request.data)
        validator.is_valid(raise_exception=True)
        obj = self.perform_create(validator)
        data = self._serialize_obj(obj)
        return Response(data=data, status=status.HTTP_201_CREATED)


class UpdateViewMixin(object):
    def perform_update(self, validator):
        return validator.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        validator = self.get_validator(instance, data=request.data, partial=partial)
        validator.is_valid(raise_exception=True)
        obj = self.perform_update(validator)
        return Response(self._serialize_obj(obj), status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class DestroyViewMixin(object):
    allow_destroy_collection = False

    def destroy(self, request, *args, **kwargs):
        resp = None
        if self.lookup_field not in self.kwargs:
            if self.allow_destroy_collection:
                qs = self.filter_queryset(self.get_queryset())
                resp = self.perform_destroy_collection(queryset=qs)
            else:
                raise MethodNotAllowed('DELETE')
        else:
            instance = self.get_object()
            resp = self.perform_destroy(instance)

        if isinstance(resp, Response):
            return resp
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def perform_destroy_collection(self, queryset):
        queryset.delete()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


#
# View Mixins
class CommonFetchMixin(object):
    select_related = ()
    prefetch_related = ()

    def is_fetchable_field(self, field_name):
        fields = self.fetching_fields
        return bool(fields and field_name in fields) or not fields

    def _qs_fetch_related(self, qs):
        if not self.select_related and not self.prefetch_related:
            return qs

        need_to_fetch = set(self.prefetch_related).union(self.select_related)
        need_to_skip = set(f for f in need_to_fetch if not self.is_fetchable_field(f))

        need_to_fetch = need_to_fetch - need_to_skip

        prefetch_related = list(need_to_fetch.intersection(self.prefetch_related))
        select_related = list(need_to_fetch.intersection(self.select_related))

        if select_related:
            qs = qs.select_related(*select_related)

        if prefetch_related:
            qs = qs.prefetch_related(*prefetch_related)

        return qs


class CRUDMixin(CreationViewMixin, UpdateViewMixin, DestroyViewMixin, BaseReadView):
    """Combines all mixins for CRUD operations and underlying base view."""


class PerActionCustomValidatorMixin(object):
    """Allows to specify custom validator for each action.
    Available actions:
    - `create`
    - `update`
    - `partial_update`
    """
    validator_classes = {}

    def get_validator_class(self):
        return self.validator_classes.get(self.action, self.validator_class)


class PerActionCustomSerializerMixin(object):
    """Allows to specify custom serializer for each action.
    Available actions:
    - `list`
    - `retrieve`
    - `create`
    - `update`
    - `partial_update`
    """
    serializer_classes = {}

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)


class PerActionCustomPermissionsMixin(object):
    """Allows to specify custom permissions for each action.
    Available actions:
    - `list`
    - `retrieve`
    - `create`
    - `update`
    - `partial_update`
    - `destroy`
    """
    action_permissions = {}

    def get_permissions(self):
        permissions = super(PerActionCustomPermissionsMixin, self).get_permissions()
        _perms = self.action_permissions.get(self.action) or ()
        permissions.extend(p() for p in _perms)
        return permissions
