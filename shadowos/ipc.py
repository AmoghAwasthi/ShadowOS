# shadowos/ipc.py

class Message:
    """
    Represents a single message sent from one process to another.
    """

    def __init__(self, sender_pid, receiver_pid, data):
        self.sender_pid = sender_pid
        self.receiver_pid = receiver_pid
        self.data = data

    def __str__(self):
        return (
            f"Message("
            f"from PID {self.sender_pid} "
            f"to PID {self.receiver_pid}: "
            f"{self.data})"
        )


class IPCManager:
    """
    Manages communication between processes.

    Each process has a message queue.
    A process can send a message to another process,
    and the receiving process can retrieve it later.
    """

    def __init__(self):
        # Dictionary:
        # PID -> list of messages waiting for that process
        self.message_queues = {}

    def register_process(self, pid):
        """
        Creates an empty message queue for a process.
        """

        if pid not in self.message_queues:
            self.message_queues[pid] = []

            print(
                f"[IPC] Registered message queue for PID {pid}."
            )

    def send_message(self, sender_pid, receiver_pid, data):
        """
        Sends a message from one process to another.
        """

        # Make sure the receiver has a message queue
        if receiver_pid not in self.message_queues:
            print(
                f"[IPC] ERROR: PID {receiver_pid} "
                f"does not exist."
            )
            return False

        message = Message(
            sender_pid,
            receiver_pid,
            data
        )

        self.message_queues[receiver_pid].append(message)

        print(
            f"[IPC] PID {sender_pid} -> PID {receiver_pid}: "
            f"{data}"
        )

        return True

    def receive_message(self, pid):
        """
        Receives the oldest waiting message for a process.

        This follows FIFO ordering.
        """

        if pid not in self.message_queues:
            print(
                f"[IPC] ERROR: PID {pid} "
                f"does not exist."
            )
            return None

        # No messages waiting
        if not self.message_queues[pid]:
            print(
                f"[IPC] PID {pid} has no messages."
            )
            return None

        # Remove the oldest message
        message = self.message_queues[pid].pop(0)

        print(
            f"[IPC] PID {pid} received message "
            f"from PID {message.sender_pid}: "
            f"{message.data}"
        )

        return message

    def has_messages(self, pid):
        """
        Checks whether a process has waiting messages.
        """

        if pid not in self.message_queues:
            return False

        return len(self.message_queues[pid]) > 0

    def get_queue_size(self, pid):
        """
        Returns the number of waiting messages.
        """

        if pid not in self.message_queues:
            return 0

        return len(self.message_queues[pid])

    def show_message_queues(self):
        """
        Displays the current IPC message queues.
        """

        print("\n========== IPC MESSAGE QUEUES ==========")

        if not self.message_queues:
            print("No registered processes.")
            return

        for pid, queue in self.message_queues.items():

            print(f"PID {pid}: {len(queue)} message(s)")

            for message in queue:
                print(f"    {message}")

        print("========================================")