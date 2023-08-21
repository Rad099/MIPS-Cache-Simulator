import math
import logging

class Cache:

  logging.basicConfig(filename="CacheLog.txt", level=logging.INFO,
    format="%(message)s")
  
  def __init__(self, ways, sets, blkSize):
    self.ways = ways
    self.sets = sets
    self.blkSize = blkSize
    #
    self.offsetBits = int(math.log(self.blkSize, 2))
    self.setBits = int(math.log(self.sets, 2))
    
    # Main content list storing tags. Pre-arranged by setbit and offset # from cache config
    self.contents = [[[] for _ in range(self.ways)] for _ in range(self.sets)]
    
    # Parallel list with contents. Stores the valid bits of each block/set
    self.validSets = [[0 for _ in range(self.ways)] for _ in range(len(self.contents))]
    
    # (Recently Used Tag) a list keeping track of recently used tags. Lowest index is LRU
    self.RUTag = []

    # hit and miss counts
    self.hits = 0
    self.misses = 0
    self.total = 1

  # addressBreakdown Method
  # Crucial method for splicing memory address
  # to return tag, setbits, and offset bits
  # Used in every class method
  def addressBreakDown(self, addr):
    b = bin(int(addr, 16))
    b = b.lstrip('-0b')
    memAddr = b.zfill(32)
    tagBits = 32 - (self.offsetBits + self.setBits)
    tag = memAddr[0: tagBits]
    setBin = memAddr[tagBits: tagBits+self.setBits]
    offset = memAddr[tagBits + self.setBits:]
    if (self.setBits == 0):  # Fully associative Cache if log2 set = 0; no set bits
      offset = memAddr[tagBits:]
      setBin = '0'
      
    return hex(int(tag,2)), setBin, offset

  # addData Method
  # Called by fetch method. Adds tag to appropiate block/set in Content
  # Updates validSet and RUTag to correspond with update
  def addData(self, addr, i):
    tag, set, offset = self.addressBreakDown(addr)
    x = int(set, 2)
    self.contents[x][i] = tag  # assign tag to cache
    self.validSets[x][i] = 1   # Update valid bit to 1
    self.RUTag.append([tag, x])     # add tag to stack for LRU tracking
    self.writeLog(False, i, addr)
  
  
      
  # Fetch Method
  # main method of cache: checks if tag is present in cache
  # fetches the memory with hit or adds data if miss. Uses
  # LRU function to replace already filled blocks.
  # Writes into log for every activity
  # Only method used outside of class
  def fetch(self, addr):
    tag, set, offset = self.addressBreakDown(addr)
    b = bin(int(addr,16))
    b = b.lstrip('-0b')
    b = b.zfill(32)
    hit = False
    addedData = True
    x = int(set,2)
    i = 0
    logging.info(f'access {self.total} \nchecking for mem address {addr} (binary: {b}) in set {int(set,2)}... tag: {tag}, offset: {offset}')
    rTag = []
    while i < len(self.contents[x]):
      if self.validSets[x][i] == 1:
        logging.info(f'block {i}... occupied: tag: {self.contents[x][i]}')
      else:
        logging.info(f'block {i}... empty')
      if tag == self.contents[x][i] and self.validSets[x][i] == 1:
        for y in range(len(self.RUTag)):  # removes the tag then appends to the top
          if self.RUTag[y][0] == tag and self.RUTag[y][1] == x:
              rTag = self.RUTag[y]
        self.RUTag.remove(rTag)
        self.RUTag.append([tag, x])
        hit = True
        self.hits += 1
        self.writeLog(hit, i, addr)
        break
          
      else:
          i += 1

    if hit == False:
          self.misses += 1
          i = 0
          while i < len(self.contents[x]):
            if self.validSets[x][i] == 1:
              i+=1
              addedData = False
              
            elif self.validSets[x][i] == 0:
              self.addData(addr, i)
              addedData = True
              break
              
    if addedData == False:
      self.LRU(addr)

    self.total += 1

    if hit == True:
      return True
    else:
      return False
    

            
  # LRU Method
  # Called when all blocks in a set are full
  # Looks for LRU in the set and replaces with new tag
  # Updates content and tag stack accordingly
  def LRU(self, addr):
    tag, set, offset = self.addressBreakDown(addr)
    LeastTag = 'error'
    logging.info("All blocks occupied. Finding least used block...\n")
    x = int(set, 2)
    if self.setBits == 0:
       for t in range(len(self.contents[0])):
          if self.contents[0][t] == self.RUTag[0][0]:
            LeastTag = self.RUTag[0]
            logging.info(f'LRU: {LeastTag[0]} at block {t}')
            logging.info(f'Replacing with: {tag}')
            self.contents[0][t] = tag
            self.RUTag.remove(LeastTag)
            self.RUTag.append([tag, x])
            self.writeLog(False, t, addr)
            break
            
    else: 
      LRUSet = []
      for i in range(len(self.contents[x])):
        for y in range(len(self.RUTag)):
          if self.contents[x][i] == self.RUTag[y][0] and self.RUTag[y][1] == x:
            LRUSet.append(y)
            
      LRUSet.sort()
      LeastTag = self.RUTag[LRUSet[0]]
      for t in range(len(self.contents[x])):  
        if self.contents[x][t] == LeastTag[0]:
          logging.info(f'LRU: {LeastTag[0]} at block {t}')
          logging.info(f'Replacing with: {tag}')
          self.contents[x][t] = tag
          self.RUTag.remove(LeastTag)
          self.RUTag.append([tag, x])
          self.writeLog(False, t, addr)
          break
        

              
  
  # Method for displaying basic stats of addr being fetched
  # Used outside of class
  def displayCache(self, addr):
    tag, set, offset = self.addressBreakDown(addr)
    x = int(set,2)
    b = bin(int(addr,16))
    b = b.lstrip('-0b')
    b = b.zfill(32)
    print(f'checking for mem address {addr} (binary: {b}) in set {x}... tag: {tag}, offset: {offset}')


    
     
    
    

  # Uses Logging library to write to CacheLog file everytime a fetch is
  # called. 
  def writeLog(self, hit, blk, addr):
    tag, set, offset = self.addressBreakDown(addr)
    x = int(set,2)

    if hit == True:
      logging.info(f'Hit! address found in set {x} block {blk} \n\n')

    else:
      logging.info(f'Miss! storing tag {tag} into set {x} block {blk} \n\n')
     
  def getContents(self):
    return self.contents
    
  def getValidSets(self):
    return self.validSets

  def getTagStack(self):
    return self.RUTag

  # Method for calculating total fetches and hit rate
  def getStats(self):
    total = self.hits + self.misses
    print(f'total fetches: {total}')
    print(f'hits: {self.hits}')
    print(f'misses: {self.misses}')
    hitPercentage = float(self.hits)/float(total) * 100
    hitPercentage = round(hitPercentage)
    print(f'hit percentage: {int(hitPercentage)}%')

  # Method for clearing log file for next program run
  def clearLog(self):
    with open("CacheLog.txt",'r+') as file:
      file.truncate(0)