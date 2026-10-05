"""
CPU Scheduler for SHADOWOS.

Current scheduling algorithm:
    Preemptive Priority Scheduling with Time Quantum

The scheduler is responsible for deciding which READY
process gets access to the simulated CPU.

Priority rule:
    Smaller priority number = higher priority.

Example:

    Priority 1 -> highest priority
    Priority 2
    Priority 3 -> lowest priority


Time Quantum:
    The maximum number of CPU ticks a process can use
    before the scheduler gets another chance to switch it.
"""


from shadowos.process import ProcessState


class Scheduler:
    """
    Controls CPU allocation between processes.

    The scheduler handles:

    - READY queue
    - CPU assignment
    - Priority scheduling
    - Preemption
    - Time quantum
    - Context switches
    """

    def __init__(self, process_manager, time_quantum=2):

        # We need access to the ProcessManager so the scheduler
        # can work with all processes in the system.
        self.process_manager = process_manager

        # Processes waiting for CPU time.
        self.ready_queue = []

        # Process currently using the CPU.
        self.current_process = None

        # Number of CPU ticks allowed before a time-slice
        # expiration can cause a context switch.
        self.time_quantum = time_quantum

        # Number of ticks the current process has used
        # during its current time slice.
        self.quantum_used = 0

        # Number of context switches performed by the scheduler.
        self.context_switches = 0

    # =========================================================
    # READY QUEUE MANAGEMENT
    # =========================================================

    def add_process(self, process):
        """
        Add a process to the READY queue.

        Only READY processes are allowed into the queue.
        """

        if process.state != ProcessState.READY:
            return

        # Prevent duplicate entries.
        if process not in self.ready_queue:

            self.ready_queue.append(process)

            print(
                f"[Scheduler] PID {process.pid} "
                f"added to READY queue."
            )

    def remove_process(self, process):
        """
        Remove a process from the READY queue.
        """

        if process in self.ready_queue:

            self.ready_queue.remove(process)

            print(
                f"[Scheduler] PID {process.pid} "
                f"removed from READY queue."
            )

    # =========================================================
    # FIND BEST PROCESS
    # =========================================================

    def get_highest_priority_process(self):
        """
        Find the highest-priority READY process.

        Smaller priority number = higher priority.
        """

        # Remove processes that are no longer READY.
        self.ready_queue = [
            process
            for process in self.ready_queue
            if process.state == ProcessState.READY
        ]

        # No READY processes means the CPU has nothing to run.
        if not self.ready_queue:
            return None

        # Select the process with the smallest priority value.
        return min(
            self.ready_queue,
            key=lambda process: process.priority
        )

    # =========================================================
    # MAIN SCHEDULING FUNCTION
    # =========================================================

    def schedule(self):
        """
        Decide which process should use the CPU.

        This function is called whenever the scheduler
        needs to make a decision.

        Possible situations:

        1. CPU is idle
        2. Current process finished
        3. Current process is blocked
        4. Higher-priority process arrived
        5. Time quantum expired
        6. Current process continues
        """

        # Find the best process currently waiting.
        highest_priority = self.get_highest_priority_process()

        # -----------------------------------------------------
        # CASE 1: No READY processes
        # -----------------------------------------------------

        if highest_priority is None:

            # If the current process is not running anymore,
            # release the CPU.
            if (
                self.current_process is None
                or self.current_process.state != ProcessState.RUNNING
            ):
                self.current_process = None

            return self.current_process

        # -----------------------------------------------------
        # CASE 2: CPU is currently idle
        # -----------------------------------------------------

        if self.current_process is None:

            self.start_process(highest_priority)

            return self.current_process

        # -----------------------------------------------------
        # CASE 3: Current process has terminated
        # -----------------------------------------------------

        if self.current_process.state == ProcessState.TERMINATED:

            finished = self.current_process

            self.finish_process(finished)

            self.start_process(highest_priority)

            return self.current_process

        # -----------------------------------------------------
        # CASE 4: Current process became BLOCKED
        # -----------------------------------------------------

        if self.current_process.state == ProcessState.BLOCKED:

            print(
                f"[Scheduler] PID {self.current_process.pid} "
                f"is BLOCKED."
            )

            self.current_process = None

            self.start_process(highest_priority)

            return self.current_process

        # -----------------------------------------------------
        # CASE 5: Higher-priority process is waiting
        # -----------------------------------------------------

        if (
            highest_priority.priority
            < self.current_process.priority
        ):

            print(
                f"[Scheduler] Higher priority process detected: "
                f"PID {highest_priority.pid}"
            )

            # Preempt the current process.
            self.preempt_current_process()

            # Give CPU to the higher-priority process.
            self.start_process(highest_priority)

            return self.current_process

        # -----------------------------------------------------
        # CASE 6: Continue current process
        # -----------------------------------------------------

        return self.current_process

    # =========================================================
    # START PROCESS
    # =========================================================

    def start_process(self, process):
        """
        Give the CPU to a process.
        """

        # Remove it from READY queue because it is now running.
        self.remove_process(process)

        # Change state to RUNNING.
        process.run()

        # Store it as the current CPU process.
        self.current_process = process

        # Reset its time quantum.
        self.quantum_used = 0

        print(
            f"[Scheduler] CPU assigned to "
            f"PID {process.pid} ({process.name})."
        )

    # =========================================================
    # TIMER / TIME QUANTUM
    # =========================================================

    def handle_timer_tick(self):
        """
        Handle one timer tick.

        The timer interrupt calls this function.

        Every CPU tick:

            quantum_used += 1

        If the process reaches the time quantum:

            RUNNING
                ↓
             PREEMPT
                ↓
             READY

        Then another process can be scheduled.
        """

        # If nothing is running, there is nothing to count.
        if self.current_process is None:
            return

        # Only count time for a RUNNING process.
        if self.current_process.state != ProcessState.RUNNING:
            return

        # Increase the number of ticks used by this process.
        self.quantum_used += 1

        print(
            f"[Scheduler] PID {self.current_process.pid} "
            f"used quantum tick "
            f"{self.quantum_used}/{self.time_quantum}"
        )

        # Has the process used its entire time slice?
        if self.quantum_used >= self.time_quantum:

            print(
                f"[Scheduler] Time quantum expired for "
                f"PID {self.current_process.pid}."
            )

            # Preempt the process.
            self.preempt_current_process()

    # =========================================================
    # PREEMPTION
    # =========================================================

    def preempt_current_process(self):
        """
        Take the CPU away from the current process.

        The process is NOT terminated.

        Instead:

            RUNNING
                ↓
              READY

        It can be scheduled again later.
        """

        if self.current_process is None:
            return

        process = self.current_process

        print(
            f"[Scheduler] Preempting "
            f"PID {process.pid} ({process.name})."
        )

        # Move the process back to READY.
        process.make_ready()

        # Put it back into the READY queue.
        self.add_process(process)

        # CPU is temporarily free.
        self.current_process = None

        # Reset time quantum counter.
        self.quantum_used = 0

        # Record the context switch.
        self.context_switches += 1

        print(
            f"[Scheduler] Context switch "
            f"#{self.context_switches}"
        )

    # =========================================================
    # PROCESS COMPLETION
    # =========================================================

    def finish_process(self, process):
        """
        Handle a process that has finished execution.
        """

        # Mark the process as terminated.
        process.terminate()

        # Make sure it is not in the READY queue.
        self.remove_process(process)

        # If this process was using the CPU, release the CPU.
        if self.current_process == process:

            self.current_process = None

        # Reset quantum counter.
        self.quantum_used = 0

        print(
            f"[Scheduler] PID {process.pid} "
            f"has left the scheduler."
        )

    # =========================================================
    # DEBUGGING / MONITORING
    # =========================================================

    def show_ready_queue(self):
        """
        Display the current READY queue.

        This will eventually be used by the monitoring dashboard.
        """

        print("\n========== READY QUEUE ==========")

        if not self.ready_queue:

            print("READY queue is empty.")

        else:

            for process in self.ready_queue:

                print(
                    f"PID={process.pid} | "
                    f"Name={process.name} | "
                    f"Priority={process.priority} | "
                    f"State={process.state.value}"
                )

        print("=================================")

    def show_scheduler_status(self):
        """
        Display current scheduler information.
        """

        print("\n========== SCHEDULER STATUS ==========")

        if self.current_process is None:

            print("CPU: IDLE")

        else:

            print(
                f"CPU Process: PID {self.current_process.pid} "
                f"({self.current_process.name})"
            )

            print(
                f"Priority: {self.current_process.priority}"
            )

            print(
                f"Quantum: "
                f"{self.quantum_used}/{self.time_quantum}"
            )

        print(
            f"Context Switches: {self.context_switches}"
        )

        print("======================================")