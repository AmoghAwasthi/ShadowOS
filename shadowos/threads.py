"""
Thread management for SHADOWOS.

A process can contain multiple threads.

Example:

    Process P1
    ├── Thread T1
    ├── Thread T2
    └── Thread T3

Threads share the resources of their parent process,
but each thread has its own execution state.
"""

from enum import Enum


class ThreadState(Enum):
    """
    Possible states of a thread.

    READY       -> Waiting for execution.
    RUNNING     -> Currently executing.
    BLOCKED     -> Waiting for a resource/event.
    TERMINATED  -> Thread has finished.
    """

    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    TERMINATED = "TERMINATED"


class Thread:
    """
    Represents a single thread belonging to a process.
    """

    def __init__(self, tid, process_id, name):

        # Unique Thread ID.
        self.tid = tid

        # PID of the process this thread belongs to.
        self.process_id = process_id

        # Human-readable thread name.
        self.name = name

        # Threads start in READY state.
        self.state = ThreadState.READY

        # Number of CPU ticks used by this thread.
        self.cpu_ticks = 0

    # =========================================================
    # THREAD STATE MANAGEMENT
    # =========================================================

    def run(self):
        """
        Move the thread into RUNNING state.
        """

        # A terminated thread cannot run again.
        if self.state == ThreadState.TERMINATED:

            print(
                f"[Thread] TID {self.tid} "
                f"cannot run because it is TERMINATED."
            )

            return False

        # A blocked thread must first be unblocked.
        if self.state == ThreadState.BLOCKED:

            print(
                f"[Thread] TID {self.tid} "
                f"cannot run because it is BLOCKED."
            )

            return False

        self.state = ThreadState.RUNNING

        print(
            f"[Thread] TID {self.tid} ({self.name}) "
            f"is now RUNNING."
        )

        return True

    def run_one_tick(self):
        """
        Simulate one CPU tick for this thread.
        """

        # The thread must be running before using the CPU.
        if self.state != ThreadState.RUNNING:

            return False

        self.cpu_ticks += 1

        print(
            f"[Thread] TID {self.tid} used CPU tick "
            f"{self.cpu_ticks}."
        )

        return True

    def block(self):
        """
        Move the thread into BLOCKED state.
        """

        if self.state == ThreadState.TERMINATED:

            return False

        self.state = ThreadState.BLOCKED

        print(
            f"[Thread] TID {self.tid} "
            f"is now BLOCKED."
        )

        return True

    def unblock(self):
        """
        Move a blocked thread back to READY.
        """

        if self.state != ThreadState.BLOCKED:

            return False

        self.state = ThreadState.READY

        print(
            f"[Thread] TID {self.tid} "
            f"is now READY."
        )

        return True

    def terminate(self):
        """
        Permanently terminate the thread.
        """

        if self.state == ThreadState.TERMINATED:

            return False

        self.state = ThreadState.TERMINATED

        print(
            f"[Thread] TID {self.tid} "
            f"has been TERMINATED."
        )

        return True


class ThreadManager:
    """
    Creates and manages threads.

    The ThreadManager is similar to ProcessManager,
    but operates at the thread level.
    """

    def __init__(self):

        # Store every thread created by SHADOWOS.
        self.threads = []

        # Next TID.
        self.next_tid = 1

    # =========================================================
    # THREAD CREATION
    # =========================================================

    def create_thread(self, process_id, name):
        """
        Create a new thread for a process.

        The new thread starts in READY state.
        """

        thread = Thread(
            tid=self.next_tid,
            process_id=process_id,
            name=name
        )

        self.threads.append(thread)

        self.next_tid += 1

        print(
            f"[ThreadManager] Created TID={thread.tid} "
            f"({thread.name}) for PID={process_id}"
        )

        return thread

    # =========================================================
    # THREAD LOOKUP
    # =========================================================

    def get_thread(self, tid):
        """
        Find a thread using its TID.
        """

        for thread in self.threads:

            if thread.tid == tid:

                return thread

        return None

    # =========================================================
    # PROCESS THREADS
    # =========================================================

    def get_process_threads(self, process_id):
        """
        Return all threads belonging to a process.
        """

        return [
            thread
            for thread in self.threads
            if thread.process_id == process_id
        ]

    # =========================================================
    # THREAD CONTROL
    # =========================================================

    def block_thread(self, tid):
        """
        Block a thread using its TID.
        """

        thread = self.get_thread(tid)

        if thread is None:

            print(
                f"[ThreadManager] TID {tid} does not exist."
            )

            return False

        return thread.block()

    def unblock_thread(self, tid):
        """
        Unblock a thread using its TID.
        """

        thread = self.get_thread(tid)

        if thread is None:

            print(
                f"[ThreadManager] TID {tid} does not exist."
            )

            return False

        return thread.unblock()

    def terminate_thread(self, tid):
        """
        Terminate a thread using its TID.
        """

        thread = self.get_thread(tid)

        if thread is None:

            print(
                f"[ThreadManager] TID {tid} does not exist."
            )

            return False

        return thread.terminate()

    # =========================================================
    # DISPLAY
    # =========================================================

    def show_thread_table(self):
        """
        Display every thread in the system.
        """

        print("\n========== THREAD TABLE ==========")

        if not self.threads:

            print("No threads exist.")

        else:

            for thread in self.threads:

                print(
                    f"TID: {thread.tid:<3} | "
                    f"PID: {thread.process_id:<3} | "
                    f"Name: {thread.name:<18} | "
                    f"State: {thread.state.value:<10} | "
                    f"CPU Ticks: {thread.cpu_ticks}"
                )

        print("==================================")
        