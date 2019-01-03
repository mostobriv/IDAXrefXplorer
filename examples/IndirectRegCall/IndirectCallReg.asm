section .text
global _start 

_start:
    mov eax, bar
    mov ebx, foo
    add ebx, 4
    call eax

.exit:
	mov eax, 1
	mov ebx, 0
	int 80h

.foo:
	mov eax, 4
	mov ebx, 1
	mov ecx, foostr
	mov edx, foostrLen
	int 80h             

    jmp .exit

.bar:
    mov eax, 4
    mov ebx, 1
    mov ecx, barstr
    mov edx, barstrLen
    int 80h

    jmp .exit



section .data

foostr:     db 'Is it foo?',10
foostrLen:  equ $-foostr

barstr:     db 'Or it is bar?', 10
barstrLen:  equ $-barstr
