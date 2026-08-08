def two_sum(nums, target):
    num_dict = {}
    for i, num in enumerate(nums):
        if target - num in num_dict:
            return [num_dict[target - num], i]
        num_dict[num] = i

print(two_sum([2, 7, 11, 15], 9))  # Output: [0, 1]