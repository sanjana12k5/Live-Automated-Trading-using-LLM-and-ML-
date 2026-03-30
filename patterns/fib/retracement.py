FIB_LEVELS = [0.382, 0.5, 0.618]

def calculate_fib(high, low):
    diff = high - low
    return {lvl: high - diff * lvl for lvl in FIB_LEVELS}
