#!/usr/bin/env python3

import argparse
import datetime
import sys
from database import Task, db

def list_tasks(args):
    """List all tasks with optional filtering"""
    db.connect(reuse_if_open=True)
    
    query = Task.select()
    
    # Apply filters if provided
    if args.status:
        query = query.where(Task.status == args.status)
    if args.priority:
        query = query.where(Task.priority == args.priority)
    if args.due:
        due_date = datetime.datetime.strptime(args.due, '%Y-%m-%d').date()
        query = query.where(Task.due_date == due_date)
    
    # Execute query and display results
    if query.count() == 0:
        print("No tasks found.")
    else:
        print(f"{'ID':<5} {'Title':<30} {'Status':<10} {'Priority':<10} {'Due Date':<12}")
        print("-" * 70)
        for task in query:
            due_str = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'
            print(f"{task.id:<5} {task.title[:30]:<30} {task.status:<10} {task.priority or 'None':<10} {due_str:<12}")
    
    db.close()

def add_task(args):
    """Add a new task"""
    db.connect(reuse_if_open=True)
    
    # Parse due date if provided
    due_date = None
    if args.due:
        try:
            due_date = datetime.datetime.strptime(args.due, '%Y-%m-%d').date()
        except ValueError:
            print("Error: Due date should be in format YYYY-MM-DD")
            db.close()
            return
    
    # Create task
    try:
        task = Task.create(
            title=args.title,
            description=args.description,
            priority=args.priority,
            due_date=due_date
        )
        print(f"Task added successfully with ID: {task.id}")
    except Exception as e:
        print(f"Error adding task: {e}")
    
    db.close()

def update_task(args):
    """Update an existing task"""
    db.connect(reuse_if_open=True)
    
    try:
        task = Task.get_by_id(args.id)
        
        # Update fields if provided
        if args.title:
            task.title = args.title
        if args.description:
            task.description = args.description
        if args.status:
            task.status = args.status
        if args.priority:
            task.priority = args.priority
        if args.due:
            task.due_date = datetime.datetime.strptime(args.due, '%Y-%m-%d').date()
        
        task.save()
        print(f"Task {args.id} updated successfully.")
    except Task.DoesNotExist:
        print(f"Error: Task with ID {args.id} not found.")
    except Exception as e:
        print(f"Error updating task: {e}")
    
    db.close()

def delete_task(args):
    """Delete a task by ID"""
    db.connect(reuse_if_open=True)
    
    try:
        task = Task.get_by_id(args.id)
        task.delete_instance()
        print(f"Task {args.id} deleted successfully.")
    except Task.DoesNotExist:
        print(f"Error: Task with ID {args.id} not found.")
    except Exception as e:
        print(f"Error deleting task: {e}")
    
    db.close()

def complete_task(args):
    """Mark a task as done"""
    db.connect(reuse_if_open=True)
    
    try:
        task = Task.get_by_id(args.id)
        task.status = 'done'
        task.save()
        print(f"Task {args.id} marked as done.")
    except Task.DoesNotExist:
        print(f"Error: Task with ID {args.id} not found.")
    except Exception as e:
        print(f"Error completing task: {e}")
    
    db.close()

def show_task(args):
    """Show detailed information about a task"""
    db.connect(reuse_if_open=True)
    
    try:
        task = Task.get_by_id(args.id)
        print(f"\nTask #{task.id}")
        print(f"{'Title:':<12} {task.title}")
        print(f"{'Description:':<12} {task.description or 'None'}")
        print(f"{'Status:':<12} {task.status}")
        print(f"{'Priority:':<12} {task.priority or 'None'}")
        
        if task.due_date:
            due_str = task.due_date.strftime('%Y-%m-%d')
            days_left = (task.due_date - datetime.date.today()).days
            if days_left < 0:
                due_info = f"{due_str} (Overdue by {abs(days_left)} days)"
            elif days_left == 0:
                due_info = f"{due_str} (Due today)"
            else:
                due_info = f"{due_str} ({days_left} days left)"
            print(f"{'Due Date:':<12} {due_info}")
        else:
            print(f"{'Due Date:':<12} None")
        
        print(f"{'Created:':<12} {task.created_date.strftime('%Y-%m-%d %H:%M')}")
    except Task.DoesNotExist:
        print(f"Error: Task with ID {args.id} not found.")
    except Exception as e:
        print(f"Error retrieving task: {e}")
    
    db.close()

def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(description='CLI Task Manager')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Parser for the "list" command
    list_parser = subparsers.add_parser('list', help='List all tasks')
    list_parser.add_argument('--status', choices=['pending', 'done', 'overdue'], help='Filter by status')
    list_parser.add_argument('--priority', choices=['high', 'medium', 'low'], help='Filter by priority')
    list_parser.add_argument('--due', help='Filter by due date (YYYY-MM-DD)')
    list_parser.add_argument('--sort', choices=['priority', 'due', 'created'], default='created', 
                            help='Sort tasks by priority, due date, or creation date')
    
    # Parser for the "add" command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('--title', help='Task title')
    add_parser.add_argument('--description', help='Task description')
    add_parser.add_argument('--priority', choices=['high', 'medium', 'low'], default='medium', help='Task priority')
    add_parser.add_argument('--due', help='Due date (YYYY-MM-DD)')
    
    # Parser for the "update" command
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('id', type=int, help='Task ID')
    update_parser.add_argument('--title', help='New task title')
    update_parser.add_argument('--description', help='New task description')
    update_parser.add_argument('--status', choices=['pending', 'done', 'overdue'], help='New task status')
    update_parser.add_argument('--priority', choices=['high', 'medium', 'low'], help='New task priority')
    update_parser.add_argument('--due', help='New due date (YYYY-MM-DD)')
    
    # Parser for the "delete" command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('id', type=int, help='Task ID')
    
    # Parser for the "complete" command
    complete_parser = subparsers.add_parser('complete', help='Mark a task as done')
    complete_parser.add_argument('id', type=int, help='Task ID')
    
    # Parser for the "show" command
    show_parser = subparsers.add_parser('show', help='Show detailed task information')
    show_parser.add_argument('id', type=int, help='Task ID')
    
    # Parse arguments and call the appropriate function
    args = parser.parse_args()
    
    if args.command == 'list':
        list_tasks(args)
    elif args.command == 'add':
        add_task(args)
    elif args.command == 'update':
        update_task(args)
    elif args.command == 'delete':
        delete_task(args)
    elif args.command == 'complete':
        complete_task(args)
    elif args.command == 'show':
        show_task(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    # Import required function from peewee
    from peewee import fn
    main()