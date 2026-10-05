"""
Interrupt handling for SHADOWOS.

A real operating system receives interrupts from hardware
and software.

SHADOWOS simulates this idea using events.

Current interrupt types:

    TIMER
    SECURITY_ALERT

The TIMER interrupt is particularly important because
it allows the scheduler to regain control of the CPU.
"""


class InterruptHandler:

    def __init__(self, process_manager, scheduler=None, kernel=None):

        # Process manager allows interrupts to interact
        # with processes.
        self.process_manager = process_manager

        # The scheduler is optional so that the interrupt
        # handler can communicate with it.
        self.scheduler = scheduler
        self.kernel = kernel

        # Count how many interrupts have occurred.
        self.interrupt_count = 0
        
    # =========================================================
    # GENERAL INTERRUPT HANDLER
    # =========================================================

    def handle_interrupt(self, event_type, data=None):
        """
        Receive and process an interrupt.

        Example:

            handle_interrupt("TIMER")
        """

        # Every interrupt increments the interrupt counter.
        self.interrupt_count += 1

        print(
            f"\n[INTERRUPT #{self.interrupt_count}] "
            f"{event_type}"
        )

        if data:
            print(f"[INTERRUPT DATA] {data}")

        # -----------------------------------------------------
        # TIMER INTERRUPT
        # -----------------------------------------------------

        if event_type == "TIMER":

            self.handle_timer_interrupt()

        # -----------------------------------------------------
        # SECURITY INTERRUPT
        # -----------------------------------------------------

        elif event_type == "SECURITY_ALERT":

            self.handle_security_alert(data)

        # -----------------------------------------------------
        # UNKNOWN INTERRUPT
        # -----------------------------------------------------

        else:

            print(
                f"[InterruptHandler] Unknown interrupt: "
                f"{event_type}"
            )

    # =========================================================
    # TIMER INTERRUPT
    # =========================================================

    def handle_timer_interrupt(self):
        """
        Handle a timer interrupt.

        The timer interrupt gives the scheduler an opportunity
        to check whether the current process has used its
        complete time quantum.
        """

        print(
            "[InterruptHandler] Timer interrupt received."
        )

        # Make sure the scheduler is connected.
        if self.scheduler is None:

            print(
                "[InterruptHandler] No scheduler connected."
            )

            return

        # Tell the scheduler that one CPU tick has occurred.
        self.scheduler.handle_timer_tick()

    # =========================================================
    # SECURITY INTERRUPT
    # =========================================================

    def handle_security_alert(self, data=None):
        """
        Handle a security alert interrupt.

        A suspicious process is isolated and its
        resources are released.
        """

        print(
            "[InterruptHandler] Security alert received."
        )

        if data is None:
            print(
                "[InterruptHandler] No security "
                "event data provided."
            )
            return

        pid = data.get("pid")

        if pid is None:
            print(
                "[InterruptHandler] Security alert "
                "does not contain a PID."
            )
            return

        print(
            f"[InterruptHandler] Security event "
            f"associated with PID {pid}."
        )

        # --------------------------------------------------
        # Ask the kernel to isolate the process.
        # --------------------------------------------------

        if self.kernel is not None:

            security = (
                self.kernel.security_manager
            )

            security.isolate_process(pid)

            print(
                f"[InterruptHandler] PID {pid} "
                f"has been isolated."
            )