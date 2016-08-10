class PaginatorError(Exception):
    """Base paginator exception"""


class InvalidOffsetError(PaginatorError):
    """Incorrect `offset` parameter"""


class InvalidPageError(PaginatorError):
    """Incorrect `page` parameter"""


class InvalidLimitError(PaginatorError):
    """Incorrect `limit` parameter"""


class OffsetPaginator(object):
    ALL_ITEMS_FLAGS = (-1, 'all', '-1')
    ALL_ITEMS_LIMIT_VALUE = None

    DEFAULT_OFFSET = 0
    DEFAULT_LIMIT = 10
    DEFAULT_PAGE = 0

    NOT_SET = object()

    def __init__(self, collection, limit=DEFAULT_LIMIT, **params):
        """This paginator slices frame of items using offset/limit concept

        :param collection: iterable object that contains all items
        :param offset: start position of slicing (values None, [0, +inf])
        :param limit: count of items to slice (values [0, +inf]); page size
        :param page: if offset is None, the page param can be used to paginate
                     through collection (values None, [0, +inf]); `offset` has a higher
                     priority
        """
        self._all_items = collection
        self._offset = self.validate_offset(params.get('offset'))
        self._page = self.validate_page(params.get('page'))
        self._limit = self.validate_limit(limit)
        self._start, self._end = self.DEFAULT_OFFSET, self.DEFAULT_OFFSET + self.DEFAULT_LIMIT

        self._init_start_end_edge()

    def _init_start_end_edge(self):
        # offset/limit mode ?
        if self._is_num(self._offset):
            self._start = self._offset
            self._end = (self._limit
                         if self._limit == self.ALL_ITEMS_LIMIT_VALUE
                         else self._start + self._limit)

        elif self._limit == self.ALL_ITEMS_LIMIT_VALUE:
            self._end = self._limit

        # page/page size mode ?
        elif self._is_num(self._page):
            self._start = self._page * self._limit
            self._end = self._start + self._limit

        elif not self._is_num(self._offset):
            self._end = self._start + self._limit

    def to_number(self, val, *default):
        if self._is_num(val):
            return val

        if self._is_str(val) and val.lstrip('-').isdigit():
            return int(val)

        if default:
            return default[0]
        return None

    def _is_num(self, value):
        return isinstance(value, int)

    def _is_str(self, value):
        return isinstance(value, str)

    def validate_offset(self, offset):
        offset = self.to_number(offset, self.NOT_SET)
        if self._is_num(offset) and offset >= 0 or offset is self.NOT_SET:
            return offset
        raise InvalidOffsetError()

    def validate_page(self, page):
        page = self.to_number(page, self.NOT_SET)
        if self._is_num(page) and page >= 0 or page is self.NOT_SET:
            return page
        raise InvalidPageError()

    def validate_limit(self, limit):
        if limit in self.ALL_ITEMS_FLAGS:
            return self.ALL_ITEMS_LIMIT_VALUE

        if limit is None or limit is self.NOT_SET:
            return self.DEFAULT_LIMIT

        limit = self.to_number(limit)
        if isinstance(limit, int) and limit >= 0:
            return limit
        raise InvalidLimitError()

    def get_frame(self):
        """Performs slicing of collection

        :return: slice of items according to offset/limit/page values
        """
        return self._all_items[slice(self.start, self.end)]

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end
