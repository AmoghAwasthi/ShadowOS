# shadowos/resources.py


class Resource:
    """
    Represents a system resource.

    A resource can have multiple identical instances.
    For example:
        CPU = 4 instances
        MEMORY = 8 instances
        DISK = 2 instances
    """

    def __init__(self, name, total_units):
        self.name = name
        self.total_units = total_units
        self.available_units = total_units

    def allocate(self, units=1):
        """
        Allocate resource units if enough are available.
        """

        if units <= 0:
            return False

        if units > self.available_units:
            print(
                f"[Resource] Cannot allocate {units} "
                f"units of {self.name}. "
                f"Only {self.available_units} available."
            )
            return False

        self.available_units -= units

        print(
            f"[Resource] Allocated {units} unit(s) "
            f"of {self.name}. "
            f"Available = {self.available_units}"
        )

        return True

    def release(self, units=1):
        """
        Release resource units back to the system.
        """

        if units <= 0:
            return False

        if self.available_units + units > self.total_units:
            print(
                f"[Resource] Cannot release {units} "
                f"units of {self.name}. "
                f"Exceeds total capacity."
            )
            return False

        self.available_units += units

        print(
            f"[Resource] Released {units} unit(s) "
            f"of {self.name}. "
            f"Available = {self.available_units}"
        )

        return True

    def is_available(self, units=1):
        """
        Check whether the requested number of units
        are currently available.
        """

        return self.available_units >= units

    def __str__(self):
        return (
            f"{self.name}: "
            f"{self.available_units}/"
            f"{self.total_units} available"
        )


