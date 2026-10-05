"""
SHADOWOS Synchronization Demonstration.

This demo shows two threads competing for a shared resource.

We will demonstrate:

    Thread 1 -> acquire mutex
    Thread 2 -> attempt mutex
    Thread 2 -> BLOCKED
    Thread 1 -> release mutex
    Thread 2 -> READY

This simulates mutual exclusion in an operating system.
"""


from shadowos.threads import ThreadManager
from shadowos.synchronization import Mutex, SharedResource


def main():

    print("\n========================================")
    print(" SHADOWOS SYNCHRONIZATION DEMO")
    print("========================================\n")

    # ---------------------------------------------------------
    # STEP 1: Create two simulated threads
    # ---------------------------------------------------------

    thread_manager = ThreadManager()

    thread1 = thread_manager.create_thread(
        process_id=1,
        name="DatabaseWriter"
    )

    thread2 = thread_manager.create_thread(
        process_id=1,
        name="DatabaseReader"
    )

    # ---------------------------------------------------------
    # STEP 2: Create a shared resource
    # ---------------------------------------------------------

    database = SharedResource(
        name="DatabaseCounter",
        initial_value=0
    )

    # ---------------------------------------------------------
    # STEP 3: Create a mutex
    # ---------------------------------------------------------

    database_lock = Mutex(
        name="DatabaseLock"
    )

    print("\n--- Thread 1 attempts to access database ---")

    # Thread 1 acquires the mutex.
    database_lock.acquire(thread1)

    # Thread 1 is now allowed to access the resource.
    thread1.run()

    database.increment()

    print(
        f"Database value = {database.read()}"
    )

    # ---------------------------------------------------------
    # STEP 4: Thread 2 attempts access
    # ---------------------------------------------------------

    print("\n--- Thread 2 attempts to access database ---")

    # Thread 2 attempts to acquire the same mutex.
    database_lock.acquire(thread2)

    print(
        f"Thread 2 state = {thread2.state.value}"
    )

    # ---------------------------------------------------------
    # STEP 5: Thread 1 finishes
    # ---------------------------------------------------------

    print("\n--- Thread 1 releases database ---")

    database_lock.release(thread1)

    print(
        f"Thread 2 state = {thread2.state.value}"
    )

    # ---------------------------------------------------------
    # STEP 6: Thread 2 now gets access
    # ---------------------------------------------------------

    print("\n--- Thread 2 accesses database ---")

    database_lock.acquire(thread2)

    thread2.run()

    database.increment()

    print(
        f"Database value = {database.read()}"
    )

    # ---------------------------------------------------------
    # FINAL STATE
    # ---------------------------------------------------------

    print("\n========================================")
    print(" FINAL RESULT")
    print("========================================")

    print(
        f"Database counter = {database.read()}"
    )

    print(
        f"Thread 1 = {thread1.state.value}"
    )

    print(
        f"Thread 2 = {thread2.state.value}"
    )


if __name__ == "__main__":
    main()
    