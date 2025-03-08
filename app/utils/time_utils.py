from datetime import datetime
import pytz

def get_current_timestamp_utc():
    return datetime.now(tz=pytz.timezone('UTC'))

def convert_date_to_iso_date(date_string):
    return datetime.fromisoformat(date_string)

def get_datetime():
    return datetime.now()