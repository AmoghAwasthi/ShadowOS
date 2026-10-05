# main.py

from shadowos.kernel import Kernel


def main():
    """
    Main entry point for SHADOWOS.
    """

    kernel = Kernel()

    # --------------------------------------------------
    # CREATE PROCESSES
    # --------------------------------------------------

    process1 = kernel.create_process(
        "DatabaseServer",
        priority=1,
        burst_time=5
    )

    process2 = kernel.create_process(
        "ClientProcess",
        priority=3,
        burst_time=4
    )

    # --------------------------------------------------
    # CREATE THREADS
    # --------------------------------------------------

    kernel.create_thread(
        process1.pid,
        "DatabaseWorker"
    )

    kernel.create_thread(
        process2.pid,
        "ClientWorker"
    )

    # --------------------------------------------------
    # CREATE SYSTEM RESOURCES
    # --------------------------------------------------

    kernel.create_system_resource(
        "CPU",
        2
    )

    kernel.create_system_resource(
        "Memory",
        4
    )

    # --------------------------------------------------
    # CREATE SYNCHRONIZATION OBJECTS
    # --------------------------------------------------

    kernel.create_mutex(
        "DatabaseLock"
    )

    kernel.create_shared_resource(
        "DatabaseCounter",
        0
    )

    # --------------------------------------------------
    # RESOURCE ALLOCATION
    # --------------------------------------------------

    kernel.request_resource(
        process1.pid,
        "CPU",
        1
    )

    kernel.request_resource(
        process1.pid,
        "Memory",
        2
    )

    # --------------------------------------------------
    # IPC
    # --------------------------------------------------

    kernel.send_message(
        process1.pid,
        process2.pid,
        "Database server is ready."
    )

    # --------------------------------------------------
    # RUN KERNEL
    # --------------------------------------------------

    kernel.run(
        ticks=8
    )

    # --------------------------------------------------
    # DISPLAY FINAL STATE
    # --------------------------------------------------

    kernel.show_system_status()


if __name__ == "__main__":
    main()