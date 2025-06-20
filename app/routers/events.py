from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta, timezone
import requests

router = APIRouter(prefix="/events", tags=["Celestial Events"])

# Constants
API_KEY = "2QHFXH-DGEVGX-3PL9YY-5IBZ"
SATELLITE_ID = 25544  # ISS
DAYS = 5
MAX_PASSES = 20
IST = timezone(timedelta(hours=5, minutes=30))


# Pydantic models (optionally move these to schemas/events.py later)
class VisiblePass(BaseModel):
    time_ist: str
    date_ist: str
    direction: str
    duration: str  # minutes and seconds

class MeteorShower(BaseModel):
    name: str
    date_range: str
    peak_location: str
    hemisphere: str

class EclipseEvent(BaseModel):
    date: str
    type: str


@router.get("/visible-passes", response_model=List[VisiblePass])
def get_visible_passes(lat: float = Query(28.6139, description="Latitude of location"),
                       lon: float = Query(77.2090, description="Longitude of location"),
                       alt: int = Query(0, description="Altitude in meters")):
    """
    Fetch visible ISS passes for the next 5 days from user's location (if visible mag < 2.5 and elevation > 10°)
    """
    url = f"https://api.n2yo.com/rest/v1/satellite/visualpasses/{SATELLITE_ID}/{lat}/{lon}/{alt}/{DAYS}/{MAX_PASSES}?apiKey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    visible_passes = []
    for p in data['passes']:
        if p['mag'] < 2.5 and p['maxEl'] > 10:
            start_time_ist = datetime.utcfromtimestamp(p['startUTC']).replace(tzinfo=timezone.utc).astimezone(IST)
            minutes = p['duration'] // 60
            seconds = p['duration'] % 60
            formatted_duration = f"{minutes} min {seconds} sec" if minutes else f"{seconds} sec"
            visible_passes.append(VisiblePass(
                time_ist=start_time_ist.strftime('%H:%M:%S IST'),
                date_ist=start_time_ist.strftime('%Y-%m-%d'),
                direction=p['startAzCompass'],
                duration=formatted_duration
            ))

    return visible_passes


@router.get("/meteor-showers", response_model=List[MeteorShower])
def get_meteor_showers():
    """
    List upcoming meteor showers with their peak dates, locations and visibility hemisphere.
    """
    return [
        MeteorShower(
            name="Perseids",
            date_range="12–13 Aug 2025",
            peak_location="New Delhi",
            hemisphere="Northern Hemisphere (Best)"
        ),
        MeteorShower(
            name="Draconids",
            date_range="8–9 Oct 2025",
            peak_location="New Delhi",
            hemisphere="Northern Hemisphere (Best)"
        )
    ]


@router.get("/solar-eclipses", response_model=List[EclipseEvent])
def get_solar_eclipses():
    """
    List upcoming Solar eclipses with their type and date.
    """
    return [
        EclipseEvent(date="21 Sep 2025", type="Partial Solar Eclipse"),
        EclipseEvent(date="17 Feb 2026", type="Annular Solar Eclipse"),
        EclipseEvent(date="12 Aug 2026", type="Total Solar Eclipse")
    ]


@router.get("/lunar-eclipses", response_model=List[EclipseEvent])
def get_lunar_eclipses():
    """
    List upcoming Lunar eclipses with their type and date.
    """
    return [
        EclipseEvent(date="7 Sep 2025", type="Total Lunar Eclipse"),
        EclipseEvent(date="3 Mar 2026", type="Total Lunar Eclipse"),
        EclipseEvent(date="28 Aug 2026", type="Partial Lunar Eclipse")
    ]
