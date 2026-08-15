from abc import ABC, abstractmethod
import time


class Worker(ABC):
    @abstractmethod
    def run_iteration(self) -> int:
        ...

    def run(
        self,
        iterations: int | None = None,
        wait_time: float = 5,
    ) -> None:
        if iterations is not None and iterations < 1:
            raise ValueError("iterations must be at least 1")
        if wait_time < 0:
            raise ValueError("wait_time cannot be negative")

        if iterations is not None:
            for _ in range(iterations):
                self.run_iteration()
            return

        while True:
            self.run_iteration()
            time.sleep(wait_time)
