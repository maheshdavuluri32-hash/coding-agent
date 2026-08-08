import os
import json
import argparse

class TodoList:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                json.dump([], f)

    def add(self, task):
        tasks = self.load()
        tasks.append(task)
        self.save(tasks)

    def view(self):
        tasks = self.load()
        for i, task in enumerate(tasks):
            print(f"{i+1}. {task['description']}")
            if 'done' in task and task['done']:
                print("Done")

    def delete(self, index):
        try:
            tasks = self.load()
            del tasks[index-1]
            self.save(tasks)
        except IndexError:
            print("Invalid index")

    def mark_done(self, index):
        try:
            tasks = self.load()
            tasks[index-1]['done'] = True
            self.save(tasks)
        except IndexError:
            print("Invalid index")

    def load(self):
        with open(self.filename, 'r') as f:
            return json.load(f)

    def save(self, tasks):
        with open(self.filename, 'w') as f:
            json.dump(tasks, f, indent=4)


def main():
    todo = TodoList('todo.json')
    parser = argparse.ArgumentParser(description='To-Do List CLI')
    subparsers = parser.add_subparsers(dest='command')

    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('task', help='Task description')

    view_parser = subparsers.add_parser('view', help='View all tasks')
    view_parser.set_defaults(command='view')

    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('index', type=int, help='Task index')

    mark_done_parser = subparsers.add_parser('mark-done', help='Mark a task as done')
    mark_done_parser.add_argument('index', type=int, help='Task index')

    args = parser.parse_args()

    if args.command == 'add':
        todo.add(args.task)
    elif args.command == 'view':
        todo.view()
    elif args.command == 'delete':
        todo.delete(args.index)
    elif args.command == 'mark-done':
        todo.mark_done(args.index)


if __name__ == '__main__':
    main()