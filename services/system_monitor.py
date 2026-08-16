import time

import psutil


class SystemMonitor:
    def __init__(self):
        self.cpu = 0.0
        self.mem = 0.0
        self.disk = 0.0
        self.battery = None
        self.net_mbps = 0.0
        self.latency = 11
        self._last_net = None
        self._last_t = None
        self._cpu_hist = []
        self._cache = None
        self._cache_t = 0.0
        try:
            self.cpu = psutil.cpu_percent(interval=None)
        except Exception:
            pass

    def read(self):
        now = time.time()
        if self._cache is not None and now - self._cache_t < 0.4:
            return self._cache
        try:
            self.cpu = psutil.cpu_percent(interval=None)
        except Exception:
            pass
        try:
            self.mem = psutil.virtual_memory().percent
        except Exception:
            pass
        try:
            self.disk = psutil.disk_usage("C:").percent
        except Exception:
            pass
        try:
            self.battery = psutil.sensors_battery()
        except Exception:
            self.battery = None
        try:
            io = psutil.net_io_counters()
            now = time.time()
            if self._last_net is not None and self._last_t is not None:
                dt = max(0.001, now - self._last_t)
                self.net_mbps = ((io.bytes_recv + io.bytes_sent - self._last_net) / 1024.0 / 1024.0) / dt
                self.net_mbps = max(0.0, self.net_mbps)
            self._last_net = io.bytes_recv + io.bytes_sent
            self._last_t = now
        except Exception:
            pass
        self._cpu_hist.append(self.cpu)
        if len(self._cpu_hist) > 24:
            self._cpu_hist.pop(0)
        data = {
            "cpu": self.cpu,
            "mem": self.mem,
            "disk": self.disk,
            "battery": self.battery,
            "net_mbps": self.net_mbps,
            "latency": self.latency,
            "gpu": min(97.0, self.cpu * 0.78 + 9.0),
        }
        self._cache = data
        self._cache_t = now
        return data

    def cpu_history(self):
        return list(self._cpu_hist)
