from __future__ import annotations

import time
import unittest

from agent_platform.worker import TeamWorker


class TeamWorkerTests(unittest.TestCase):
    def test_job_lifecycle_and_failure_visibility(self) -> None:
        worker = TeamWorker(max_workers=1)
        try:
            job = worker.submit(lambda: "done")
            for _ in range(20):
                if worker.get(job.job_id).status == "completed":
                    break
                time.sleep(0.01)
            self.assertEqual("completed", worker.get(job.job_id).status)
            self.assertEqual("done", worker.get(job.job_id).result)
            failed = worker.submit(lambda: (_ for _ in ()).throw(RuntimeError("provider")))
            for _ in range(20):
                if worker.get(failed.job_id).status == "failed":
                    break
                time.sleep(0.01)
            self.assertEqual("failed", worker.get(failed.job_id).status)
            self.assertEqual("RuntimeError", worker.get(failed.job_id).error)
        finally:
            worker.close()


if __name__ == "__main__":
    unittest.main()
