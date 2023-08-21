# Ridwan Alrefai - November 2022
# University of Illinois Chicago - Fall 2022
# MIPS Simulator with full Cache functionality. Supports most instructions from # MIPS architecture including jump and branch. Multiple modes for register 
# display, instruction run and cache design.
from tabulate import tabulate
import os
import CacheClass
#
#
# 

# Used to clear output for neat formatting 
def clear():
  os.system('clear')

# DEFINITIONS OF ALL INSTRUCTIONS AND THEIR BINARY OP AND THEIR PROPERTIES:
# tuple structure: name | op_binary | regRead | regWrite | memRead | memWrite | x-type | operator
# op_type: 1 for I-type, 2 for R-type, 3 for j-type
INSTRUCTIONS = (("add", '100000', 1, 1, 0, 0, 2, "+"), 
                ("addi", '001000', 1, 1, 0, 0, 1, "+"),
                ("sub", "100010", 1, 1, 0, 0, 2, "-"),
                ("sw", '101011', 1, 0, 0, 1, 1, "store"), 
                ("lw", '100011', 1, 1, 1, 0, 1, "load"),
                ("slt", '101010', 1, 1, 0, 0, 2, "<"), 
                ("beq", '000100', 1, 0, 0, 0, 1, "="), 
                ("bne", '000101', 1, 0, 0, 0, 1, "!="), 
                ("andi", '001100', 1, 1, 0, 0, 1, "and"),
                ("j", '000010', 0, 0, 0, 0, 3, "jump"),
                ("srl", '000010', 1, 1, 0, 0, 2, "shift"),
                ("xor", "100110", 1, 1, 0, 0, 2, "x"))

# SECTION |MEMORY AND REGISTER|

# REGISTER LIST -- STRUCTURE: NAME | NUMBER | VALUE
register_list = [["$zero", 0, 0], 
                 ["$at", 1, 0], 
                 ["$v0", 2, 0], 
                 ["$v1", 3, 0], 
                 ["$a0", 4, 0],
                 ["$a2", 6, 0], 
                 ["$a3", 7, 0], 
                 ["$t0", 8, 0], 
                 ["$t1", 9, 0], 
                 ["$t2", 10, 0], 
                 ["$t3", 11, 0], 
                 ["$t4", 12, 0], 
                 ["$t5", 13, 0], 
                 ["$t6", 14, 0], 
                 ["$t7", 15, 0], 
                 ["$s0", 16, 0], 
                 ["$s1", 17, 0], 
                 ["$s2", 18, 0], 
                 ["$s3", 19, 0], 
                 ["$s4", 20, 0], 
                 ["$s5", 21, 0], 
                 ["$s6", 22, 0], 
                 ["$s7", 23, 0], 
                 ["$t8", 24, 0], 
                 ["$t9", 25, 0],
                 ["$k0", 26, 0],
                 ["$k1", 27, 0],
                 ["$gp", 28, 6144], # constant values as seen in MARS
                 ["$sp", 29, 16380],
                 ["$fp", 30, 0], 
                 ["$ra", 31, 0]]


# MEMORY ARRAY (DICTIONARY)
data_memory = {}
min = "0x00000000"
max = "0x000021FF"
addr = range(int(min, 16), int(max, 16), 4) 
for i in addr:
  data_memory[hex(i)] = 0

# Dictionary used to display memory.
# Only displays memory addresses used in store
# and load for better usability
accesed_mem = {}


# HEX LIBRARY
# Will be populated after loading code
# Used to display hex code even after conversions
hexInstr = []
# Cache Instanciation
ways = 0
sets = 0
size = 0
config = input("Please select Cache configuration \n\n 1: 1-way 8-set, 64 byte blks \n 2: 1-way 4-set, 32 byte blks \n 3: 4-way FA 32 byte blks \n 4: 4-way 2-set, 64 byte blks")
if config == "1":
  cache = CacheClass.Cache(1, 8, 64)
elif config == "2":
  cache = CacheClass.Cache(1, 4, 32)
elif config == "3":
  cache = CacheClass.Cache(4, 1, 32)
elif config == "4":
  cache = CacheClass.Cache(4, 2, 64)

cache.clearLog()
clear()



#------------------------------------<<FUNCTION SECTION>>-------------------------------------------#
#----------------Functions for program reading file and parsing hex conversion----------------------#
#-----------Functions for executing instructions, and reading and writing regs and mem--------------#

