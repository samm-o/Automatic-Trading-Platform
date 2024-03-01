from datetime import datetime
import pytz

def isDST():
    """Determine whether or not Daylight Savings Time is in effect"""
    
    x = datetime(datetime.now().year, 1, 1, 0, 0, 0, tzinfo=pytz.timezone('US/Eastern'))
    y = datetime.now(pytz.timezone('US/Eastern'))
    
    return not (y.utcoffset() == x.utcoffset())

print(isDST())