# src/mock_apis/booking_services.py
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Union, Dict

# from langchain_core.tools import tool

from config import BOOKINGS_FILE, DELAY

class Booking:
    def __init__(self, room_id, start_time, end_time, booked_by):
        self.name = booked_by + "_booking"
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time
        self.booked_by = booked_by

    def __repr__(self):
        return (f"Booking(room_id={self.room_id}, name={self.name}, "
                f"booked_by={self.booked_by}, start_time={self.start_time}, "
                f"end_time={self.end_time}")
    
    def to_dict(self):
        # Convert datetime objects to string if necessary
        return {
            "name": self.name,
            "room_id": self.room_id,
            "start_time": self.start_time.isoformat() if isinstance(self.start_time, datetime) else self.start_time,
            "end_time": self.end_time.isoformat() if isinstance(self.end_time, datetime) else self.end_time,
            "booked_by": self.booked_by
        }
# @tool("load_bookings", description="Load existing bookings from external file.")
def load_bookings(
        filepath: Path = BOOKINGS_FILE
    ) -> Dict[str, List[Dict[str, Union[str, datetime]]]]:
    """Load existing bookings from external file."""
    existing_data: Dict[str, List[Dict[str, Union[str, datetime]]]] = {}
    try:
        with open(filepath, "r") as f:
            existing_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: Could not decode existing JSON in {filepath}. Starting fresh.")
        existing_data = {}
    return existing_data



# @tool("check_time_conflict", description="Check if a room has a time conflict for the requested time.")
def check_time_conflict_tool(
        existing_bookings: List[Dict[str, Union[str, datetime]]],
        room_id: int, 
        start_date: Union[str, datetime], 
        start_time: Union[str, datetime], 
        duration_hours: Optional[float]=None,
    ) -> bool:
    """ 
    Check if a room has a time conflict for the requested time. 
    """
    try:
        start_date = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
        start_time = datetime.strptime(start_time, '%I:%M:%S %p') if isinstance(start_time, str) else start_time
        start_time = start_date.replace(hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0)

        end_time = start_time + timedelta(hours=duration_hours)

        room_bookings = existing_bookings.get(room_id, [])
        if not room_bookings:
            return False
        for booking in room_bookings:
            booking_start = datetime.fromisoformat(booking['start_time'])
            booking_end = datetime.fromisoformat(booking['end_time']) + DELAY
            if start_time < booking_end and end_time > booking_start:
                return True
        return False
    
    except Exception as e:
        print(f"Error check_time_conflict_tool: {str(e)}")
        return False

def get_room_reserved_time_slots(
        room_id: Union[int, str], 
        existing_bookings: Dict[str, List[Dict[str, Union[str, datetime]]]]) -> List[Dict]:
    
    free_time_slots = []
    room_id = str(room_id)
    
    return free_time_slots

# @tool("book_room", description="Book a room for the specified time and user.")
def book_room_tool(
        room_id: int, start_time: str, 
        end_time: str, user_name: str
    ) -> Optional[Booking]:
    """Book a room for the specified time and user."""
    existing_bookings = load_bookings()
    room_id = str(room_id)
    room_bookings = existing_bookings.get(room_id, [])

    # create new booking
    new_booking = Booking(
        room_id=room_id,
        start_time=start_time,
        end_time=end_time,
        booked_by=user_name,
    )
    room_bookings.append(new_booking)

    print(f"Current bookings for room {room_id}: {room_bookings}")
    existing_bookings[room_id] = room_bookings
    
    try:
        file_path: Path = BOOKINGS_FILE
        with open(file_path, "w") as f:            
            json.dump(existing_bookings, f, indent=4)
        print(f"Bookings saved successfully to {file_path}")

    except Exception as e:
        print(f"Error saving bookings: {str(e)}")

    return new_booking