import pynamodb
from pynamodb.models import Model
import pytz
from datetime import datetime
import time

class UserData(Model):
    class Meta:
        table_name = 'User_data_IML_DRP'
        region = 'us-east-1'
        aws_access_key_id="AKIA47CR2BY3NO7RAE43"
        aws_secret_access_key="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"
        
    message_id = pynamodb.attributes.UnicodeAttribute(hash_key=True) ## hash key = True means this is the primary key
    incoming_message = pynamodb.attributes.UnicodeAttribute()
    reply = pynamodb.attributes.UnicodeAttribute()
        
UserData.create_table(read_capacity_units=5, write_capacity_units=5, billing_mode='PROVISIONED')

class ThreadData(Model):
    class Meta:
        table_name = 'thread_data_IML_DRP'
        region = 'us-east-1'
        aws_access_key_id="AKIA47CR2BY3NO7RAE43"
        aws_secret_access_key="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"
        
    phone_number = pynamodb.attributes.UnicodeAttribute(hash_key=True)
    thread_ID = pynamodb.attributes.UnicodeAttribute()
        
ThreadData.create_table(read_capacity_units=10, write_capacity_units=10, billing_mode='PROVISIONED')

class ThreadLessData(Model):
    class Meta:
        table_name = "thread_less_data"
        region = "us-east-1"
        aws_access_key_id = "AKIA47CR2BY3NO7RAE43"
        aws_secret_access_key = "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"
    message_id = pynamodb.attributes.UnicodeAttribute(hash_key=True) ## hash key = True means this is the primary key
    phone_number = pynamodb.attributes.UnicodeAttribute()
    incoming_message = pynamodb.attributes.UnicodeAttribute()
    reply = pynamodb.attributes.UnicodeAttribute()
    thread_ID = pynamodb.attributes.UnicodeAttribute()
    
ThreadLessData.create_table(read_capacity_units=10, write_capacity_units=10, billing_mode='PROVISIONED')

class ThreadDataSixHours(Model):
    class Meta:
        table_name = "thread_data_six_hours"
        region = "us-east-1"
        aws_access_key_id = "AKIA47CR2BY3NO7RAE43"
        aws_secret_access_key = "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"
    message_id = pynamodb.attributes.UnicodeAttribute(hash_key=True) ## hash key = True means this is the primary key
    phone_number = pynamodb.attributes.UnicodeAttribute()
    incoming_message = pynamodb.attributes.UnicodeAttribute()
    reply = pynamodb.attributes.UnicodeAttribute()
    thread_ID = pynamodb.attributes.UnicodeAttribute()
    sent_at = pynamodb.attributes.UnicodeAttribute()
    thread_created_at = pynamodb.attributes.UTCDateTimeAttribute(default= datetime.now(pytz.utc))
    def from_datetime(cls, dt):
        # Convert the datetime to Pakistan time zone
        tz = pytz.timezone('Asia/Karachi')
        local_dt = dt.astimezone(tz)
        # Format the datetime as a string
        return local_dt.strftime('%Y-%m-%d %H:%M:%S %Z%z')

    def save(self, **kwargs):
        # Set the created_at attribute to the current time in Pakistan time zone
        self.sent_at = self.from_datetime(datetime.now())
        return super(ThreadDataSixHours, self).save(**kwargs)
    
ThreadDataSixHours.create_table(read_capacity_units=10, write_capacity_units=10, billing_mode='PROVISIONED')
    
    
    