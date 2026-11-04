def call():
    return 1


def run():
    for _ in range(3):
        try:
            call()
        except Exception:
            continue
