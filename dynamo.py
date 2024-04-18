import pynamodb
from pynamodb.models import Model

class User(Model):
    class Meta:
        table_name = 'User_data_IML_DRP'
        region = 'us-east-1'
        aws_access_key_id="AKIA47CR2BY3NO7RAE43"
        aws_secret_access_key="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"
        
    message_id = pynamodb.attributes.UnicodeAttribute(hash_key=True) ## hash key = True means this is the primary key
    incoming_message = pynamodb.attributes.UnicodeAttribute()
    reply = pynamodb.attributes.UnicodeAttribute()
        
        
User.create_table(read_capacity_units=5, write_capacity_units=5, billing_mode='PROVISIONED')
class User(Model):
    class Meta:
        table_name = 'thread_data_IML_DRP'
        region = 'us-east-1'
        aws_access_key_id="AKIA47CR2BY3NO7RAE43"
        aws_secret_access_key="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"
        
    phone_number = pynamodb.attributes.UnicodeAttribute(hash_key=True)
    thread_ID = pynamodb.attributes.UnicodeAttribute()
        
User.create_table(read_capacity_units=10, write_capacity_units=10, billing_mode='PROVISIONED')

class User(Model):
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
    
User.create_table(read_capacity_units=10, write_capacity_units=10, billing_mode='PROVISIONED')


    
    
    