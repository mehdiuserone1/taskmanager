from peewee import *
import datetime

db = SqliteDatabase('database.db')

class Task(Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),  
        ('done', 'Done'),
        ('overdue', 'Overdue')
    )
    PRIORITY_CHOICES = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    )
    
    title = CharField(max_length=200)
    description = CharField(max_length=500, null=True)
    status = CharField(choices=STATUS_CHOICES, default='pending')
    priority = CharField(choices=PRIORITY_CHOICES, default='medium', null=True)
    due_date = DateField(null=True)
    created_date = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return f"Task('{self.title}', status='{self.status}', due='{self.due_date}')"
    
    def is_overdue(self):
        """Consistent with from_db logic"""
        return (self.status != 'done' 
            and self.due_date < datetime.date.today())
    @classmethod
    def from_db(cls, db, field_names, model_data, done=False):
        """Override how instances are created from database rows"""
        instance = super().from_db(db, field_names, model_data, done)
        
        # Check overdue status when instance is loaded
        if instance.status != 'done' and instance.due_date < datetime.date.today():
            instance.status = 'overdue'
            # Auto-save if you want persistence (optional)
            instance.save()
            
        return instance
    
    def validate(self):
        if self.status not in ['pending','done','overdue']:
            # print(self.status)
            raise ValueError(f"Status must be one of {self.STATUS_CHOICES}")
        if self.priority not in ['low','medium','high']:
            raise ValueError(f"Priority must be one of {self.PRIORITY_CHOICES}")
 


    # Hook it to save()
    def save(self, *args, **kwargs):
        self.validate()
        super().save(*args, **kwargs)
    
    class Meta:
        database = db
        indexes = (
        # Speeds up status/due_date queries
        (('status', 'due_date'), False),
        (('priority', 'due_date'), False),
    )
        
db.connect()
db.create_tables([Task])
# db.drop_tables([Task])
# db.create_tables([Task])
db.close()