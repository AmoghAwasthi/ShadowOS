# SHADOWOS - Phase One Starter

SHADOWOS is a distributed Operating System simulator designed to demonstrate:
- Process management
- CPU scheduling
- Threads and synchronization
- Inter-process communication (IPC)
- Resource allocation and deadlock handling
- Security events
- Distributed node coordination

## Phase One goal

Do NOT try to implement everything at once.

The first milestone is a working single-node OS simulation:

Event -> Process -> Scheduler -> Thread -> Resource/IPC

After this works, distributed nodes and security/fault handling can be added.

## How to run

Requirements:
- Python 3.10+

Run:

    python main.py

No external packages are required for the starter version.

## Recommended implementation order

1. Process lifecycle
2. Priority/preemptive scheduler
3. Interrupt handling
4. Threads
5. Mutex/semaphore synchronization
6. IPC
7. Resource allocation
8. Deadlock detection/recovery
9. Security manager
10. Distributed nodes
11. Monitoring dashboard
