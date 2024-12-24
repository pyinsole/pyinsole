import sentry_sdk


def sentry_handler(*, delete_message: bool = False):
    async def send_to_sentry(exc_info: BaseException, message: str):
        scope: sentry_sdk.Scope = sentry_sdk.get_current_scope()
        scope.set_extra("message", message)
        sentry_sdk.capture_exception(exc_info)
        return delete_message

    return send_to_sentry
