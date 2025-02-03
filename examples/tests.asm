; main program
main:
    call load_immediate
    call load_from_memory
    call increment
    call increment_pairs
    hlt

; Load immediate value to register
load_immediate:
    MVI a, 1
    MVI b, 2
    MVI c, 3
    MVI d, 4
    MVI e, 5
    MVI h, 6
    MVI l, 7
    ret

; load from memory
load_from_memory:
    LDA 0h
    ret

; increment
increment:
    INR a
    INR b
    INR c
    INR d
    INR e
    INR h
    INR l
    ret

increment_pairs:
    INX bc
    INX de
    INX hl
    ret