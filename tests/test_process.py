"""
Basic tests for the SHADOWOS process lifecycle.

These tests help us verify that the process state
transitions are working correctly.
"""

from shadowos.process import ProcessManager, ProcessState


def test_process_creation():
    """
    Verify that a newly created process eventually
    becomes READY.
    """

    manager = ProcessManager()

    process = manager.create_process(
        name="TestProcess",
        priority=1,
        burst_time=3
    )

    # The first process should receive PID 1.
    assert process.pid == 1

    # After creation, it should be READY.
    assert process.state == ProcessState.READY


def test_process_blocking():
    """
    Verify:

        READY -> BLOCKED
    """

    manager = ProcessManager()

    process = manager.create_process(
        name="TestProcess",
        priority=1,
        burst_time=3
    )

    # Ask the ProcessManager to block the process.
    manager.block_process(process.pid)

    assert process.state == ProcessState.BLOCKED


def test_process_unblocking():
    """
    Verify:

        BLOCKED -> READY
    """

    manager = ProcessManager()

    process = manager.create_process(
        name="TestProcess",
        priority=1,
        burst_time=3
    )

    manager.block_process(process.pid)

    # The process was blocked, so it can now be unblocked.
    manager.unblock_process(process.pid)

    assert process.state == ProcessState.READY


def test_process_termination():
    """
    Verify:

        READY -> TERMINATED
    """

    manager = ProcessManager()

    process = manager.create_process(
        name="TestProcess",
        priority=1,
        burst_time=3
    )

    manager.terminate_process(process.pid)

    assert process.state == ProcessState.TERMINATED


def test_process_execution():
    """
    Verify that a process can execute CPU time
    and eventually terminate.
    """

    manager = ProcessManager()

    process = manager.create_process(
        name="TestProcess",
        priority=1,
        burst_time=2
    )

    # The scheduler normally calls run().
    process.run()

    assert process.state == ProcessState.RUNNING

    # First CPU tick.
    process.run_one_tick()

    # One tick should remain.
    assert process.remaining_time == 1

    # Second CPU tick.
    process.run_one_tick()

    # No CPU time remains, so the process terminates.
    assert process.state == ProcessState.TERMINATED