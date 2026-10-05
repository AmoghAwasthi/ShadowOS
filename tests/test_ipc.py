from shadowos.ipc import IPCManager, Message


def test_message_creation():
    message = Message(1, 2, "Hello")

    assert message.sender_pid == 1
    assert message.receiver_pid == 2
    assert message.data == "Hello"


def test_register_process():
    ipc = IPCManager()

    ipc.register_process(1)

    assert 1 in ipc.message_queues
    assert ipc.get_queue_size(1) == 0


def test_send_message():
    ipc = IPCManager()

    ipc.register_process(1)
    ipc.register_process(2)

    result = ipc.send_message(
        1,
        2,
        "Hello Process 2"
    )

    assert result is True
    assert ipc.get_queue_size(2) == 1


def test_receive_message():
    ipc = IPCManager()

    ipc.register_process(1)
    ipc.register_process(2)

    ipc.send_message(
        1,
        2,
        "Hello"
    )

    message = ipc.receive_message(2)

    assert message is not None
    assert message.sender_pid == 1
    assert message.receiver_pid == 2
    assert message.data == "Hello"

    assert ipc.get_queue_size(2) == 0


def test_fifo_message_order():
    ipc = IPCManager()

    ipc.register_process(1)
    ipc.register_process(2)

    ipc.send_message(1, 2, "First")
    ipc.send_message(1, 2, "Second")
    ipc.send_message(1, 2, "Third")

    first = ipc.receive_message(2)
    second = ipc.receive_message(2)
    third = ipc.receive_message(2)

    assert first.data == "First"
    assert second.data == "Second"
    assert third.data == "Third"


def test_receive_empty_queue():
    ipc = IPCManager()

    ipc.register_process(1)

    message = ipc.receive_message(1)

    assert message is None


def test_send_to_invalid_process():
    ipc = IPCManager()

    ipc.register_process(1)

    result = ipc.send_message(
        1,
        999,
        "Invalid receiver"
    )

    assert result is False