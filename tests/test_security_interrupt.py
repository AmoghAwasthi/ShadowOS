from shadowos.kernel import Kernel
from shadowos.security import SecurityStatus


def test_security_event_triggers_isolation():

    kernel = Kernel()

    process = kernel.create_process(
        "SuspiciousProcess",
        priority=2,
        burst_time=5
    )

    kernel.report_security_event(
        process.pid,
        "UNAUTHORIZED_ACCESS",
        "Attempted access to restricted resource."
    )

    assert (
        kernel.security_manager.get_status(
            process.pid
        )
        == SecurityStatus.ISOLATED
    )


def test_security_event_is_recorded():

    kernel = Kernel()

    process = kernel.create_process(
        "SuspiciousProcess",
        priority=2,
        burst_time=5
    )

    kernel.report_security_event(
        process.pid,
        "RESOURCE_ABUSE",
        "Excessive resource usage detected."
    )

    assert len(
        kernel.security_manager.events
    ) == 1


def test_normal_process_remains_trusted():

    kernel = Kernel()

    process = kernel.create_process(
        "NormalProcess",
        priority=2,
        burst_time=5
    )

    assert (
        kernel.security_manager.get_status(
            process.pid
        )
        == SecurityStatus.TRUSTED
    )