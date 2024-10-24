
def calculate_backoff_multiplier(number_of_tries, backoff_factor):
    return backoff_factor**number_of_tries
