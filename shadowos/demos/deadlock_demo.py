# shadowos/demos/deadlock_demo.py

from shadowos.kernel import Kernel


def main():

    print("\n")
    print("==============================================")
    print("          SHADOWOS DEADLOCK DEMO")
    print("==============================================")

    # --------------------------------------------------
    # 1. INITIALIZE KERNEL
    # --------------------------------------------------

    kernel = Kernel()

    # --------------------------------------------------
    # 2. CREATE TWO PROCESSES
    # --------------------------------------------------

    print("\n--- Creating Processes ---")

    process1 = kernel.create_process(
        "ProcessA",
        priority=1,
        burst_time=5
    )

    process2 = kernel.create_process(
        "ProcessB",
        priority=2,
        burst_time=5
    )

    # --------------------------------------------------
    # 3. CREATE TWO RESOURCES
    # --------------------------------------------------

    print("\n--- Creating Resources ---")

    kernel.create_system_resource(
        "ResourceA",
        1
    )

    kernel.create_system_resource(
        "ResourceB",
        1
    )

    # --------------------------------------------------
    # 4. PROCESS 1 ACQUIRES RESOURCE A
    # --------------------------------------------------

    print("\n--- Process 1 acquires Resource A ---")

    kernel.request_resource(
        process1.pid,
        "ResourceA",
        1
    )

    # --------------------------------------------------
    # 5. PROCESS 2 ACQUIRES RESOURCE B
    # --------------------------------------------------

    print("\n--- Process 2 acquires Resource B ---")

    kernel.request_resource(
        process2.pid,
        "ResourceB",
        1
    )

    # --------------------------------------------------
    # 6. PROCESS 1 REQUESTS RESOURCE B
    # --------------------------------------------------

    print("\n--- Process 1 requests Resource B ---")

    kernel.request_resource(
        process1.pid,
        "ResourceB",
        1
    )

    # --------------------------------------------------
    # 7. PROCESS 2 REQUESTS RESOURCE A
    # --------------------------------------------------

    print("\n--- Process 2 requests Resource A ---")

    kernel.request_resource(
        process2.pid,
        "ResourceA",
        1
    )

    # --------------------------------------------------
    # DEADLOCK HAS NOW BEEN CREATED
    #
    # PID 1:
    #   Holds Resource A
    #   Waits for Resource B
    #
    # PID 2:
    #   Holds Resource B
    #   Waits for Resource A
    #
    # Therefore:
    #
    # PID 1 -> PID 2
    # PID 2 -> PID 1
    # --------------------------------------------------

    print("\n")
    print("==============================================")
    print("           DEADLOCK CREATED")
    print("==============================================")

    print(
        "PID 1 holds ResourceA and waits for ResourceB."
    )

    print(
        "PID 2 holds ResourceB and waits for ResourceA."
    )

    # --------------------------------------------------
    # 8. DETECT DEADLOCK
    # --------------------------------------------------

    print("\n--- Running Deadlock Detection ---")

    deadlocked = (
        kernel.resource_manager.detect_deadlock()
    )

    # --------------------------------------------------
    # 9. RECOVER FROM DEADLOCK
    # --------------------------------------------------

    if deadlocked:

        print("\n--- Starting Deadlock Recovery ---")

        victim = (
            kernel.resource_manager
            .recover_from_deadlock(
                deadlocked
            )
        )

        # Terminate the victim in ProcessManager too.
        kernel.process_manager.terminate_process(
            victim
        )

        print(
            f"\nPID {victim} was selected as "
            f"the recovery victim."
        )

    # --------------------------------------------------
    # 10. SHOW FINAL RESOURCE STATE
    # --------------------------------------------------

    print("\n--- Final Resource State ---")

    kernel.resource_manager.show_resources()

    kernel.resource_manager.show_allocations()

    # --------------------------------------------------
    # 11. CHECK DEADLOCK AGAIN
    # --------------------------------------------------

    print("\n--- Running Deadlock Detection Again ---")

    kernel.resource_manager.detect_deadlock()

    print("\n")
    print("==============================================")
    print("        DEADLOCK DEMONSTRATION COMPLETE")
    print("==============================================")


if __name__ == "__main__":
    main()