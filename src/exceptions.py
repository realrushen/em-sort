class EMSortException(Exception):
    pass


class UnsupportedMarkerFormatException(EMSortException):
    pass


class UnsupportedTypeException(EMSortException):
    pass


class InvalidMarkersPairException(EMSortException):
    pass


class SheetDoesNotExistsException(EMSortException):
    pass
