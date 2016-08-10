from rest_framework.filters import OrderingFilter


class CustomOrderingBackend(OrderingFilter):

    def remove_invalid_fields(self, queryset, fields, view):
        valid_ordering = super(CustomOrderingBackend, self).remove_invalid_fields(
            queryset=queryset, fields=fields, view=view)
        ordering_aliases = getattr(view, 'ordering_aliases', {})

        result_ordering = []
        for term in fields:
            cleaned_name = term.lstrip('-').partition('__')[0]
            if term in valid_ordering:
                result_ordering.append(term)
            elif cleaned_name in ordering_aliases:
                result_ordering.append(
                    ('-' if term.startswith('-') else '') + ordering_aliases[cleaned_name]
                )
        return result_ordering

    def get_ordering(self, request, queryset, view):
        ordering = super(CustomOrderingBackend, self).get_ordering(request, queryset, view)
        if not ordering:
            return None
        return ordering
