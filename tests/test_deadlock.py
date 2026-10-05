from shadowos.resources import ResourceManager


def test_no_deadlock():

    manager = ResourceManager()

    manager.create_resource("CPU", 2)

    manager.request_resource(
        1,
        "CPU",
        1
    )

    result = manager.detect_deadlock()

    assert result == []


def test_detect_deadlock():

    manager = ResourceManager()

    # Two resources with one unit each.
    manager.create_resource("ResourceA", 1)
    manager.create_resource("ResourceB", 1)

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

    # PID 1 now waits for Resource B.
    assert not manager.request_resource(
        1,
        "ResourceB",
        1
    )

    # PID 2 now waits for Resource A.
    assert not manager.request_resource(
        2,
        "ResourceA",
        1
    )

    # This creates:
    #
    # PID 1 -> PID 2
    # PID 2 -> PID 1
    #
    # Therefore a deadlock exists.

    deadlocked = manager.detect_deadlock()

    assert 1 in deadlocked
    assert 2 in deadlocked
    