# ALU Operations
# Called if instructions require register read or write
# Returns value of destination register
def ALU(im1, im2, im3, op):
  if op == "+":
    im1 = im2 + im3
  elif op == "<":
    im1 = 0
    if im2 < im3:
      im1 = 1
  elif op == "shift":
    im1 = im2 >> im3
  elif op == "and":
    im1 = im2 & im3
  elif op == "-":
    im1 = im2 - im3
  elif op == "x":
    b1 = bin(im2)
    b2 = bin(im3)
    b1 = b1.lstrip('-0b')
    b2 = b2.lstrip('-0b')
    b1 = b1.zfill(32)
    b2 = b2.zfill(32)
    
    newBin = ''
    i = 0
    j = 0
    while i < len(b1) and j < len(b2):
      if b1[i] == '1' and b2[j] == '0':
        newBin += '1'
      elif b1[i] == '0' and b2[j] == '1':
        newBin += '1'
      else:
        newBin += '0'
      i += 1
      j += 1
      
    if im2 < 0 or im3 < 0:
      im1 = 0 - int(newBin,2)
    else:
      im1 = int(newBin,2)
  return im1


# Branch Operations
# Called for all i-type instructions
# Only modifies PC if instruction is beq or bne
# Returns true if insruction is a branch
def branch(op, im1, im2, imm, PC):
  new_PC = PC + 4 + (imm << 2)
  if op == "beq":
    if im1 == im2:
      PC = new_PC
      return PC, True
  elif op == "bne":
    if im1 != im2:
      PC = new_PC
      return PC, True
  
  return PC + 4, False

# Load and Store Operations
# Called in i-type instructions
# Modifies or loads data from data memory
# if op is lw or sw
def loadStore(op, base, rt, offset, PC, reg):
  addr = hex(base + offset)
  PC += 4
  
  if op == "sw":
    cache.displayCache(addr)
    if cache.fetch(addr):
      print("Hit!")
    else:
      print("Miss! Storing address")
      
    data_memory[addr] = rt
    accesed_mem[addr] = rt
    return PC, True

  elif op == "lw":
    cache.displayCache(addr)
    if cache.fetch(addr):
      print("Hit!")
    else:
      print("Miss! Storing address")
    reg[2] = data_memory[addr]
    return PC, True
  
  
  return PC, False
  
  
  
# Main execution function of an instruction
# uses many helper functions for each
# insruction type, operation, and branch
# return true if instruction is executed
# and returns PC value
def Execute(instr, PC):
  r = instr.replace(",", "")
  s = r.split(" ")
  tuple = ()
  op = s[0]
  for i in INSTRUCTIONS: # Fetch instruction tuple
    if i[0] == op:
      tuple = i
  if tuple[6] == 1:
    isDone, PC = executeiType(s, tuple, PC)
  elif tuple[6] == 2:
    isDone, PC = executerType(s, tuple, PC)
  else:
    isDone, PC = executejType(s, tuple, PC)

  return isDone, PC

# Executes an r-type instruction when called
def executerType(s, tuple, PC):
  rDest = registerNumber(s[1])
  reg2 = registerNumber(s[2])
  digit = s[3].isdigit()
  if not digit:
    reg3 = registerNumber(s[3])
    r3 = []
    for r in register_list:
      if r[1] == reg3:
        r3 = r
    rm = r3[2]
  else:
    rm = int(s[3])
  r1 = []
  r2 = []
  for r in register_list:
    if r[1] == rDest:
      r1 = r
    if r[1] == reg2:
      r2 = r
  if r1 == [] or r2 == []:
    return False
  r1[2] = ALU(r1[2], r2[2], rm, tuple[7])
  PC += 4
  return True, PC

# Executes and i-type instruction if called
# Can also execute a branch instruction
def executeiType(s, tuple, PC):
  rDest = registerNumber(s[1])
  reg2 = registerNumber(s[2])
  imm = int(s[3])
  r1 = []
  r2 = []
  for r in register_list:
    if r[1] == rDest:
      r1 = r
    if r[1] == reg2:
      r2 = r
  if r1 == [] or r2 == []:
    return False
  new_PC, isMem = loadStore(tuple[0], r2[2], r1[2], imm, PC, r1)
  
  new_PC, isBranch = branch(tuple[0], r1[2], r2[2], imm, PC)
  PC = new_PC
  if not isBranch or not isMem:
    r1[2] = ALU(r1[2], r2[2], imm, tuple[7])
  
  return True, PC
  
# Executes a jump instruction
# Modifies PC accordingly and returns
def executejType(s, tuple, PC):
  jump = int(s[1]) << 2
  jb = bin(jump)
  jb = jb.lstrip('-0b')
  jb = jb.zfill(26)
  pb = bin(int(PC))
  pb = pb.lstrip('-0b')
  pb = pb.zfill(32)
  new_PC = pb[0:6] + jb
  new_PCint = int(new_PC, 2)

  return True, new_PCint
  
  
# Used for all immutables
# if a number is negative,
# this function returns the
# two's complement
def twosComp(immutable):
  immutable = immutable.lstrip('-0b')
  immutable = immutable.zfill(16)
  newBin = ''
  for i in range(16):
    if immutable[i] == '0':
      newBin += '1'
    else:
      newBin += '0'

    b = int(newBin, 2)
    result = b + 1
    result = bin(result)
    
  return result

