"""Performance monitoring module integrated with Prometheus for Tío Pepe."""

from typing import Dict, Any, Optional
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import psutil
import logging
from threading import Thread
import time

class PerformanceMonitor:
    """Manages system performance monitoring with Prometheus integration."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.metrics_port = self.config.get('metrics_port', 9090)
        self.collection_interval = self.config.get('collection_interval', 15)
        self.enabled = self.config.get('enabled', True)
        self.monitor_thread: Optional[Thread] = None

        # Initialize Prometheus metrics
        self.cpu_usage = Gauge('system_cpu_usage_percent',
                             'Current CPU usage percentage')
        self.memory_usage = Gauge('system_memory_usage_bytes',
                                'Current memory usage in bytes')
        self.disk_usage = Gauge('system_disk_usage_percent',
                              'Current disk usage percentage')
        
        self.request_counter = Counter('http_requests_total',
                                     'Total HTTP requests',
                                     ['method', 'endpoint', 'status'])
        
        self.response_time = Histogram('http_response_time_seconds',
                                     'HTTP response time in seconds',
                                     ['method', 'endpoint'])

        # Custom application metrics
        self.active_tasks = Gauge('app_active_tasks',
                                'Number of currently active tasks')
        self.error_counter = Counter('app_errors_total',
                                   'Total application errors',
                                   ['type', 'component'])

    def start(self) -> bool:
        """Start the performance monitoring server and collection."""
        if not self.enabled:
            self.logger.info("Performance monitoring is disabled")
            return False

        try:
            # Start Prometheus metrics server
            start_http_server(self.metrics_port)
            self.logger.info(f"Started Prometheus metrics server on port {self.metrics_port}")

            # Start metrics collection in background
            self.monitor_thread = Thread(target=self._collect_metrics, daemon=True)
            self.monitor_thread.start()
            return True

        except Exception as e:
            self.logger.error(f"Failed to start performance monitoring: {str(e)}")
            return False

    def _collect_metrics(self) -> None:
        """Continuously collect and update system metrics."""
        while True:
            try:
                # Update CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_usage.set(cpu_percent)

                # Update memory metrics
                memory = psutil.virtual_memory()
                self.memory_usage.set(memory.used)

                # Update disk metrics
                disk = psutil.disk_usage('/')
                self.disk_usage.set(disk.percent)

            except Exception as e:
                self.logger.error(f"Error collecting metrics: {str(e)}")
                self.error_counter.labels(type='metric_collection',
                                        component='system').inc()

            time.sleep(self.collection_interval)

    def track_request(self, method: str, endpoint: str, status: int,
                     response_time: float) -> None:
        """Track HTTP request metrics."""
        if not self.enabled:
            return

        try:
            self.request_counter.labels(
                method=method,
                endpoint=endpoint,
                status=str(status)
            ).inc()

            self.response_time.labels(
                method=method,
                endpoint=endpoint
            ).observe(response_time)

        except Exception as e:
            self.logger.error(f"Error tracking request metrics: {str(e)}")

    def update_task_count(self, count: int) -> None:
        """Update the number of active tasks."""
        if self.enabled:
            self.active_tasks.set(count)

    def record_error(self, error_type: str, component: str) -> None:
        """Record an application error."""
        if self.enabled:
            self.error_counter.labels(
                type=error_type,
                component=component
            ).inc()

    def stop(self) -> None:
        """Stop the performance monitoring."""
        self.enabled = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        self.logger.info("Stopped performance monitoring")