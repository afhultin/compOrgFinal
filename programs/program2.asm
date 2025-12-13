# Program 2: Summation Loop
# Expected: mem[0] = 15

ADDI $t0, $zero, 5      # counter
ADDI $t1, $zero, 0      # sum

LOOP:
    ADD  $t1, $t1, $t0
    ADDI $t0, $t0, -1
    BEQ  $t0, $zero, END
    BEQ  $zero, $zero, LOOP

END:
    SW   $t1, 0($zero)
