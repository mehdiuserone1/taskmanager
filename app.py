from database import db , Task

new_task = Task.create(title="test 1",
                       due_date="2023-12-31")