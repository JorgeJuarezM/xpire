; main program
main:
    call load_immediate
    call load_from_memory
    call increment
    call decrement
    call increment_pairs
    call jump
    call load_immediate_16
    call store_accumulator_in_memory
    call push_to_stack
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

decrement:
    DCR a
    DCR b
    DCR c
    DCR d
    DCR e
    DCR h
    DCR l
    ret


increment_pairs:
    INX bc
    INX de
    INX hl
    ret

jump:
    JMP jump_to
    jump_to:
        ret

load_immediate_16:
    LXI bc, 0x1234h
    LXI de, 0x5678h
    LXI hl, 0x9012h
    ret

store_accumulator_in_memory:
    STA 0x8888h
    ret

push_to_stack:
    push bc
    push de
    push hl
    pop bc
    pop de
    pop hl
    ret
