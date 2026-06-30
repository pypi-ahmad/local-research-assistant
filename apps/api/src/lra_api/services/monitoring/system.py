"""System monitoring utilities."""

from __future__ import annotations

import subprocess

import psutil
import redis

from lra_api.core.config import get_settings


class MonitoringService:
    """Runtime metrics collection service."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.redis_client = redis.from_url(self.settings.redis_url)

    def system_status(self) -> dict[str, float | int | None]:
        """Collect CPU, memory, GPU, and queue depth metrics."""
        gpu_util, gpu_mem = self._gpu_metrics()
        queue_depth = self.redis_client.llen("celery")
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.2),
            "memory_percent": psutil.virtual_memory().percent,
            "gpu_utilization": gpu_util,
            "gpu_memory_used_mb": gpu_mem,
            "queue_depth": int(queue_depth),
        }

    @staticmethod
    def _gpu_metrics() -> tuple[float | None, float | None]:
        try:
            output = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used",
                    "--format=csv,noheader,nounits",
                ],
                text=True,
            ).strip()
            util_s, mem_s = output.split(",")
            return float(util_s.strip()), float(mem_s.strip())
        except Exception:  # noqa: BLE001
            return None, None
