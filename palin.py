
def is_palindrome(s):
    s = ''.join(c for c in s if c.isalnum()).lower()
    return s == s[::-1]

s = input("Enter a string: ")
print(f"'{s}' {'is' if is_palindrome(s) else 'is not'} a palindrome.")