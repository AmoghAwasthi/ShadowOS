# shadowos/demos/phase_one_demo.py

from shadowos.kernel import Kernel


def main():
    print("\n")
    print("==============================================")
    print("       SHADOWOS PHASE ONE DEMONSTRATION")
    print("==============================================")

    # ==================================================
    # 1. INITIALIZE KERNEL
    # ==================================================

    kernel = Kernel()

    # ==================================================
    # 2. CREATE PROCESSES
    # ==================================================

    print("\n--- Creating Processes ---")

    server = kernel.create_process(
        "ServerProcess",
        priority=1,
        burst_time=6
    )

    client = kernel.create_process(
        "ClientProcess",
        priority=3,
        burst_time=4
    )

    # ==================================================
    # 3. CREATE THREADS
    # ==================================================

    print("\n--- Creating Threads ---")

    server_thread = kernel.create_thread(
        server.pid,
        "ServerWorker"
    )

    client_thread = kernel.create_thread(
        client.pid,
        "ClientWorker"
    )

    # ==================================================
    # 4. CREATE SYSTEM RESOURCES
    # ==================================================

    print("\n--- Creating System Resources ---")

    kernel.create_system_resource(
        "CPU",
        2
    )

    kernel.create_system_resource(
        "Memory",
        4
    )

    kernel.create_system_resource(
        "Disk",
        2
    )

    # ==================================================
    # 5. CREATE SYNCHRONIZATION OBJECTS
    # ==================================================

    print("\n--- Creating Synchronization Objects ---")

    database_lock = kernel.create_mutex(
        "DatabaseLock"
    )

    database = kernel.create_shared_resource(
        "DatabaseCounter",
        0
    )

    # ==================================================
    # 6. ALLOCATE RESOURCES
    # ==================================================

    print("\n--- Resource Allocation ---")

    kernel.request_resource(
        server.pid,
        "CPU",
        1
    )

    kernel.request_resource(
        server.pid,
        "Memory",
        2
    )

    kernel.request_resource(
        client.pid,
        "CPU",
        1
    )

    # ==================================================
    # 7. IPC COMMUNICATION
    # ==================================================

    print("\n--- Inter-Process Communication ---")

    kernel.send_message(
        server.pid,
        client.pid,
        "Server is ready."
    )

    kernel.send_message(
        client.pid,
        server.pid,
        "Client request received."
    )

    # ==================================================
    # 8. SYNCHRONIZATION DEMONSTRATION
    # ==================================================

    print("\n--- Synchronization ---")

    print("\nServer thread attempting database access:")

    if database_lock.acquire(server_thread):
        server_thread.run()

        database.increment()

        print(
            f"Database value = {database.read()}"
        )

    print("\nClient thread attempting database access:")

    if not database_lock.acquire(client_thread):
        print(
            f"Client thread state = "
            f"{client_thread.state.value}"
        )

    print("\nServer thread releasing database:")

    database_lock.release(server_thread)

    print(
        f"Client thread state = "
        f"{client_thread.state.value}"
    )

    # ==================================================
    # 9. IPC MESSAGE RECEIVING
    # ==================================================

    print("\n--- Receiving IPC Messages ---")

    kernel.receive_message(client.pid)
    kernel.receive_message(server.pid)

    # ==================================================
    # 10. RUN THE KERNEL
    # ==================================================

    print("\n--- Starting Kernel Execution ---")

    kernel.run(
        ticks=8
    )

    # ==================================================
    # 11. RELEASE RESOURCES
    # ==================================================

    print("\n--- Releasing Resources ---")

    kernel.release_resource(
        server.pid,
        "CPU",
        1
    )

    kernel.release_resource(
        server.pid,
        "Memory",
        2
    )

    kernel.release_resource(
        client.pid,
        "CPU",
        1
    )

    # ==================================================
    # 12. FINAL SYSTEM STATUS
    # ==================================================

    kernel.show_system_status()

    print("\n")
    print("==============================================")
    print("       PHASE ONE DEMONSTRATION COMPLETE")
    print("==============================================")


if __name__ == "__main__":
    main()