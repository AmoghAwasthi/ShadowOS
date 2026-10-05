from shadowos.resources import ResourceManager


def test_deadlock_recovery():

    manager = ResourceManager()

    # Create two resources.
    manager.create_resource(
        "ResourceA",
        1
    )

    manager.create_resource(
        "ResourceB",
        1
    )

    # PID 1 gets Resource A.
    assert manager.request_resource(
        1,
        "ResourceA",
        1
    )

    # PID 2 gets Resource B.
    assert manager.request_resource(
        2,
        "ResourceB",
        1
    )

    # PID 1 waits for Resource B.
    assert not manager.request_resource(
        1,
        "ResourceB",
        1
    )

    # PID 2 waits for Resource A.
    assert not manager.request_resource(
        2,
        "ResourceA",
        1
    )

    # Detect the deadlock.
    deadlocked = manager.detect_deadlock()

    assert 1 in deadlocked
    assert 2 in deadlocked

    # Recover from the deadlock.
    victim = manager.recover_from_deadlock(
        deadlocked
    )

    # Highest PID should be selected.
    assert victim == 2

    # PID 2 should no longer have allocations.
    assert 2 not in manager.allocations

    # Resource B should now be available.
    resource_b = manager.get_resource(
        "ResourceB"
    )

    assert resource_b.available_units == 1
    