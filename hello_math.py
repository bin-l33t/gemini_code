import math

pi_str = str(math.pi)[2:12]
e_str = str(math.e)[2:12]

pi_digits = [int(d) for d in pi_str]
e_digits = [int(d) for d in e_str]

pi_sum = 0
print("Adding pi digits:")
for digit in pi_digits:
    print(digit)
    pi_sum += digit


e_sum = 0
print("Adding e digits:")
for digit in e_digits:
    print(digit)
    e_sum += digit


total_sum = pi_sum + e_sum

print(f"Sum of the first 10 digits of pi: {pi_sum}")
print(f"Sum of the first 10 digits of e: {e_sum}")
print(f"Total sum: {total_sum}")