"""
Tests for the SHADOWOS CPU scheduler.

These tests verify:
1. Priority selection
2. CPU assignment
3. Preemption
4. Process completion
"""

from shadowos.process import ProcessManager, ProcessState
from shadowos.scheduler import Scheduler


def test_highest_priority_process_runs_first():
    """
    The process with the smallest priority number
    should get the CPU first.
    """

    manager = ProcessManager()
    scheduler = Scheduler(manager)

    # Create three processes with different priorities.
    low_priority = manager.create_process(
        name="LowPriority",
        priority=3,
        burst_time=5
    )

    high_priority = manager.create_process(
        name="HighPriority",
        priority=1,
        burst_time=5
    )

    medium_priority = manager.create_process(
        name="MediumPriority",
        priority=2,
        burst_time=5
    )

    # Add all processes to the scheduler.
    scheduler.add_process(low_priority)
    scheduler.add_process(high_priority)
    scheduler.add_process(medium_priority)

    # Ask the scheduler who should run.
    selected = scheduler.schedule()

    # Priority 1 should win.
    assert selected == high_priority

    # It should now be RUNNING.
    assert high_priority.state == ProcessState.RUNNING


def test_preemption():
    """
    Verify that a higher-priority process can
    preempt a lower-priority process.
    """

    manager = ProcessManager()
    scheduler = Scheduler(manager)

    # Start with a low-priority process.
    low_priority = manager.create_process(
        name="LowPriority",
        priority=3,
        burst_time=5
    )

    scheduler.add_process(low_priority)

    # Scheduler starts the low-priority process.
    scheduler.schedule()

    assert scheduler.current_process == low_priority

    # Create a higher-priority process.
    high_priority = manager.create_process(
        name="HighPriority",
        priority=1,
        burst_time=5
    )

    scheduler.add_process(high_priority)

    # Scheduler runs again.
    scheduler.schedule()

    # High-priority process should now be running.
    assert scheduler.current_process == high_priority

    # The old process should have returned to READY.
    assert low_priority.state == ProcessState.READY

    # A context switch should have occurred.
    assert scheduler.context_switches == 1


def test_finished_process_is_removed():
    """
    Verify that a completed process is removed
    from the scheduler.
    """

    manager = ProcessManager()
    scheduler = Scheduler(manager)

    process = manager.create_process(
        name="ShortProcess",
        priority=1,
        burst_time=1
    )

    scheduler.add_process(process)

    # Start the process.
    scheduler.schedule()

    # Use its only CPU tick.
    process.run_one_tick()

    # It should now be terminated.
    assert process.state == ProcessState.TERMINATED

    # Tell scheduler it has finished.
    scheduler.finish_process(process)

    # CPU should now be free.
    assert scheduler.current_process is None