class ResourceManager:
    """
    Manages all system resources.

    Tracks:
        - Available resources
        - Resources allocated to processes
        - Resource requests
    """

    def __init__(self):
        # Resource name -> Resource object
        self.resources = {}

        # PID -> {resource_name: units}
        self.allocations = {}
        
        # PID -> {resource_name: units_requested}
        self.waiting = {}

    def create_resource(self, name, total_units):
        """
        Create and register a new system resource.
        """

        if name in self.resources:
            print(
                f"[ResourceManager] Resource "
                f"'{name}' already exists."
            )
            return False

        if total_units <= 0:
            print(
                "[ResourceManager] Resource must "
                "have at least one unit."
            )
            return False

        self.resources[name] = Resource(
            name,
            total_units
        )

        print(
            f"[ResourceManager] Created resource "
            f"'{name}' with {total_units} unit(s)."
        )

        return True

    def get_resource(self, name):
        """
        Return a resource by name.
        """

        return self.resources.get(name)

    def register_process(self, pid):
        """
        Create an allocation table for a process.
        """

        if pid not in self.allocations:
            self.allocations[pid] = {}

            print(
                f"[ResourceManager] Registered "
                f"PID {pid}."
            )

    def request_resource(self, pid, resource_name, units=1):
        """
        A process requests resource units.

        Allocation only succeeds if enough units
        are currently available.
        """

        if pid not in self.allocations:
            self.register_process(pid)

        resource = self.get_resource(resource_name)

        if resource is None:
            print(
                f"[ResourceManager] ERROR: "
                f"Resource '{resource_name}' does not exist."
            )
            return False

        if not resource.allocate(units):

            # Record that this process is waiting
            # for the resource.
            if pid not in self.waiting:
                self.waiting[pid] = {}

            self.waiting[pid][resource_name] = units

            print(
                f"[ResourceManager] PID {pid} "
                f"is WAITING for {units} unit(s) "
                f"of {resource_name}."
            )

            return False

        # Record allocation
        if resource_name not in self.allocations[pid]:
            self.allocations[pid][resource_name] = 0

        self.allocations[pid][resource_name] += units

        print(
            f"[ResourceManager] PID {pid} acquired "
            f"{units} unit(s) of {resource_name}."
        )

        # Remove the waiting request if the
        # resource was successfully acquired.
        if pid in self.waiting:
            self.waiting[pid].pop(
                resource_name,
                None
            )

            if not self.waiting[pid]:
                del self.waiting[pid]

        return True

    def release_resource(self, pid, resource_name, units=1):
        """
        Release resource units held by a process.
        """

        if pid not in self.allocations:
            print(
                f"[ResourceManager] PID {pid} "
                f"has no allocated resources."
            )
            return False

        if resource_name not in self.allocations[pid]:
            print(
                f"[ResourceManager] PID {pid} "
                f"does not hold {resource_name}."
            )
            return False

        allocated = self.allocations[pid][resource_name]

        if units > allocated:
            print(
                f"[ResourceManager] PID {pid} "
                f"cannot release {units} unit(s). "
                f"It only holds {allocated}."
            )
            return False

        resource = self.get_resource(resource_name)

        if resource is None:
            return False

        resource.release(units)

        self.allocations[pid][resource_name] -= units

        # Remove empty allocation entries
        if self.allocations[pid][resource_name] == 0:
            del self.allocations[pid][resource_name]

        print(
            f"[ResourceManager] PID {pid} released "
            f"{units} unit(s) of {resource_name}."
        )

        return True

    def release_all_resources(self, pid):
        """
        Release every resource currently held by a process.

        This is useful when a process terminates.
        """

        if pid not in self.allocations:
            return

        # Make a copy because the dictionary
        # is modified during iteration.
        held_resources = list(
            self.allocations[pid].items()
        )

        for resource_name, units in held_resources:
            self.release_resource(
                pid,
                resource_name,
                units
            )

        print(
            f"[ResourceManager] Released all "
            f"resources held by PID {pid}."
        )

    def get_process_resources(self, pid):
        """
        Return all resources currently held by a process.
        """

        if pid not in self.allocations:
            return {}

        return self.allocations[pid].copy()
    
    def detect_deadlock(self):
        """
        Detect circular waits between processes.

        Returns:
            list: PIDs involved in a deadlock.
        """

        # --------------------------------------------------
        # Build a wait-for graph.
        #
        # Example:
        #
        # PID 1 waits for Resource B
        # PID 2 holds Resource B
        #
        # Therefore:
        #
        # PID 1 -> PID 2
        # --------------------------------------------------

        graph = {}

        # Add every known process to the graph.
        for pid in self.allocations:
            graph[pid] = set()

        # --------------------------------------------------
        # Find which processes are waiting for resources
        # held by other processes.
        # --------------------------------------------------

        for waiting_pid, requests in self.waiting.items():

            if waiting_pid not in graph:
                graph[waiting_pid] = set()

            for resource_name in requests:

                # Check every process that currently
                # holds this resource.
                for owner_pid, owned_resources in self.allocations.items():

                    if owner_pid == waiting_pid:
                        continue

                    if resource_name in owned_resources:

                        graph[waiting_pid].add(
                            owner_pid
                        )

        # --------------------------------------------------
        # Use DFS to find cycles in the wait-for graph.
        # --------------------------------------------------

        visited = set()
        recursion_stack = set()
        deadlocked = set()

        def dfs(pid, path):

            visited.add(pid)
            recursion_stack.add(pid)

            for next_pid in graph.get(pid, set()):

                # We found a cycle.
                if next_pid in recursion_stack:

                    # Find where the cycle begins.
                    if next_pid in path:
                        cycle_start = path.index(
                            next_pid
                        )

                        deadlocked.update(
                            path[cycle_start:]
                        )

                    continue

                if next_pid not in visited:

                    dfs(
                        next_pid,
                        path + [next_pid]
                    )

            recursion_stack.remove(pid)

        # Run DFS from every process.
        for pid in graph:

            if pid not in visited:
                dfs(pid, [pid])

        # Convert set to sorted list so the
        # result is predictable for testing.
        deadlocked = sorted(deadlocked)

        # --------------------------------------------------
        # Report result.
        # --------------------------------------------------

        if deadlocked:

            print(
                "[Deadlock] DEADLOCK DETECTED!"
            )

            print(
                f"[Deadlock] Affected PIDs: "
                f"{deadlocked}"
            )

        else:

            print(
                "[Deadlock] No deadlock detected."
            )

        # IMPORTANT:
        # The tests expect this method to return
        # a list, even when there is no deadlock.
        return deadlocked
    def recover_from_deadlock(self, deadlocked_pids):
        """
        Recover from a detected deadlock.

        The simplest recovery strategy used by SHADOWOS
        is to terminate one of the deadlocked processes.

        The victim process is selected using a simple rule:
        choose the process with the highest PID.

        Once terminated, all resources held by that
        process are released.
        """

        if not deadlocked_pids:
            print(
                "[Deadlock] No recovery required."
            )
            return None

        # --------------------------------------------------
        # Select a victim.
        #
        # In a real OS, victim selection could consider:
        # - Process priority
        # - Amount of resources held
        # - Execution progress
        # - Restart cost
        #
        # For SHADOWOS, we use the highest PID.
        # --------------------------------------------------

        victim_pid = max(deadlocked_pids)

        print(
            f"[Deadlock] Selecting PID {victim_pid} "
            f"as the recovery victim."
        )

        # --------------------------------------------------
        # Release every resource held by the victim.
        # --------------------------------------------------

        self.release_all_resources(victim_pid)

        # --------------------------------------------------
        # Remove any pending resource requests.
        # --------------------------------------------------

        if victim_pid in self.waiting:
            del self.waiting[victim_pid]

        # --------------------------------------------------
        # Remove the process from the allocation table.
        # --------------------------------------------------

        if victim_pid in self.allocations:
            del self.allocations[victim_pid]

        print(
            f"[Deadlock] PID {victim_pid} "
            f"has been recovered."
        )

        return victim_pid
    
        def dfs(pid, path):

            visited.add(pid)
            recursion_stack.add(pid)

            for next_pid in graph.get(pid, set()):

                # Found a cycle.
                if next_pid in recursion_stack:

                    cycle_start = path.index(
                        next_pid
                    )

                    deadlocked.update(
                        path[cycle_start:]
                    )

                    continue

                if next_pid not in visited:

                    dfs(
                        next_pid,
                        path + [next_pid]
                    )

            recursion_stack.remove(pid)

        for pid in graph:
            if pid not in visited:
                dfs(pid, [pid])

        deadlocked = sorted(deadlocked)

        if deadlocked:

            print(
                "[Deadlock] DEADLOCK DETECTED!"
            )

            print(
                f"[Deadlock] Affected PIDs: "
                f"{deadlocked}"
            )

        else:

            print(
                "[Deadlock] No deadlock detected."
            )

        return deadlocked
    
    def show_resources(self):
        """
        Display the current resource status.
        """

        print("\n========== RESOURCE STATUS ==========")

        if not self.resources:
            print("No resources registered.")
            return

        for resource in self.resources.values():
            print(resource)

        print("=====================================")

    def show_allocations(self):
        """
        Display which processes currently hold
        which resources.
        """

        print("\n========== RESOURCE ALLOCATIONS ==========")

        if not self.allocations:
            print("No process allocations.")
            return

        for pid, resources in self.allocations.items():

            print(f"PID {pid}:")

            if not resources:
                print("    No resources")

            for resource_name, units in resources.items():
                print(
                    f"    {resource_name}: "
                    f"{units} unit(s)"
                )

        print("==========================================")
        