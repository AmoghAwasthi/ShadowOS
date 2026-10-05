# shadowos/security.py


from enum import Enum


class SecurityStatus(Enum):
    """
    Represents the security status of a process.
    """

    TRUSTED = "TRUSTED"
    SUSPICIOUS = "SUSPICIOUS"
    ISOLATED = "ISOLATED"
    TERMINATED = "TERMINATED"


class SecurityEvent:
    """
    Represents a security-related event detected
    by the security manager.
    """

    def __init__(self, pid, event_type, description):
        self.pid = pid
        self.event_type = event_type
        self.description = description

    def __str__(self):
        return (
            f"SecurityEvent("
            f"PID={self.pid}, "
            f"Type={self.event_type}, "
            f"Description={self.description})"
        )


class SecurityManager:
    """
    Manages process security and simulated
    security events.
    """

    def __init__(self):
        # PID -> SecurityStatus
        self.process_status = {}

        # List of security events detected
        self.events = []

        # Set of isolated processes
        self.isolated_processes = set()

    # ==================================================
    # PROCESS REGISTRATION
    # ==================================================

    def register_process(self, pid):
        """
        Register a process as trusted.
        """

        if pid not in self.process_status:

            self.process_status[pid] = (
                SecurityStatus.TRUSTED
            )

            print(
                f"[Security] PID {pid} "
                f"registered as TRUSTED."
            )

    # ==================================================
    # SECURITY EVENT DETECTION
    # ==================================================

    def report_event(
        self,
        pid,
        event_type,
        description
    ):
        """
        Report a security event involving a process.
        """

        # Make sure the process is registered.
        if pid not in self.process_status:
            self.register_process(pid)

        event = SecurityEvent(
            pid,
            event_type,
            description
        )

        self.events.append(event)

        # Mark the process as suspicious.
        self.process_status[pid] = (
            SecurityStatus.SUSPICIOUS
        )

        print(
            f"[Security] ALERT: PID {pid} "
            f"marked as SUSPICIOUS."
        )

        print(
            f"[Security] Event: {event_type} - "
            f"{description}"
        )

        return event

    # ==================================================
    # PROCESS ISOLATION
    # ==================================================

    def isolate_process(self, pid):
        """
        Isolate a suspicious process.

        An isolated process is prevented from
        participating normally in the system.
        """

        if pid not in self.process_status:
            print(
                f"[Security] PID {pid} "
                f"is not registered."
            )
            return False

        self.process_status[pid] = (
            SecurityStatus.ISOLATED
        )

        self.isolated_processes.add(pid)

        print(
            f"[Security] PID {pid} "
            f"has been ISOLATED."
        )

        return True

    # ==================================================
    # PROCESS TERMINATION
    # ==================================================

    def terminate_process(self, pid):
        """
        Mark a process as terminated by the
        security subsystem.
        """

        if pid not in self.process_status:
            print(
                f"[Security] PID {pid} "
                f"is not registered."
            )
            return False

        self.process_status[pid] = (
            SecurityStatus.TERMINATED
        )

        # Remove from isolation set if present.
        self.isolated_processes.discard(pid)

        print(
            f"[Security] PID {pid} "
            f"has been TERMINATED."
        )

        return True

    # ==================================================
    # SECURITY CHECK
    # ==================================================

    def is_process_allowed(self, pid):
        """
        Check whether a process is allowed to
        continue normal execution.
        """

        if pid not in self.process_status:
            return False

        status = self.process_status[pid]

        return status == SecurityStatus.TRUSTED

    # ==================================================
    # STATUS
    # ==================================================

    def get_status(self, pid):
        """
        Return the security status of a process.
        """

        return self.process_status.get(pid)

    # ==================================================
    # EVENT LOG
    # ==================================================

    def show_events(self):
        """
        Display all recorded security events.
        """

        print("\n========== SECURITY EVENTS ==========")

        if not self.events:
            print("No security events recorded.")
            return

        for event in self.events:
            print(event)

        print("======================================")

    def show_security_status(self):
        """
        Display the security status of every
        registered process.
        """

        print("\n========== SECURITY STATUS ==========")

        if not self.process_status:
            print("No processes registered.")
            return

        for pid, status in self.process_status.items():

            print(
                f"PID {pid}: {status.value}"
            )

        print("=====================================")