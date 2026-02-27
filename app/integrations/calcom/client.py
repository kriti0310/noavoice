import httpx
import logging
from typing import Any, Dict, List, Optional
from app.config.settings import settings
logger = logging.getLogger(__name__)


class CalComAPIError(Exception):
    pass


class CalComClient:

    def __init__(self):
        self.base_url    = settings.CALCOM_BASE_URL
        self.event_type_id = settings.CALCOM_EVENT_TYPE_ID
        self.timeout     = settings.CALCOM_TIMEOUT or 30.0

        self._base_headers = {
            "Authorization": f"Bearer {settings.CALCOM_API_KEY}",
            "Content-Type":  "application/json",
            "cal-api-version": settings.CALCOM_API_VERSION,
        }

        # Slots endpoint requires a different API version
        self._slot_headers = {
            **self._base_headers,
            "cal-api-version": "2024-09-04",
        }

    # ─── Core Request ─────────────────────────────────────────────────────────

    async def _request(
        self,
        method:   str,
        endpoint: str,
        data:     Optional[Dict[str, Any]] = None,
        params:   Optional[Dict[str, Any]] = None,
        headers:  Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                logger.info(f"📡 CalCom {method.upper()} → {url}")

                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers or self._base_headers,
                    json=data,
                    params=params,
                )

                response.raise_for_status()
                result = response.json()

                logger.info(f"✅ CalCom response: {result.get('status')}")
                return result

            except httpx.HTTPStatusError as e:
                logger.error(f"❌ CalCom HTTP {e.response.status_code}: {e.response.text}")
                raise CalComAPIError(f"HTTP {e.response.status_code}: {e.response.text}")

            except httpx.TimeoutException:
                logger.error("❌ CalCom request timed out")
                raise CalComAPIError("Request timed out")

            except Exception as e:
                logger.error(f"❌ CalCom unexpected error: {e}")
                raise

    # ─── Slots ────────────────────────────────────────────────────────────────

    async def get_available_slots(
        self,
        start_date: str,
        end_date:   str,
        timezone:   str = "Asia/Kolkata",
    ) -> List[str]:
        """
        Get available time slots.
        Args:
            start_date: "2024-08-13" (YYYY-MM-DD)
            end_date:   "2024-08-14" (YYYY-MM-DD)
            timezone:   "Asia/Kolkata"
        Returns:
            List of available ISO time strings
        """
        params = {
            "eventTypeId": self.event_type_id,
            "start":       start_date,
            "end":         end_date,
            "timeZone":    timezone,
        }

        res   = await self._request("GET", "/slots", params=params, headers=self._slot_headers)
        slots = res.get("data", {}).get("slots", {})

        return [
            s["time"]
            for day in slots.values()
            for s in day
        ]

    # ─── Bookings ─────────────────────────────────────────────────────────────

    async def create_booking(
        self,
        start:    str,
        name:     str,
        email:    str,
        timezone: str = "Asia/Kolkata",
        phone:    Optional[str] = None,
        notes:    Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new booking.
        Args:
            start:    "2024-08-13T09:00:00Z" (ISO 8601 UTC)
            name:     "John Doe"
            email:    "john@example.com"
            timezone: "Asia/Kolkata"
            phone:    "+919876543210" (optional)
            notes:    "First visit" (optional)
        """
        payload: Dict[str, Any] = {
            "start":       start,
            "eventTypeId": int(self.event_type_id),
            "attendee": {
                "name":     name,
                "email":    email,
                "timeZone": timezone,
                "language": "en",
            },
        }

        if phone:
            payload["attendee"]["phoneNumber"] = phone

        if notes:
            payload["bookingFieldsResponses"] = {"notes": notes}

        return await self._request("POST", "/bookings", data=payload)

    async def get_booking(self, booking_uid: str) -> Dict[str, Any]:
        """Get a single booking by UID."""
        return await self._request("GET", f"/bookings/{booking_uid}")

    async def get_bookings_by_email(self, email: str) -> Dict[str, Any]:
        """Get all bookings for a patient by email."""
        params = {
            "attendeeEmail": email,
            "eventTypeId":   self.event_type_id,
        }
        return await self._request("GET", "/bookings", params=params)

    async def reschedule_booking(
        self,
        booking_uid: str,
        new_start:   str,
        reason:      Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Reschedule an existing booking.
        Args:
            booking_uid: "abc123xyz"
            new_start:   "2024-08-15T10:00:00Z" (UTC)
            reason:      "Patient requested different time" (optional)
        """
        payload: Dict[str, Any] = {"start": new_start}

        if reason:
            payload["reschedulingReason"] = reason

        return await self._request("POST", f"/bookings/{booking_uid}/reschedule", data=payload)

    async def cancel_booking(
        self,
        booking_uid: str,
        reason:      Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Cancel an existing booking.
        Args:
            booking_uid: "abc123xyz"
            reason:      "Patient cancelled" (optional)
        """
        payload: Dict[str, Any] = {}

        if reason:
            payload["cancellationReason"] = reason

        return await self._request("POST", f"/bookings/{booking_uid}/cancel", data=payload)


# Single instance — import this everywhere
calcom_client = CalComClient()