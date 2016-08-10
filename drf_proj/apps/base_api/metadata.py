from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework.metadata import SimpleMetadata
from rest_framework.request import clone_request
from rest_framework import exceptions


class CustomMetadata(SimpleMetadata):
    """Exposes `validator_class` if available"""
    def determine_actions(self, request, view):
        actions = {}
        for method in {'PUT', 'POST'} & set(view.allowed_methods):
            view.request = clone_request(request, method)
            try:
                if hasattr(view, 'check_permissions'):
                    view.check_permissions(view.request)
                if method == 'PUT' and hasattr(view, 'get_object'):
                    view.get_object()
            except (exceptions.APIException, PermissionDenied, Http404):
                pass
            else:
                # try to get `validator` first
                serializer = view.get_validator() if hasattr(view, 'get_validator') else view.get_serializer()
                actions[method] = self.get_serializer_info(serializer)
            finally:
                view.request = request

        return actions
