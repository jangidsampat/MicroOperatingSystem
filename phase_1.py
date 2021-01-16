class Card():
    def __init__(self, inputfile = 'inputPhase1.txt'):
        self.infile = open(inputfile,'r')

    def __del__(self):
        self.infile.close()

    def read(self):
        temp = self.infile.readline()
        return temp if temp!='' else None

class LinePrinter():
    def __init__(self, outputfile = 'outputPhase1.txt'):
        self.outfile = open(outputfile, 'w')

    def __del__(self):
        self.outfile.close()

    def write(self, line = ''):
        self.outfile.write(line + '\n')

    def jobend(self):
        self.outfile.write('\n\n')

class Memory():
    def __init__(self):
        self.mainMem = []
        self.wordNum = 0
        self.offset = 0
        for _ in range(100):
            self.mainMem.append([None, None, None, None])
    
    def writeToMem(self, data):
        for i in data:
            self.mainMem[self.wordNum][self.offset] = i
            if i=="H":
                self.offset = 0
                self.wordNum+=1
                continue
            self.offset+=1
            if self.offset==4: self.wordNum+=1
            self.offset%=4

class Cpu():
    def __init__(self):
        self.SI = 3
        self.IR = [None,None,None,None]
        self.R = [None,None,None,None]
        self.IC = None
        self.C = False

    def executeProg(self, memory, card, linep):
        self.IC = 00
        self.SI = 0
        runLoop = True
        while runLoop:
            self.IR[:] = memory.mainMem[self.IC][:]
            self.IC+=1
            if self.IR[0]=="H":
                self.SI = 3
                self.masterMode(card, memory, linep)
                runLoop = False
            elif self.IR[:2]==["G", "D"]:
                self.SI = 1
                self.masterMode(card, memory, linep)
                self.SI = 0
            elif self.IR[:2]==["P", "D"]:
                self.SI = 2
                self.masterMode(card, memory, linep)
                self.SI = 0
            elif self.IR[:2]==["L", "R"]:
                self.R[:] = memory.mainMem[int("".join(self.IR[2:]))][:]
            elif self.IR[:2]==["S", "R"]:
                memory.mainMem[int("".join(self.IR[2:]))][:] = self.R[:]
            elif self.IR[:2]==["C", "R"]:
                if self.R[:] == memory.mainMem[int("".join(self.IR[2:]))][:]:
                    self.C = True
                else:
                    self.C = False
            elif self.IR[:2]==["B", "T"]:
                if self.C:
                    self.IC = int("".join(self.IR[2:]))

    def masterMode(self, card, memory, linep):
        if self.SI==1:
            data = card.read()
            blockNum = int(self.IR[2])
            wordOffSet = 0
            offset = 0
            for i in data[:-1]:
                memory.mainMem[blockNum*10 + wordOffSet][offset] = i
                offset+=1
                if offset==4: wordOffSet+=1
                offset%=4
        elif self.SI==2:
            outputLine = ""
            blockNum = int(self.IR[2])
            wordOffSet = 0
            offset = 0
            for i in range(40):
                if memory.mainMem[blockNum*10 + wordOffSet][offset]==None:
                    break
                outputLine += memory.mainMem[blockNum*10 + wordOffSet][offset]
                offset+=1
                if offset==4: wordOffSet+=1
                offset%=4
            print("Writing Output Line : ", outputLine)
            linep.write(outputLine)
        elif self.SI==3:
            linep.jobend()

    def curr_ir(self):
        return self.IR[0] + self.IR[1] + self.IR[2] + self.IR[3]

    def curr_reg(self):
        return self.R[0] + self.R[1] + self.R[2] + self.R[3]

class MOS():
    def __init__(self):
        self.card = Card()
        self.linep = LinePrinter()
        self.cpu = None
        self.memory = None

    def load(self):
        InitJobData = None
        amjActive = False
        while True:
            jobData = self.card.read()
            if jobData==None:
                break
            if jobData[0]=="$":
                if jobData[:4]=="$AMJ":
                    InitJobData = jobData
                    amjActive = True
                    self.cpu = Cpu()
                    self.memory = Memory()
                if jobData[:4]=="$DTA":
                    amjActive = False
                    self.cpu.executeProg(self.memory, self.card, self.linep)
                if jobData[:4]=="$END":
                    amjActive = False
                    print(InitJobData[:-1], " - Done")
                    print()
            elif amjActive:
                self.memory.writeToMem(jobData[:-1])
	
mos=MOS()
mos.load()