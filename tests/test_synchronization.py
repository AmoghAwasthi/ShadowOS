"""
Tests for SHADOWOS synchronization primitives.

These tests verify:

1. Mutex locking
2. Mutex blocking
3. Mutex release
4. Semaphore behaviour
5. Shared resource access
"""


from shadowos.threads import ThreadManager, ThreadState
from shadowos.synchronization import (
    Mutex,
    Semaphore,
    SharedResource
)


# =============================================================
# MUTEX TESTS
# =============================================================


def test_mutex_acquire():
    """
    Verify that a thread can acquire a free mutex.
    """

    thread_manager = ThreadManager()

    thread = thread_manager.create_thread(
        process_id=1,
        name="Thread1"
    )

    mutex = Mutex("DatabaseLock")

    result = mutex.acquire(thread)

    assert result is True

    assert mutex.is_locked() is True

    assert mutex.get_owner() == thread.tid


def test_mutex_blocks_second_thread():
    """
    Verify that only one thread can own a mutex.

    T1 -> acquires mutex
    T2 -> becomes BLOCKED
    """

    thread_manager = ThreadManager()

    thread1 = thread_manager.create_thread(
        process_id=1,
        name="Thread1"
    )

    thread2 = thread_manager.create_thread(
        process_id=1,
        name="Thread2"
    )

    mutex = Mutex("DatabaseLock")

    # T1 gets the lock.
    assert mutex.acquire(thread1) is True

    # T2 should not be able to get it.
    assert mutex.acquire(thread2) is False

    # T2 should now be BLOCKED.
    assert thread2.state == ThreadState.BLOCKED


def test_mutex_release():
    """
    Verify that releasing a mutex allows another
    waiting thread to continue.
    """

    thread_manager = ThreadManager()

    thread1 = thread_manager.create_thread(
        process_id=1,
        name="Thread1"
    )

    thread2 = thread_manager.create_thread(
        process_id=1,
        name="Thread2"
    )

    mutex = Mutex("DatabaseLock")

    # T1 gets the mutex.
    mutex.acquire(thread1)

    # T2 attempts to get it and becomes blocked.
    mutex.acquire(thread2)

    assert thread2.state == ThreadState.BLOCKED

    # T1 releases the mutex.
    mutex.release(thread1)

    # T2 should be woken up.
    assert thread2.state == ThreadState.READY


def test_wrong_thread_cannot_release_mutex():
    """
    A thread that does not own the mutex should not
    be able to release it.
    """

    thread_manager = ThreadManager()

    thread1 = thread_manager.create_thread(
        process_id=1,
        name="Owner"
    )

    thread2 = thread_manager.create_thread(
        process_id=1,
        name="Attacker"
    )

    mutex = Mutex("ProtectedResource")

    mutex.acquire(thread1)

    # T2 attempts an illegal release.
    result = mutex.release(thread2)

    assert result is False

    # T1 should still own the mutex.
    assert mutex.get_owner() == thread1.tid


# =============================================================
# SEMAPHORE TESTS
# =============================================================


def test_semaphore_allows_available_resources():
    """
    A semaphore with count=2 should allow two threads
    to acquire the resource.
    """

    thread_manager = ThreadManager()

    thread1 = thread_manager.create_thread(
        process_id=1,
        name="Thread1"
    )

    thread2 = thread_manager.create_thread(
        process_id=1,
        name="Thread2"
    )

    semaphore = Semaphore(
        "DatabaseConnections",
        initial_count=2
    )

    assert semaphore.wait(thread1) is True

    assert semaphore.wait(thread2) is True

    assert semaphore.get_count() == 0


def test_semaphore_blocks_when_empty():
    """
    Once all semaphore resources are consumed,
    another thread should become BLOCKED.
    """

    thread_manager = ThreadManager()

    thread1 = thread_manager.create_thread(
        process_id=1,
        name="Thread1"
    )

    thread2 = thread_manager.create_thread(
        process_id=1,
        name="Thread2"
    )

    thread3 = thread_manager.create_thread(
        process_id=1,
        name="Thread3"
    )

    semaphore = Semaphore(
        "DatabaseConnections",
        initial_count=2
    )

    semaphore.wait(thread1)
    semaphore.wait(thread2)

    # No resources remain.
    result = semaphore.wait(thread3)

    assert result is False

    assert thread3.state == ThreadState.BLOCKED


def test_semaphore_signal_wakes_thread():
    """
    signal() should make another resource available
    and wake a waiting thread.
    """

    thread_manager = ThreadManager()

    thread1 = thread_manager.create_thread(
        process_id=1,
        name="Thread1"
    )

    thread2 = thread_manager.create_thread(
        process_id=1,
        name="Thread2"
    )

    semaphore = Semaphore(
        "ResourcePool",
        initial_count=1
    )

    # T1 consumes the only resource.
    semaphore.wait(thread1)

    # T2 must wait.
    semaphore.wait(thread2)

    assert thread2.state == ThreadState.BLOCKED

    # Return the resource.
    semaphore.signal()

    # T2 should wake up.
    assert thread2.state == ThreadState.READY


# =============================================================
# SHARED RESOURCE TESTS
# =============================================================


def test_shared_resource_read_write():
    """
    Verify that a shared resource can be read and written.
    """

    resource = SharedResource(
        name="Counter",
        initial_value=0
    )

    assert resource.read() == 0

    resource.write(10)

    assert resource.read() == 10


def test_shared_resource_increment():
    """
    Verify that the shared resource can be incremented.
    """

    resource = SharedResource(
        name="Counter",
        initial_value=0
    )

    resource.increment()

    assert resource.read() == 1