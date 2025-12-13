# Program 1: Increment Loop
# Expected: mem[0] = 11

ADDI $t0, $zero, 10
ADDI $t1, $zero, 1
ADD  $t2, $t0, $t1
SW   $t2, 0($zero)
