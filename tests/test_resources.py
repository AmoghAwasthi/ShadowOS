from shadowos.resources import Resource, ResourceManager


def test_resource_creation():
    resource = Resource("CPU", 4)

    assert resource.name == "CPU"
    assert resource.total_units == 4
    assert resource.available_units == 4


def test_resource_allocation():
    resource = Resource("CPU", 4)

    result = resource.allocate(2)

    assert result is True
    assert resource.available_units == 2


def test_resource_allocation_failure():
    resource = Resource("CPU", 2)

    result = resource.allocate(3)

    assert result is False
    assert resource.available_units == 2


def test_resource_release():
    resource = Resource("CPU", 4)

    resource.allocate(2)
    result = resource.release(1)

    assert result is True
    assert resource.available_units == 3


def test_create_resource():
    manager = ResourceManager()

    result = manager.create_resource("Memory", 8)

    assert result is True
    assert manager.get_resource("Memory") is not None


def test_process_resource_request():
    manager = ResourceManager()

    manager.create_resource("CPU", 4)

    result = manager.request_resource(
        1,
        "CPU",
        2
    )

    assert result is True

    assert manager.get_resource("CPU").available_units == 2

    assert manager.get_process_resources(1)["CPU"] == 2


def test_process_resource_release():
    manager = ResourceManager()

    manager.create_resource("CPU", 4)

    manager.request_resource(1, "CPU", 2)

    result = manager.release_resource(
        1,
        "CPU",
        1
    )

    assert result is True

    assert manager.get_resource("CPU").available_units == 3
    assert manager.get_process_resources(1)["CPU"] == 1


def test_release_all_resources():
    manager = ResourceManager()

    manager.create_resource("CPU", 4)
    manager.create_resource("Memory", 8)

    manager.request_resource(1, "CPU", 2)
    manager.request_resource(1, "Memory", 4)

    manager.release_all_resources(1)

    assert manager.get_resource("CPU").available_units == 4
    assert manager.get_resource("Memory").available_units == 8

    assert manager.get_process_resources(1) == {}


def test_invalid_resource_request():
    manager = ResourceManager()

    manager.create_resource("CPU", 2)

    result = manager.request_resource(
        1,
        "GPU",
        1
    )

    assert result is False


def test_process_cannot_release_unheld_resource():
    manager = ResourceManager()

    manager.create_resource("CPU", 4)

    result = manager.release_resource(
        1,
        "CPU",
        1
    )

    assert result is False