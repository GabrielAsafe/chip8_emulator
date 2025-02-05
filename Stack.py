class Stack:
    def __init__(self):
        self.lifo = []  # Inicializa a pilha como uma lista vazia

    def push(self, value):
        self.lifo.append(value)  # Adiciona um valor no topo da pilha

    def pop(self):
        if self.lifo:
            return self.lifo.pop()  # Remove e retorna o topo da pilha
        else:
            raise IndexError("Stack underflow: trying to pop from an empty stack")

    def get(self):
        if self.lifo:
            return self.lifo[-1]  # Retorna o topo da pilha sem remover
        else:
            return None  # Retorna None se a pilha estiver vazia

