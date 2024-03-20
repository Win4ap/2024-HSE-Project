class RSA():
    char_to_int = {'a': 1 ,'b': 2 ,'c': 3, 
    'd': 4 , 'e': 5 , 'f': 6 , 'g': 7 , 'h': 8 , 'i': 9, 
    'j': 10, 'k': 11, 'l': 12, 'm': 13, 'n': 14, 'o': 15, 
    'p': 16, 'q': 17, 'r': 18, 's': 19, 't': 20, 'u': 21, 
    'v': 22, 'w': 23, 'x': 24, 'y': 25, 'z': 26, '!': 27, 
    '_': 28, '?': 29, ',': 30, '.': 31, ';': 32, 'A': 33, 
    'B': 34, 'C': 35, 'D': 36, 'E': 37, 'F': 38, 'G': 39, 
    'H': 40, 'I': 41, 'J': 42, 'K': 43, 'L': 44, 'M': 45, 
    'N': 46, 'O': 47, 'P': 48, 'Q': 49, 'R': 50, 'S': 51, 
    'T': 52, 'U': 53, 'V': 54, 'W': 55, 'X': 56, 'Y': 57, 
    'Z': 58, '-': 59,'0': 60, '1': 61, '2': 62, '3': 63, 
    '4': 64, '5': 65, '6': 66, '7': 67, '8': 68, '9': 69
    }
    p = 7507 

    def encrypt(self, string) -> str:
        result = ''
        pk = 0
        for k in range(0, len(string)):
            pk += 2
            if pk+17 > 104:
                pk = 1
            i = string[k]
            x = self.char_to_int[i]
            to_send = x + self.p*3006*((pk+17)**5)
            result = result + str(to_send) + '|'
        return result