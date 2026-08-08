def tower_of_hanoi(n, source, target, auxiliary):
    if n > 0:
        # Move n - 1 disks from source to auxiliary, so they are out of the way
        tower_of_hanoi(n-1, source, auxiliary, target)

        # Move the nth disk from source to target
        print(f'Move disk {n} from peg {source} to peg {target}')

        # Move the n - 1 disks that we left on auxiliary to target
        tower_of_hanoi(n-1, auxiliary, target, source)