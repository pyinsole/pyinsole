class ProviderError(Exception):
    pass


class ProviderRuntimeError(ProviderError):
    pass


class PyinsoleError(Exception):
    pass


class DeleteMessage(PyinsoleError):
    pass
