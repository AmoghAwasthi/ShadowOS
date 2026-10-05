from shadowos.security import (
    SecurityManager,
    SecurityStatus,
)


def test_process_registration():

    security = SecurityManager()

    security.register_process(1)

    assert (
        security.get_status(1)
        == SecurityStatus.TRUSTED
    )


def test_security_event_marks_process_suspicious():

    security = SecurityManager()

    security.register_process(1)

    event = security.report_event(
        1,
        "UNAUTHORIZED_ACCESS",
        "Process attempted restricted operation."
    )

    assert event.pid == 1
    assert event.event_type == "UNAUTHORIZED_ACCESS"

    assert (
        security.get_status(1)
        == SecurityStatus.SUSPICIOUS
    )


def test_suspicious_process_not_allowed():

    security = SecurityManager()

    security.register_process(1)

    security.report_event(
        1,
        "MALICIOUS_ACTIVITY",
        "Suspicious system activity detected."
    )

    assert security.is_process_allowed(1) is False


def test_trusted_process_allowed():

    security = SecurityManager()

    security.register_process(1)

    assert security.is_process_allowed(1) is True


def test_process_isolation():

    security = SecurityManager()

    security.register_process(1)

    security.report_event(
        1,
        "RESOURCE_ABUSE",
        "Process consumed excessive resources."
    )

    result = security.isolate_process(1)

    assert result is True

    assert (
        security.get_status(1)
        == SecurityStatus.ISOLATED
    )

    assert 1 in security.isolated_processes


def test_process_termination():

    security = SecurityManager()

    security.register_process(1)

    security.isolate_process(1)

    result = security.terminate_process(1)

    assert result is True

    assert (
        security.get_status(1)
        == SecurityStatus.TERMINATED
    )

    assert 1 not in security.isolated_processes