# Used for formatting instruction registers
def register(b):
  register = "$" + str(int(b, 2))

  return register

# Retrieves the number of the input register
def registerNumber(str):
  s = str.replace("$", "")
    
  return int(s)
  
      
# |FILE READING|
def loadCode(filename):
  f = open(filename, "r")
  codelines = f.readlines()
  code = [c for c in codelines if c[0] != "#"] # removes any comments from reading
  f.close()
  for i in range(len(code)):
    code[i] = code[i].replace("\n", "")
    hexInstr.append(code[i])
  instr_binary = parseHex(code)
  instr_array = parseBinary(instr_binary)
  
  return instr_array
  

# |PARSING INTO BINARY FORM|
def parseHex(code):
  instr_binary = []
  for line in code:
    b = bin(int(line, 16))
    b = b.lstrip('-0b')
    b = b.zfill(32)
    instr_binary.append(b)

  return instr_binary

# |PARSING BINARY INTO RESPECTIVE INSTRUCTION FORM|
def parseBinary(array):
  instr = []
  for b in array:
    if b[0:6] == "000000":
      instr.append(rtype(b))
    elif b[0:6] == "000010":
      instr.append(jtype(b))
    else:
      instr.append(itype(b))

  return instr

  
# |Definitions and orginazation of instruction types|
# used in main to display instructions
def rtype(b):
  instr = ""
  for i in INSTRUCTIONS:
    if i[1] == b[-6:] and i[6] == 2:
      instr += i[0]
  if b[6:11] == "00000" and b[21:26] != "00000":
    instr = instr + " " + register(b[16:21]) + ", " + register(b[11:16]) + ", " + str(int(b[21:26]))
  else:
    instr = instr + " " + register(b[16:21]) + ", " + register(b[6:11]) + ", " + register(b[11:16])

  return instr

def itype(b):
  if b[16] == '1':
    immutable = -abs(int(twosComp(b[-16:]), 2))
  else:
    immutable = int(b[-16:], 2)
  instr = ""
  for i in INSTRUCTIONS:
    if b[0:6] == i[1] and i[6] == 1:
      op = i[0]

  instr = op + " " + register(b[11:16]) + ", " + register(b[6:11]) + ", " + str(immutable)

  return instr

def jtype(b):
  instr = "j" + " " + str(int(b[6:], 2))

  return instr

  
#-------------------------------<<MAIN SECTION>>--------------------------#
#-----------------Register, Memory Display, and UI Under This Line---------------#


# Displays registers using tabulate library
def displayRegs():
  data = register_list
  print(tabulate(data, headers=["Name", "Number", "Value"], tablefmt="outline"))
  
    
def displayMem():
  data = [(k, v) for k,v in accesed_mem.items()]
  print(tabulate(data, headers = ["address", "data"], tablefmt="grid"))


  
  
# Start 
# PC VALUE
PC = 0
a = loadCode("InstructionHex.txt")
instr_count = 0  # Keeps track of number of instructions in a program

# PC index dictionary to hold each pc per instruction to easily jump to a pc
# by loop index
pc_index = {}
# Filling dictionary
for x in range(len(a)):
  pc_index[PC] = x
  PC += 4

# restart PC for main use
PC = 0
i = 0

inp = input("type s for next instrution or n to run the rest of instructions, or q to quit")
while i < len(a):
  if inp == 's' or inp == 'n':
    current_pc = PC
    if inp == 's':
      clear()
    executed, next_pc = Execute(a[i], PC)
    if executed:
        instr_count += 1
        if inp == 's':
          print("Hex:", hexInstr[i])
          print("Instruction:", a[i])
          print("PC:", hex(current_pc))
          print("next PC:", hex(next_pc))
          print("instruction #:", instr_count)
          displayRegs()
          print("\n\n")
        PC = next_pc
        if next_pc in pc_index:
          i = pc_index[next_pc]
        elif next_pc not in pc_index:
          break
        else:
          i += 1
        if inp == 's':
          inp = input("type s for next instrution or n to run the rest of instructions")
          print("\n\n")
    else:
      print("Error: cannot compile code at PC: ", current_pc)
      break
  elif inp == 'q':
    break
  else:
    print("Error, try again")
    inp = input("type s for next instrution or n to run the rest of instructions")

clear()

inp = input("Select r for register and memory content\nSelect c for cache summary and stats\n")

if inp == 'r':
  displayRegs()
  print("Instruction count:", instr_count, '\n')
  print("Showing Accessed and stored memory...")
  displayMem()

elif inp == 'c':
  cache.getStats()
  print("Detailed Log information included in CacheLog.txt")


