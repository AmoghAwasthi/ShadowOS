"""
Process management for SHADOWOS.

This module handles:
1. Process states
2. Process creation
3. Process execution
4. Process blocking/unblocking
5. Process termination

The ProcessManager is responsible for controlling
the lifecycle of every process in SHADOWOS.
"""

from enum import Enum
from shadowos.threads import ThreadManager


class ProcessState(Enum):
    """
    Different states that a process can be in.

    NEW         -> Process has just been created.
    READY       -> Process is waiting for CPU time.
    RUNNING     -> Process is currently using the CPU.
    BLOCKED     -> Process is waiting for a resource/event.
    TERMINATED  -> Process has finished or was terminated.
    """

    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    TERMINATED = "TERMINATED"


class Process:
    """
    Represents one process inside SHADOWOS.

    A process contains information such as:
    - PID
    - Name
    - Priority
    - CPU burst time
    - Current state
    """

    def __init__(self, pid, name, priority, burst_time):

        # Every process gets a unique Process ID.
        self.pid = pid

        # Human-readable process name.
        self.name = name

        # Smaller number = higher priority.
        # Example: priority 1 is higher than priority 3.
        self.priority = priority

        # Total amount of CPU time required by this process.
        self.burst_time = burst_time

        # CPU time still required.
        self.remaining_time = burst_time

        # A newly created process starts in the NEW state.
        self.state = ProcessState.NEW

        # A process can contain multiple threads.
        # We will use this later when implementing threads.
        # Store the threads belonging to this process.
        self.threads = []
    
    # ---------------------------------------------------------
    # THREAD MANAGEMENT
    # ---------------------------------------------------------

    def add_thread(self, thread):
        """
        Attach a thread to this process.

        A process can contain multiple threads.
        """

        # Make sure the thread belongs to this process.
        if thread.process_id != self.pid:

            print(
                f"[Process] TID {thread.tid} does not "
                f"belong to PID {self.pid}."
            )

            return False

        # Prevent duplicate threads.
        if thread not in self.threads:

            self.threads.append(thread)

            print(
                f"[Process] TID {thread.tid} added "
                f"to PID {self.pid}."
            )

        return True

    def get_threads(self):
        """
        Return all threads belonging to this process.
        """

        return self.threads
    # ---------------------------------------------------------
    # PROCESS STATE METHODS
    # ---------------------------------------------------------

    def make_ready(self):
        """
        Move the process into the READY state.

        A READY process is waiting for the scheduler
        to give it CPU time.
        """

        # A process that is not finished can become READY.
        if self.state != ProcessState.TERMINATED:

            self.state = ProcessState.READY

            print(
                f"[Process] PID {self.pid} ({self.name}) "
                f"is now READY."
            )

    def run(self):
        """
        Move the process into the RUNNING state.

        The scheduler will call this when the process
        is selected for CPU execution.
        """

        # A terminated process cannot run again.
        if self.state == ProcessState.TERMINATED:
            print(
                f"[Process] PID {self.pid} cannot run "
                f"because it is TERMINATED."
            )
            return False

        # A blocked process cannot directly start running.
        if self.state == ProcessState.BLOCKED:
            print(
                f"[Process] PID {self.pid} cannot run "
                f"because it is BLOCKED."
            )
            return False

        self.state = ProcessState.RUNNING

        print(
            f"[Process] PID {self.pid} ({self.name}) "
            f"is now RUNNING."
        )

        return True

    def run_one_tick(self):
        """
        Simulate the process using the CPU for one time unit.

        One scheduler tick represents one small unit of CPU time.
        """

        # The process must be RUNNING before it can use the CPU.
        if self.state != ProcessState.RUNNING:
            return False

        # Reduce the remaining CPU burst by one.
        if self.remaining_time > 0:
            self.remaining_time -= 1

        print(
            f"[Process] PID {self.pid} used 1 CPU tick. "
            f"Remaining time: {self.remaining_time}"
        )

        # If no CPU time remains, the process has finished.
        if self.remaining_time == 0:
            self.terminate()

        return True

    def block(self):
        """
        Move the process into the BLOCKED state.

        A blocked process cannot use the CPU.

        Example:
        A process may become blocked while waiting for:
        - A file
        - A database
        - A mutex
        - A semaphore
        - An IPC message
        """

        # A terminated process cannot be blocked.
        if self.state == ProcessState.TERMINATED:
            print(
                f"[Process] PID {self.pid} cannot be blocked "
                f"because it is TERMINATED."
            )
            return False

        self.state = ProcessState.BLOCKED

        print(
            f"[Process] PID {self.pid} ({self.name}) "
            f"is now BLOCKED."
        )

        return True

    def unblock(self):
        """
        Move a BLOCKED process back to READY.

        This simulates the event/resource the process was
        waiting for becoming available.
        """

        # Only a BLOCKED process should be unblocked.
        if self.state != ProcessState.BLOCKED:
            print(
                f"[Process] PID {self.pid} is not BLOCKED."
            )
            return False

        self.state = ProcessState.READY

        print(
            f"[Process] PID {self.pid} ({self.name}) "
            f"is now READY again."
        )

        return True

    def terminate(self):
        """
        Permanently terminate the process.

        Once a process reaches TERMINATED, it cannot
        return to READY or RUNNING.
        """

        # Avoid doing the same operation twice.
        if self.state == ProcessState.TERMINATED:
            return False

        self.state = ProcessState.TERMINATED

        print(
            f"[Process] PID {self.pid} ({self.name}) "
            f"has been TERMINATED."
        )

        return True


