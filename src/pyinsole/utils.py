def calculate_backoff_multiplier(number_of_tries: int, backoff_factor: float) -> float:
    return backoff_factor**number_of_tries
