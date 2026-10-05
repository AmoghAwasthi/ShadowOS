"""
Synchronization primitives for SHADOWOS.

Operating systems need synchronization because multiple
threads/processes may access the same shared resource.

Example:

    Thread T1 ─────┐
                   │
                   ▼
              Shared Data
                   ▲
                   │
    Thread T2 ─────┘

Without synchronization, both threads may modify the
resource at the same time and cause a race condition.

This module currently provides:

1. Mutex
2. Semaphore
3. SharedResource

These are simulated OS primitives. They are not Python's
real threading.Lock or threading.Semaphore.
"""


# =============================================================
# MUTEX
# =============================================================


class Mutex:
    """
    A Mutex provides mutual exclusion.

    Only ONE thread can own a mutex at a time.

    Example:

        T1 -> acquire() -> SUCCESS
        T2 -> acquire() -> BLOCKED

        T1 -> release()

        T2 -> acquire() -> SUCCESS
    """

    def __init__(self, name):

        # Human-readable name for the mutex.
        self.name = name

        # True when some thread currently owns the mutex.
        self.locked = False

        # TID of the thread that owns the mutex.
        self.owner = None

        # Threads waiting for this mutex.
        self.waiting_threads = []

    # ---------------------------------------------------------
    # ACQUIRE
    # ---------------------------------------------------------

    def acquire(self, thread):
        """
        Attempt to acquire the mutex.

        Returns:

            True  -> Lock acquired
            False -> Thread must wait
        """

        # -----------------------------------------------------
        # CASE 1: Mutex is free
        # -----------------------------------------------------

        if not self.locked:

            # Lock the mutex.
            self.locked = True

            # Record who owns it.
            self.owner = thread.tid

            print(
                f"[Mutex] {thread.name} "
                f"(TID {thread.tid}) acquired "
                f"'{self.name}'."
            )

            return True

        # -----------------------------------------------------
        # CASE 2: Thread already owns the mutex
        # -----------------------------------------------------

        if self.owner == thread.tid:

            print(
                f"[Mutex] TID {thread.tid} already owns "
                f"'{self.name}'."
            )

            return True

        # -----------------------------------------------------
        # CASE 3: Mutex is already owned
        # -----------------------------------------------------

        print(
            f"[Mutex] TID {thread.tid} is BLOCKED. "
            f"'{self.name}' is owned by TID {self.owner}."
        )

        # Add the thread to the waiting queue.
        if thread not in self.waiting_threads:

            self.waiting_threads.append(thread)

        # Block the actual simulated thread.
        thread.block()

        return False

    # ---------------------------------------------------------
    # RELEASE
    # ---------------------------------------------------------

    def release(self, thread):
        """
        Release the mutex.

        Only the thread that owns the mutex is allowed
        to release it.
        """

        # Make sure the releasing thread actually owns it.
        if self.owner != thread.tid:

            print(
                f"[Mutex] TID {thread.tid} cannot release "
                f"'{self.name}'."
            )

            return False

        print(
            f"[Mutex] TID {thread.tid} released "
            f"'{self.name}'."
        )

        # Unlock the mutex.
        self.locked = False

        # There is currently no owner.
        self.owner = None

        # -----------------------------------------------------
        # Wake up the next waiting thread.
        # -----------------------------------------------------

        if self.waiting_threads:

            next_thread = self.waiting_threads.pop(0)

            print(
                f"[Mutex] Waking TID {next_thread.tid}."
            )

            # Move the waiting thread back to READY.
            next_thread.unblock()

        return True

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    def is_locked(self):
        """
        Return True if the mutex is currently locked.
        """

        return self.locked

    def get_owner(self):
        """
        Return the TID of the current owner.

        Returns None if the mutex is free.
        """

        return self.owner


# =============================================================
# SEMAPHORE
# =============================================================


class Semaphore:
    """
    Simulated counting semaphore.

    A semaphore maintains a counter representing the
    number of available instances of a resource.

    Example:

        Semaphore count = 2

        T1 -> wait() -> count becomes 1
        T2 -> wait() -> count becomes 0
        T3 -> wait() -> BLOCKED

        T1 -> signal() -> count becomes 1
        T3 -> can now continue
    """

    def __init__(self, name, initial_count):

        # Name of the semaphore.
        self.name = name

        # Number of currently available resource instances.
        self.count = initial_count

        # Threads waiting for the semaphore.
        self.waiting_threads = []

    # ---------------------------------------------------------
    # WAIT
    # ---------------------------------------------------------

    def wait(self, thread):
        """
        Attempt to acquire one semaphore unit.

        This corresponds to the classic semaphore:

            wait()

        operation.
        """

        # If at least one resource is available...
        if self.count > 0:

            # Consume one available unit.
            self.count -= 1

            print(
                f"[Semaphore] TID {thread.tid} acquired "
                f"'{self.name}'. "
                f"Available={self.count}"
            )

            return True

        # No resource is available.
        print(
            f"[Semaphore] TID {thread.tid} is BLOCKED "
            f"waiting for '{self.name}'."
        )

        # Add the thread to the waiting queue.
        if thread not in self.waiting_threads:

            self.waiting_threads.append(thread)

        # Block the simulated thread.
        thread.block()

        return False

    # ---------------------------------------------------------
    # SIGNAL
    # ---------------------------------------------------------

    def signal(self):
        """
        Return one semaphore unit.

        This corresponds to:

            signal()

        in classical semaphore terminology.
        """

        # Increase the available resource count.
        self.count += 1

        print(
            f"[Semaphore] '{self.name}' signalled. "
            f"Available={self.count}"
        )

        # If a thread is waiting, wake the oldest one.
        if self.waiting_threads:

            next_thread = self.waiting_threads.pop(0)

            print(
                f"[Semaphore] Waking "
                f"TID {next_thread.tid}."
            )

            next_thread.unblock()

    def get_count(self):
        """
        Return the current semaphore count.
        """

        return self.count


# =============================================================
# SHARED RESOURCE
# =============================================================


class SharedResource:
    """
    Represents data that multiple threads may access.

    This class is useful for demonstrating race conditions.

    Example:

        Shared Counter = 0

        T1 and T2 both attempt:

            counter = counter + 1

        The mutex can be used to ensure only one thread
        modifies the counter at a time.
    """

    def __init__(self, name, initial_value=0):

        # Name of the shared resource.
        self.name = name

        # Actual stored value.
        self.value = initial_value

    # ---------------------------------------------------------
    # READ
    # ---------------------------------------------------------

    def read(self):
        """
        Read the current value.
        """

        print(
            f"[Resource] {self.name} READ -> {self.value}"
        )

        return self.value

    # ---------------------------------------------------------
    # WRITE
    # ---------------------------------------------------------

    def write(self, value):
        """
        Write a new value.
        """

        print(
            f"[Resource] {self.name} "
            f"WRITE: {self.value} -> {value}"
        )

        self.value = value

    # ---------------------------------------------------------
    # INCREMENT
    # ---------------------------------------------------------

    def increment(self):
        """
        Increment the shared value by one.

        NOTE:

        This operation is intentionally simple.

        If multiple threads perform this operation without
        synchronization, a race condition can occur.

        The mutex should be responsible for protecting this
        operation.
        """

        old_value = self.value

        self.value += 1

        print(
            f"[Resource] {self.name} "
            f"incremented: {old_value} -> {self.value}"
        )