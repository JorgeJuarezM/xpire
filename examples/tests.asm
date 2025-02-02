; Load immediate value to register
load_inmmediate:
    MVI a, 1
    MVI b, 2
    MVI c, 3
    MVI d, 4
    MVI e, 5
    MVI h, 6
    MVI l, 7
    call load_from_memory
    hlt

; load from memory
load_from_memory:
    LDA 0h
    call increment
    ret

; increment
increment:
    INR a
    ret
