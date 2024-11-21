class ProviderError(Exception):
    pass


class ProviderRuntimeError(ProviderError):
    pass


class PyinsoleError(Exception):
    pass


class DeleteMessage(PyinsoleError):  # noqa: N818
    pass
