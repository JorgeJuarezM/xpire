; main program
main:
    call load_immediate
    call load_from_memory
    call increment
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
    ret