class ProcessManager:
    """
    Responsible for creating and controlling processes.

    This class acts as the main interface for process lifecycle
    operations in SHADOWOS.
    """

    def __init__(self):

        # List containing every process created by SHADOWOS.
        self.processes = []

        # Next PID that will be assigned.
        self.next_pid = 1

    def create_process(self, name, priority, burst_time):
        """
        Create a new process.

        The lifecycle starts as:

            NEW -> READY

        after the process has been created.
        """

        # Create the Process object.
        process = Process(
            pid=self.next_pid,
            name=name,
            priority=priority,
            burst_time=burst_time
        )

        # Add the process to the process table.
        self.processes.append(process)

        # Prepare the next PID.
        self.next_pid += 1

        print(
            f"[ProcessManager] Created PID={process.pid} "
            f"({process.name})"
        )

        # A newly created process moves from NEW to READY.
        process.make_ready()

        return process

    def get_process(self, pid):
        """
        Find a process using its PID.

        Returns:
            Process object if found.
            None if no process has that PID.
        """

        for process in self.processes:

            if process.pid == pid:
                return process

        return None

    def terminate_process(self, pid):
        """
        Terminate a process using its PID.
        """

        process = self.get_process(pid)

        if process is None:
            print(
                f"[ProcessManager] PID {pid} does not exist."
            )
            return False

        return process.terminate()

    def block_process(self, pid):
        """
        Block a process using its PID.
        """

        process = self.get_process(pid)

        if process is None:
            print(
                f"[ProcessManager] PID {pid} does not exist."
            )
            return False

        return process.block()

    def unblock_process(self, pid):
        """
        Unblock a process using its PID.

        BLOCKED -> READY
        """

        process = self.get_process(pid)

        if process is None:
            print(
                f"[ProcessManager] PID {pid} does not exist."
            )
            return False

        return process.unblock()
    def add_thread_to_process(self, pid, thread):
        """
        Add a thread to a specific process.

        This keeps thread ownership under the ProcessManager.
        """

        process = self.get_process(pid)

        if process is None:

            print(
                f"[ProcessManager] PID {pid} does not exist."
            )

            return False

        return process.add_thread(thread)


    def show_process_table(self):
        """
        Display all processes and their current states.

        This is a simple version of the process table that
        will eventually be displayed in the SHADOWOS dashboard.
        """

        print("\n========== PROCESS TABLE ==========")

        for process in self.processes:

            print(
                f"PID: {process.pid:<3} | "
                f"Name: {process.name:<18} | "
                f"State: {process.state.value:<10} | "
                f"Priority: {process.priority} | "
                f"Remaining CPU: {process.remaining_time}"
            )

        print("===================================")