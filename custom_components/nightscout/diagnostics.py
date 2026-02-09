"""Diagnostics and system management for Nightscout integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class NightscoutDiagnostics:
    """Class for Nightscout diagnostics and monitoring."""

    def __init__(self, api: Any, url: str) -> None:
        """Initialize diagnostics."""
        self.api = api
        self.url = url
        self.base_domain = self._extract_domain(url)

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return url

    async def check_server_availability(self) -> dict[str, Any]:
        """Check if Nightscout server is available.
        
        Returns:
            Dictionary with availability status
        """
        try:
            status = await self.api.get_status()
            if status:
                return {
                    "available": True,
                    "status": "online",
                    "response_time": datetime.now().isoformat(),
                }
            return {
                "available": False,
                "status": "offline",
                "error": "No status returned",
            }
        except Exception as err:
            _LOGGER.error("Server availability check failed: %s", err)
            return {
                "available": False,
                "status": "error",
                "error": str(err),
            }

    async def check_dns_resolution(self) -> dict[str, Any]:
        """Check if domain name resolves.
        
        Returns:
            Dictionary with DNS resolution status
        """
        try:
            import socket
            # Extract hostname from URL
            hostname = self.base_domain
            ip_address = socket.gethostbyname(hostname)
            
            return {
                "resolved": True,
                "hostname": hostname,
                "ip_address": ip_address,
                "status": "ok",
            }
        except Exception as err:
            _LOGGER.error("DNS resolution failed: %s", err)
            return {
                "resolved": False,
                "hostname": self.base_domain,
                "status": "error",
                "error": str(err),
            }

    async def check_data_freshness(self) -> dict[str, Any]:
        """Check freshness of glucose and AAPS data.
        
        Returns:
            Dictionary with data freshness status
        """
        try:
            entries = await self.api.get_entries(count=1)
            devicestatus = await self.api.get_devicestatus(count=1)

            glucose_status = self._check_entry_age(entries)
            aaps_status = self._check_devicestatus_age(devicestatus)

            return {
                "glucose": glucose_status,
                "aaps": aaps_status,
                "overall_status": self._get_worst_status(
                    glucose_status["status"], aaps_status["status"]
                ),
            }
        except Exception as err:
            _LOGGER.error("Data freshness check failed: %s", err)
            return {
                "glucose": {"status": "error", "error": str(err)},
                "aaps": {"status": "error", "error": str(err)},
                "overall_status": "error",
            }

    def _check_entry_age(self, entries: list[dict[str, Any]]) -> dict[str, Any]:
        """Check age of last glucose entry."""
        if not entries:
            return {
                "status": "critical",
                "message": "No glucose data",
                "age_minutes": None,
            }

        entry = entries[0]
        timestamp = entry.get("date", 0)
        age_minutes = (datetime.now().timestamp() * 1000 - timestamp) / 60000

        if age_minutes > 25:
            status = "critical"
        elif age_minutes > 10:
            status = "warning"
        else:
            status = "ok"

        return {
            "status": status,
            "age_minutes": round(age_minutes, 1),
            "last_update": datetime.fromtimestamp(timestamp / 1000).isoformat(),
            "message": f"Last glucose reading {round(age_minutes, 1)} minutes ago",
        }

    def _check_devicestatus_age(self, devicestatus: list[dict[str, Any]]) -> dict[str, Any]:
        """Check age of last AAPS devicestatus."""
        if not devicestatus:
            return {
                "status": "critical",
                "message": "No AAPS data",
                "age_minutes": None,
            }

        status = devicestatus[0]
        created_at = status.get("created_at", "")
        
        try:
            timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            age_minutes = (datetime.now().timestamp() - timestamp.timestamp()) / 60

            if age_minutes > 25:
                status_level = "critical"
            elif age_minutes > 10:
                status_level = "warning"
            else:
                status_level = "ok"

            return {
                "status": status_level,
                "age_minutes": round(age_minutes, 1),
                "last_update": created_at,
                "message": f"Last AAPS update {round(age_minutes, 1)} minutes ago",
            }
        except Exception as err:
            _LOGGER.error("Error parsing devicestatus age: %s", err)
            return {
                "status": "error",
                "message": "Could not parse timestamp",
                "error": str(err),
            }

    def _get_worst_status(self, status1: str, status2: str) -> str:
        """Get the worst status between two statuses."""
        priority = {"critical": 3, "error": 3, "warning": 2, "ok": 1}
        priority1 = priority.get(status1, 0)
        priority2 = priority.get(status2, 0)
        
        if priority1 >= priority2:
            return status1
        return status2

    async def get_database_size(self) -> dict[str, Any]:
        """Get approximate database size from Nightscout status.
        
        Returns:
            Dictionary with database size information
        """
        try:
            status = await self.api.get_status()
            if not status:
                return {
                    "size_mb": None,
                    "status": "error",
                    "error": "Could not get status",
                    "message": "Unable to connect to Nightscout",
                }

            # Try to get database size from status
            # Note: Actual size may not be available in all Nightscout installations
            # We estimate based on entries count
            entries_count = self._estimate_entries_count(status)
            
            # Rough estimation: ~0.5 KB per entry average
            estimated_size_mb = None
            if entries_count:
                estimated_size_mb = round((entries_count * 0.5) / 1024, 1)
            
            # Database size warning thresholds (in MB)
            limit = 500
            warning_threshold = limit * 0.7  # 70%
            critical_threshold = limit * 0.9  # 90%

            # Determine status
            db_status = "ok"
            message = "Database size monitoring active"
            
            if estimated_size_mb is not None:
                if estimated_size_mb >= critical_threshold:
                    db_status = "critical"
                    message = f"Database size critical: {estimated_size_mb} MB"
                elif estimated_size_mb >= warning_threshold:
                    db_status = "warning"
                    message = f"Database size warning: {estimated_size_mb} MB"
                else:
                    message = f"Database size: {estimated_size_mb} MB"

            return {
                "size_mb": estimated_size_mb,
                "limit_mb": limit,
                "warning_threshold_mb": warning_threshold,
                "critical_threshold_mb": critical_threshold,
                "status": db_status,
                "message": message,
            }
        except Exception as err:
            _LOGGER.error("Database size check failed: %s", err)
            return {
                "size_mb": None,
                "status": "error",
                "error": str(err),
                "message": "Database size check failed",
            }
    
    def _estimate_entries_count(self, status: dict[str, Any]) -> int | None:
        """Estimate number of entries from Nightscout status.
        
        Args:
            status: Status dictionary from Nightscout API
            
        Returns:
            Estimated number of entries or None
        """
        try:
            # Try to get from settings if available
            settings = status.get("settings", {})
            
            # Some Nightscout instances may provide this info
            # For now, return None as this requires additional API call
            # Future: could call /api/v1/entries.json?count=0 to get total
            return None
        except Exception:
            return None

    async def get_full_diagnostics(self) -> dict[str, Any]:
        """Get comprehensive diagnostics.
        
        Returns:
            Dictionary with all diagnostic information
        """
        availability = await self.check_server_availability()
        dns = await self.check_dns_resolution()
        freshness = await self.check_data_freshness()
        db_size = await self.get_database_size()

        return {
            "server_availability": availability,
            "dns_resolution": dns,
            "data_freshness": freshness,
            "database_size": db_size,
            "timestamp": datetime.now().isoformat(),
        }


class DDNSManager:
    """Manager for DDNS services."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize DDNS manager."""
        self.session = session

    async def update_freedns(
        self, update_url: str
    ) -> dict[str, Any]:
        """Update FreeDNS hostname.
        
        Args:
            update_url: FreeDNS update URL (from freedns.afraid.org)
            
        Returns:
            Dictionary with update status
        """
        try:
            async with self.session.get(update_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                response.raise_for_status()
                content = await response.text()
                
                return {
                    "service": "FreeDNS",
                    "status": "success",
                    "response": content,
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as err:
            _LOGGER.error("FreeDNS update failed: %s", err)
            return {
                "service": "FreeDNS",
                "status": "error",
                "error": str(err),
                "timestamp": datetime.now().isoformat(),
            }

    async def update_duckdns(
        self, domain: str, token: str
    ) -> dict[str, Any]:
        """Update DuckDNS hostname.
        
        Args:
            domain: DuckDNS domain name (without .duckdns.org)
            token: DuckDNS token
            
        Returns:
            Dictionary with update status
        """
        url = f"https://www.duckdns.org/update?domains={domain}&token={token}&ip="
        
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                response.raise_for_status()
                content = await response.text()
                
                if content.strip() == "OK":
                    status = "success"
                else:
                    status = "error"
                
                return {
                    "service": "DuckDNS",
                    "status": status,
                    "response": content,
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as err:
            _LOGGER.error("DuckDNS update failed: %s", err)
            return {
                "service": "DuckDNS",
                "status": "error",
                "error": str(err),
                "timestamp": datetime.now().isoformat(),
            }

    async def check_domain_expiry(
        self, domain: str, expiry_date: str
    ) -> dict[str, Any]:
        """Check if domain is approaching expiry.
        
        Args:
            domain: Domain name
            expiry_date: Expiry date in ISO format (YYYY-MM-DD)
            
        Returns:
            Dictionary with expiry status
        """
        try:
            expiry = datetime.fromisoformat(expiry_date)
            now = datetime.now()
            days_remaining = (expiry - now).days

            if days_remaining < 0:
                status = "expired"
            elif days_remaining < 7:
                status = "critical"
            elif days_remaining < 30:
                status = "warning"
            else:
                status = "ok"

            return {
                "domain": domain,
                "expiry_date": expiry_date,
                "days_remaining": days_remaining,
                "status": status,
                "message": f"Domain expires in {days_remaining} days",
            }
        except Exception as err:
            _LOGGER.error("Domain expiry check failed: %s", err)
            return {
                "domain": domain,
                "status": "error",
                "error": str(err),
            }


# Admin tools categories
ADMIN_TOOLS_CATEGORIES = {
    "diagnostics": {
        "name": "Diagnostics",
        "description": "System health and monitoring tools",
        "tools": [
            {"id": "server_status", "name": "Server Status Check"},
            {"id": "data_freshness", "name": "Data Freshness Monitor"},
            {"id": "dns_check", "name": "DNS Resolution Check"},
            {"id": "database_size", "name": "Database Size Monitor"},
        ],
    },
    "ddns_management": {
        "name": "DDNS Management",
        "description": "Dynamic DNS management tools",
        "tools": [
            {"id": "freedns_update", "name": "FreeDNS Update"},
            {"id": "duckdns_update", "name": "DuckDNS Update"},
            {"id": "domain_expiry", "name": "Domain Expiry Check"},
        ],
    },
    "data_management": {
        "name": "Data Management",
        "description": "Database and data cleanup tools",
        "tools": [
            {"id": "cleanup_old_data", "name": "Clean Old Data (>3 months)"},
            {"id": "database_cleanup", "name": "Database Optimization"},
            {"id": "export_data", "name": "Export Data"},
        ],
    },
}


def get_admin_tools_categories() -> dict[str, Any]:
    """Get all available admin tool categories.
    
    Returns:
        Dictionary of admin tool categories
    """
    return ADMIN_TOOLS_CATEGORIES
