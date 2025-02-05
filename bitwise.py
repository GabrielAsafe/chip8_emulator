'''
OR    |
	é uma soma
	
	4|2 = 6


AND   &
	é uma multiplicação e só importa se o valor é 0 ou não 0

	1 & 44 = 1

XOR ^
	inversor. dois iguais é 0. dois opostos é 1

	1 ^ 1 = 0 


shift left <<   multiplica 	inteiros 
	desloca à esquerda n bits, na sequencia de base 2 a << n
    ou melhor dito
    
    a << n = a*(2^n)
    
    

shift right >>   divide inteiros
	desloca à direita n bits, na sequencia de base 2 a >> n
 	ou melhor dito
    
    a >> n = a / 2^n
    
    
NOT   ~
	negaçao


MASKS 

	isolar número em uma posição 
	
	print(B)1690
	print(A)1024 = pos 10
	print((B&A)>>10)#descubro qual o valor daquele bit naquela posição

'''

#AND
print(1 & 1)
print(1 & 44) #???
print(1 & 1726) #???

print("")
#OR
print(1 | 1) #???
print(1 | 2)
print(1 | 44)
print(1 | 1726)


print("")
#XOR é uma soma mas se os dois forem iguais é 0
print(1 ^ 1) 
print(1 ^ 2)
print(1 ^ 44)
print(1726 ^ 1726)


print("")
#2 4 8 16 32 64 128 256 512
#0 1 2 3  4  5  6   7   8
print(2 << 0) #2
print(2 << 1) #4
print(2 << 2) #8
print(2 << 8)



print("")
#2 4 8 16 32 64 128 256 512
#0 1 2 3  4  5  6   7   8
print(2 >> 0) #2
print(2 >> 1) #4
print(2 >> 2) #8
print(2 >> 8)


B=0b011010011010 #1690
A=1<<10 #1024


print()

A=0b10
B=0b01

print(A|B)


