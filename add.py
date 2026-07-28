```python
def add_numbers(num1, num2):
    return num1 + num2

while True:
    try:
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        break
    except ValueError:
        print("Invalid input. Please enter a valid number.")

result = add_numbers(num1, num2)
print(f"The sum of {num1} and {num2} is {result}.")
```