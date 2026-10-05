"""
Tests for the SHADOWOS thread subsystem.
"""

from shadowos.process import ProcessManager
from shadowos.threads import ThreadManager, ThreadState


def test_thread_creation():
    """
    Verify that a thread can be created.
    """

    thread_manager = ThreadManager()

    thread = thread_manager.create_thread(
        process_id=1,
        name="WorkerThread"
    )

    assert thread.tid == 1

    assert thread.process_id == 1

    assert thread.state == ThreadState.READY


def test_thread_execution():
    """
    Verify that a thread can run and consume CPU time.
    """

    thread_manager = ThreadManager()

    thread = thread_manager.create_thread(
        process_id=1,
        name="WorkerThread"
    )

    # Start the thread.
    thread.run()

    assert thread.state == ThreadState.RUNNING

    # Give it one CPU tick.
    thread.run_one_tick()

    assert thread.cpu_ticks == 1


def test_thread_block_and_unblock():
    """
    Verify:

        RUNNING -> BLOCKED -> READY
    """

    thread_manager = ThreadManager()

    thread = thread_manager.create_thread(
        process_id=1,
        name="WorkerThread"
    )

    thread.run()

    thread.block()

    assert thread.state == ThreadState.BLOCKED

    thread.unblock()

    assert thread.state == ThreadState.READY


def test_thread_termination():
    """
    Verify that a thread can be terminated.
    """

    thread_manager = ThreadManager()

    thread = thread_manager.create_thread(
        process_id=1,
        name="WorkerThread"
    )

    thread.terminate()

    assert thread.state == ThreadState.TERMINATED


def test_process_can_contain_threads():
    """
    Verify that threads can be attached to a process.
    """

    process_manager = ProcessManager()
    thread_manager = ThreadManager()

    # Create a process.
    process = process_manager.create_process(
        name="DataProcessor",
        priority=2,
        burst_time=5
    )

    # Create two threads for that process.
    thread1 = thread_manager.create_thread(
        process_id=process.pid,
        name="Worker1"
    )

    thread2 = thread_manager.create_thread(
        process_id=process.pid,
        name="Worker2"
    )

    # Attach both threads to the process.
    process.add_thread(thread1)
    process.add_thread(thread2)

    # The process should now contain two threads.
    assert len(process.get_threads()) == 2

    assert process.get_threads()[0] == thread1
    assert process.get_threads()[1] == thread2