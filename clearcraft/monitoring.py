"""
Health monitoring and diagnostics for ClearCraft.

Provides utilities for checking system health, resource usage,
and performance metrics.
"""

import psutil
import platform
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class SystemHealth:
    """System health metrics."""

    status: str  # "healthy", "degraded", "unhealthy"
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    uptime_seconds: float
    timestamp: str
    warnings: list[str]


@dataclass
class ModelHealth:
    """Model availability health check."""

    spacy_available: bool
    sentence_transformers_available: bool
    language_tool_available: bool
    warnings: list[str]


class HealthMonitor:
    """Monitors system and application health."""

    def __init__(self):
        """Initialize health monitor."""
        self.start_time = datetime.now()

    def check_system_health(self) -> SystemHealth:
        """
        Check system resource health.

        Returns:
            SystemHealth with current metrics.
        """
        warnings = []

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            warnings.append(f"High CPU usage: {cpu_percent:.1f}%")

        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        if memory_percent > 90:
            warnings.append(f"High memory usage: {memory_percent:.1f}%")

        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        if disk_percent > 90:
            warnings.append(f"High disk usage: {disk_percent:.1f}%")

        # Uptime
        uptime = (datetime.now() - self.start_time).total_seconds()

        # Determine overall status
        if len(warnings) > 2:
            status = "unhealthy"
        elif len(warnings) > 0:
            status = "degraded"
        else:
            status = "healthy"

        return SystemHealth(
            status=status,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            uptime_seconds=uptime,
            timestamp=datetime.now().isoformat(),
            warnings=warnings,
        )

    def check_model_health(self) -> ModelHealth:
        """
        Check model availability.

        Returns:
            ModelHealth with model availability status.
        """
        warnings = []

        # Check spaCy
        spacy_available = False
        try:
            import spacy
            try:
                spacy.load("en_core_web_sm")
                spacy_available = True
            except OSError:
                warnings.append("spaCy model 'en_core_web_sm' not found")
        except ImportError:
            warnings.append("spaCy not installed")

        # Check sentence-transformers
        sentence_transformers_available = False
        try:
            from sentence_transformers import SentenceTransformer
            sentence_transformers_available = True
        except ImportError:
            warnings.append("sentence-transformers not installed")

        # Check language_tool_python
        language_tool_available = False
        try:
            import language_tool_python
            language_tool_available = True
        except ImportError:
            warnings.append("language_tool_python not installed (optional)")

        return ModelHealth(
            spacy_available=spacy_available,
            sentence_transformers_available=sentence_transformers_available,
            language_tool_available=language_tool_available,
            warnings=warnings,
        )

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.

        Returns:
            Dictionary with system details.
        """
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        }

    def get_comprehensive_health(self) -> Dict[str, Any]:
        """
        Get comprehensive health report.

        Returns:
            Dictionary with all health metrics.
        """
        system_health = self.check_system_health()
        model_health = self.check_model_health()
        system_info = self.get_system_info()

        return {
            "overall_status": system_health.status,
            "timestamp": system_health.timestamp,
            "system": {
                "cpu_percent": system_health.cpu_percent,
                "memory_percent": system_health.memory_percent,
                "disk_percent": system_health.disk_percent,
                "uptime_seconds": system_health.uptime_seconds,
            },
            "models": {
                "spacy": model_health.spacy_available,
                "sentence_transformers": model_health.sentence_transformers_available,
                "language_tool": model_health.language_tool_available,
            },
            "system_info": system_info,
            "warnings": system_health.warnings + model_health.warnings,
        }


# Global instance
health_monitor = HealthMonitor()
