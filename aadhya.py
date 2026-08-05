class Student:
    def __init__(self, name, roll_no, age, marks):
        self.name = name
        self.roll_no = roll_no
        self.age = age
        self.marks = marks

    def display_details(self):
        print(f"Name: {self.name}")
        print(f"Roll No: {self.roll_no}")
        print(f"Age: {self.age}")
        print(f"Marks: {self.marks}")

def main():
    name = input("Enter student's name: ")
    roll_no = int(input("Enter student's roll no: "))
    age = int(input("Enter student's age: "))
    marks = float(input("Enter student's marks: "))

    s = Student(name, roll_no, age, marks)
    s.display_details()

if __name__ == "__main__":
    main()