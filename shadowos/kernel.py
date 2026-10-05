# shadowos/kernel.py

from shadowos.process import ProcessManager, ProcessState
from shadowos.scheduler import Scheduler
from shadowos.interrupts import InterruptHandler
from shadowos.threads import ThreadManager
from shadowos.synchronization import Mutex, Semaphore, SharedResource
from shadowos.ipc import IPCManager
from shadowos.resources import ResourceManager
from shadowos.security import SecurityManager


class Kernel:
    """
    Main kernel of SHADOWOS.

    The kernel connects all major OS subsystems:
        - Process management
        - CPU scheduling
        - Timer interrupts
        - Thread management
        - Synchronization
        - IPC
        - Resource management
    """

    def __init__(self):
        print("[Kernel] Initializing SHADOWOS...")

        # --------------------------------------------------
        # PROCESS MANAGEMENT
        # --------------------------------------------------

        self.process_manager = ProcessManager()

        # --------------------------------------------------
        # CPU SCHEDULER
        # --------------------------------------------------

        self.scheduler = Scheduler(
            self.process_manager,
            time_quantum=2
        )

        # --------------------------------------------------
        # INTERRUPT HANDLER
        # --------------------------------------------------

        self.interrupt_handler = InterruptHandler(
            self.process_manager,
            self.scheduler,
            self
        )

        # --------------------------------------------------
        # THREAD MANAGEMENT
        # --------------------------------------------------

        self.thread_manager = ThreadManager()

        # --------------------------------------------------
        # IPC
        # --------------------------------------------------

        self.ipc_manager = IPCManager()

        # --------------------------------------------------
        # RESOURCE MANAGEMENT
        # --------------------------------------------------

        self.resource_manager = ResourceManager()

        # --------------------------------------------------
        # SECURITY MANAGEMENT
        # --------------------------------------------------

        self.security_manager = SecurityManager()

        # --------------------------------------------------
        # SYNCHRONIZATION
        # --------------------------------------------------

        self.mutexes = {}
        self.semaphores = {}
        self.shared_resources = {}

        # --------------------------------------------------
        # KERNEL STATE
        # --------------------------------------------------

        self.current_tick = 0
        self.running = False

        print("[Kernel] SHADOWOS initialized successfully.")

    # ======================================================
    # PROCESS MANAGEMENT
    # ======================================================

    def create_process(
        self,
        name,
        priority=5,
        burst_time=5
    ):
        """
        Create a process and register it with all
        required kernel subsystems.
        """

        process = self.process_manager.create_process(
            name,
            priority,
            burst_time
        )

        # Add process to scheduler
        self.scheduler.add_process(process)

        # Create IPC message queue
        self.ipc_manager.register_process(
            process.pid
        )

        # Register process for resource tracking
        self.resource_manager.register_process(
            process.pid
        )

        # Register process with the security subsystem
        self.security_manager.register_process(
            process.pid
        )

        print(
            f"[Kernel] Process PID {process.pid} "
            f"registered with kernel subsystems."
        )

        return process

    # ======================================================
    # THREAD MANAGEMENT
    # ======================================================

    def create_thread(self, pid, name):
        """
        Create a thread and attach it to a process.
        """

        thread = self.thread_manager.create_thread(
            pid,
            name
        )

        if thread is None:
            return None

        success = self.process_manager.add_thread_to_process(
            pid,
            thread
        )

        if not success:
            # If attachment fails, terminate the thread
            self.thread_manager.terminate_thread(
                thread.tid
            )
            return None

        return thread

    # ======================================================
    # SYNCHRONIZATION
    # ======================================================

    def create_mutex(self, name):
        """
        Create a mutex managed by the kernel.
        """

        if name in self.mutexes:
            print(
                f"[Kernel] Mutex '{name}' already exists."
            )
            return self.mutexes[name]

        mutex = Mutex(name)

        self.mutexes[name] = mutex

        print(
            f"[Kernel] Created mutex '{name}'."
        )

        return mutex

    def create_semaphore(self, name, count):
        """
        Create a semaphore managed by the kernel.
        """

        if name in self.semaphores:
            print(
                f"[Kernel] Semaphore '{name}' "
                f"already exists."
            )
            return self.semaphores[name]

        semaphore = Semaphore(
            name,
            count
        )

        self.semaphores[name] = semaphore

        print(
            f"[Kernel] Created semaphore "
            f"'{name}' with count {count}."
        )

        return semaphore

    def create_shared_resource(self, name, value=0):
        """
        Create a shared resource managed by the kernel.
        """

        if name in self.shared_resources:
            print(
                f"[Kernel] Shared resource "
                f"'{name}' already exists."
            )
            return self.shared_resources[name]

        resource = SharedResource(
            name,
            value
        )

        self.shared_resources[name] = resource

        print(
            f"[Kernel] Created shared resource "
            f"'{name}'."
        )

        return resource

    # ======================================================
    # RESOURCE MANAGEMENT
    # ======================================================

    def report_security_event(
        self,
        pid,
        event_type,
        description
    ):
        """
        Report a security event involving a process.

        A security event causes the security subsystem
        to mark the process as suspicious and generates
        a security interrupt.
        """

        event = self.security_manager.report_event(
            pid,
            event_type,
            description
        )

        # Trigger a security interrupt.
        self.interrupt_handler.handle_interrupt(
            "SECURITY_ALERT",
            {
                "pid": pid,
                "event_type": event_type,
                "description": description
            }
        )

        return event
    def check_and_recover_deadlock(self):
        """
        Check for deadlocks and recover automatically
        if one is detected.
        """

        deadlocked = self.resource_manager.detect_deadlock()

        if not deadlocked:
            return None

        victim_pid = (
            self.resource_manager.recover_from_deadlock(
                deadlocked
            )
        )

        if victim_pid is not None:

            # Terminate the process in the
            # Process Manager as well.
            self.process_manager.terminate_process(
                victim_pid
            )

            print(
                f"[Kernel] PID {victim_pid} "
                f"terminated during deadlock recovery."
            )

        return victim_pid
    def create_system_resource(
        self,
        name,
        total_units
    ):
        """
        Create a system resource such as CPU,
        memory, disk, or I/O device.
        """

        return self.resource_manager.create_resource(
            name,
            total_units
        )

    def request_resource(
        self,
        pid,
        resource_name,
        units=1
    ):
        """
        Request system resources for a process.
        """

        return self.resource_manager.request_resource(
            pid,
            resource_name,
            units
        )

    def release_resource(
        self,
        pid,
        resource_name,
        units=1
    ):
        """
        Release resources held by a process.
        """

        return self.resource_manager.release_resource(
            pid,
            resource_name,
            units
        )

    # ======================================================
    # IPC
    # ======================================================

    def send_message(
        self,
        sender_pid,
        receiver_pid,
        data
    ):
        """
        Send an IPC message between processes.
        """

        return self.ipc_manager.send_message(
            sender_pid,
            receiver_pid,
            data
        )

    def receive_message(self, pid):
        """
        Receive the oldest IPC message
        waiting for a process.
        """

        return self.ipc_manager.receive_message(
            pid
        )

    # ======================================================
    # KERNEL EXECUTION
    # ======================================================

    def run(self, ticks=10):
        """
        Run the SHADOWOS simulation for a fixed
        number of CPU ticks.
        """

        self.running = True

        print("\n========================================")
        print(" SHADOWOS KERNEL STARTED")
        print("========================================")

        for _ in range(ticks):

            self.current_tick += 1

            print(
                f"\n========== KERNEL TICK "
                f"{self.current_tick} =========="
            )

            # --------------------------------------------------
            # TIMER INTERRUPT
            # --------------------------------------------------

            self.interrupt_handler.handle_interrupt(
                "TIMER"
            )

            # --------------------------------------------------
            # SCHEDULER
            # --------------------------------------------------

            process = self.scheduler.schedule()

            if process is None:

                print("[Kernel] CPU is IDLE.")

                continue

            # --------------------------------------------------
            # PROCESS EXECUTION
            # --------------------------------------------------

            if process.state == ProcessState.RUNNING:

                print(
                    f"[Kernel] CPU executing "
                    f"PID {process.pid} "
                    f"({process.name})"
                )

                process.run_one_tick()

            # --------------------------------------------------
            # PROCESS TERMINATION
            # --------------------------------------------------

            if process.state == ProcessState.TERMINATED:

                print(
                    f"[Kernel] PID {process.pid} "
                    f"has finished execution."
                )

                self.scheduler.finish_process(
                    process
                )

                # Release resources held by
                # the terminated process
                self.resource_manager.release_all_resources(
                    process.pid
                )

        self.running = False

        print("\n========================================")
        print(" SHADOWOS KERNEL STOPPED")
        print("========================================")

    # ======================================================
    # SYSTEM STATUS
    # ======================================================

    def show_system_status(self):
        """
        Display the current state of the entire system.
        """

        print("\n")
        print("========================================")
        print("       SHADOWOS SYSTEM STATUS")
        print("========================================")

        print(
            f"Current Kernel Tick: "
            f"{self.current_tick}"
        )

        print("\n--- Processes ---")
        self.process_manager.show_process_table()

        print("\n--- Scheduler ---")
        self.scheduler.show_scheduler_status()

        print("\n--- Threads ---")
        self.thread_manager.show_thread_table()

        print("\n--- Resources ---")
        self.resource_manager.show_resources()

        print("\n--- Resource Allocations ---")
        self.resource_manager.show_allocations()

        print("\n--- IPC Queues ---")
        self.ipc_manager.show_message_queues()

        print("\n========================================")