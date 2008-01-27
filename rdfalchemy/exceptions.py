class RDFAlchemyError(Exception):
    """Generic error class."""


class ArgumentError(RDFAlchemyError):
    """Raised for all those conditions where invalid arguments are
    sent to constructed objects.  This error generally corresponds to
    construction time state errors.
    """





