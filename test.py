from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import MD5
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
import json
import sys

json_file = "hash.json"
github = "https://github.com/MicheleViscione/Pyxercise"

def gen_key(sol, dim=32, sol_md5=None):
    sol = str(sol)
    if not sol_md5:
        sol_md5 = MD5.new(sol.encode()).digest()
    l = len(sol)
    if l == 0:
        return None
    if 2*l < dim:
        # the grather dim/l is the more complex is the filling of the missing bytes
        # so for dim closer to l we have sol closer to the original key
        rep = int(dim / l)
        temp = sol.encode()
        for k in range(rep):
            n = int.from_bytes(temp, 'big') + int.from_bytes(temp, 'little') << k
            n = n.to_bytes((n.bit_length() + 7) // 8, 'big') or b'\0'
            sol += str(n)
        l = len(sol)
    sol = pad(sol.encode(), dim)
    blocks = [ sol[i:i+dim] for i in range(0,l,dim)]
    key = b''
    prev = sol_md5
    for block in blocks:
        key = (int.from_bytes(key, 'big') + int.from_bytes(prev, 'little'))
        key = key.to_bytes((key.bit_length() + 7) // 8, 'big') or b'\0'
        key = int.from_bytes(key[:dim], byteorder="big" ) ^ int.from_bytes(block, byteorder="big")
        key = key.to_bytes((key.bit_length() + 7) // 8, 'big') or b'\0'
        prev = block
    return key

def decrypt(filename, encfile, sol):
    with open(encfile, 'r') as file:
        enc = file.read()
    ct = b64decode(enc)
    key = gen_key(sol,16)
    iv = gen_key("che iv metto?",16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    with open(filename, 'w') as file:
        file.write(pt.decode())
    return pt

def generate(num, sol):
    file_enc = f"Exercises/exercise{num}.enc"
    file_dec = f"Exercises/exercise{num}.py"
    decrypt(file_dec, file_enc, sol)



if __name__ == "__main__":

    usage = "\nUsage:\n\n   -start             generates the first\n\n   -n  solution       if solution of exercise n is correct generates the next exercise\n"

    if len(sys.argv) < 2:
        print(usage)
        exit()
    
    if len(sys.argv) == 2 and "-start" in sys.argv:
        to_dec = 0
        print("Generating Exercise[1] ...")
        generate(1, "start")
        print("Done")
        exit()
    elif len(sys.argv) == 3 and sys.argv[1].startswith("-"):
        try:
            to_dec =  int(sys.argv[1][1:])
            sol = sys.argv[2] 
        except:
            print("Error: Wrong Input flags")
            print(usage)
            exit()
    else:
        print(usage)
        exit()

    # print(to_dec)
    # print(sol)
  
    with open(json_file, 'r') as jfile:
        hash = json.load(jfile)

    sol_h = MD5.new(sol.encode()).hexdigest()

    try:
        if hash[str(to_dec)] == sol_h:
            print("Solution is correct!")
            if str(to_dec + 1) in hash:
                print(f"Generating Exercise[{to_dec +1}] ...")
                generate(to_dec +1, sol)
                print("Done")
            else:
                print(f"\nExercises completed  ,(^.^)/\n\ncheck on github for updates:  {github}\n")
        else:
            print("Wrong solution, keep tryin'!")
    except KeyError:
        print(f"Exercise[{to_dec}] not defined")


    










