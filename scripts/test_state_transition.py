from main import apply_stock_result


CASES = [
    (False, False, False, True, "False -> False"),
    (False, True, True, True, "False -> True"),
    (True, True, False, True, "True -> True"),
    (True, False, False, True, "True -> False"),
    (False, None, False, False, "False -> Unknown"),
]


failures = 0
for previous, current, should_notify, should_save, label in CASES:
    notifications = []
    saved_values = []
    result = apply_stock_result(
        previous,
        current,
        client=None,
        notify=lambda _client: notifications.append(True),
        persist=saved_values.append,
    )
    passed = (
        bool(notifications) is should_notify
        and bool(saved_values) is should_save
        and result is (current if current is not None else previous)
    )
    failures += not passed
    print(f"{'PASS' if passed else 'FAIL'} | {label} | notified={bool(notifications)} saved={saved_values}")

raise SystemExit(1 if failures else 0)
