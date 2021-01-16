from random import randint

class Card():
    def __init__(self, inputfile = 'inputPhase2.txt'):
        self.infile = open(inputfile,'r')

    def __del__(self):
        self.infile.close()

    def read(self):
        temp = self.infile.readline()
        return temp if temp!='' else None

class LinePrinter():
    def __init__(self, outputfile = 'outputPhase2.txt'):
        self.outfile = open(outputfile, 'w')

    def __del__(self):
        self.outfile.close()

    def write(self, line = ''):
        self.outfile.write(line + '\n')

    def jobend(self, cpu, pcb):
        outLine = "Process" + "(" + str(pcb.jobID) + ")" + " Terminated: "
        outLine +="Time Taken -> " + str(pcb.TTC) + "/" + str(pcb.TTL) + " "
        outLine +="Lines Printed -> " + str(pcb.TLC) + "/" + str(pcb.TLL) + "\n"
        outLine +="IR : " + str(cpu.IR) + ", IC : " + str(cpu.IC) + ", R : " + str(cpu.R) + "\n"
        self.outfile.write(outLine)
        self.outfile.write('\n\n')

class PCB():
    def __init__(self, _jobID, _TTL, _TLL):
        self.jobID = int("".join(_jobID))
        self.TTL = int("".join(_TTL))
        self.TLL = int("".join(_TLL))
        self.TTC = 0
        self.TLC = 0

class Memory():
    def __init__(self):
        self.mainMem = []
        self.pageNo = None
        self.wordNum = 0
        self.offset = 0
        for _ in range(300):
            self.mainMem.append([None, None, None, None])

    def setABlock(self, pte):
        self.pageNo = randint(0, 29)*10
        while self.mainMem[self.pageNo][0]!=None:
            self.pageNo = randint(0, 29)*10
        ttp = str(self.pageNo//10).rjust(4)
        self.mainMem[pte][:] = list(ttp)

    def printMem(self):
        tp = False
        for i in range(300):
            if self.mainMem[i][0]==None:
                tp=True
            else:
                if tp:
                    print(".")
                    print(".")
                    print(".")
                tp = False
                print(i, self.mainMem[i])
        print()
        print()

    def writeToMem(self, data):
        self.wordNum = 0
        self.offset = 0
        for i in data:
            self.mainMem[self.pageNo + self.wordNum][self.offset] = i
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
        self.PI = 0
        self.TI = 0
        self.IR = [None,None,None,None]
        self.R = [None,None,None,None]
        self.PTR = None
        self.IC = None
        self.C = False
        self.runLoop = True

    def getBlock(self, va):
        return (self.PTR + (va//10))

    def vaToRa(self, va, memory):
        ra = int("".join(memory.mainMem[self.getBlock(va)]).strip())*10 + (va%10)
        return ra

    def isValid(self, va, memory):
        if memory.mainMem[self.getBlock(va)][0]==None:
            return False
        return True

    def executeProg(self, memory, card, linep, pcb, mos):
        self.IC = 00
        self.SI = 0
        while self.runLoop:
            realAdd = self.vaToRa(self.IC, memory)
            self.IR[:] = memory.mainMem[realAdd][:]
            self.IC+=1
            self.SI = 0
            self.TI = 0
            self.PI = 0
            pcb.TTC+=1
            if pcb.TTC > pcb.TTL:
                self.TI = 2
            if self.IR[0]=="H":
                self.SI = 3
                self.masterMode(card, memory, linep, pcb, mos)
            elif self.IR[:2]==["G", "D"]:
                self.SI = 1
                pcb.TTC+=1
                if pcb.TTC > pcb.TTL:
                    self.TI = 2
                if not "".join(self.IR[2:]).strip().isnumeric():
                    self.PI = 2
                if memory.mainMem[self.getBlock(int("".join(self.IR[2:])))][0]==None:
                    memory.setABlock(self.PTR + int("".join(self.IR[2:]))//10)
                memory.setABlock(self.PTR + int("".join(self.IR[2:]))//10)
                realAdd = self.vaToRa(int("".join(self.IR[2:])), memory)
                self.masterMode(card, memory, linep, pcb, mos)
            elif self.IR[:2]==["P", "D"]:
                self.SI = 2
                pcb.TLC+=1
                if not "".join(self.IR[2:]).strip().isnumeric():
                    self.PI = 2
                self.masterMode(card, memory, linep, pcb, mos)
            elif self.IR[:2]==["L", "R"]:
                if not "".join(self.IR[2:]).strip().isnumeric():
                    self.PI = 2
                elif not self.isValid(int("".join(self.IR[2:]).strip()), memory):
                    self.PI = 3
                if self.TI!=0 or self.PI!=0:
                    self.masterMode(card, memory, linep, pcb, mos)
                else:
                    realAdd = self.vaToRa(int("".join(self.IR[2:])), memory)
                    self.R[:] = memory.mainMem[realAdd][:]
            elif self.IR[:2]==["S", "R"]:
                pcb.TTC+=1
                if pcb.TTC > pcb.TTL:
                    self.TI = 2
                if not "".join(self.IR[2:]).strip().isnumeric():
                    self.PI = 2
                if self.TI!=0 or self.PI!=0:
                    self.masterMode(card, memory, linep, pcb, mos)
                else:
                    if memory.mainMem[self.getBlock(int("".join(self.IR[2:])))][0]==None:
                        memory.setABlock(self.PTR + int("".join(self.IR[2:]))//10)
                    realAdd = self.vaToRa(int("".join(self.IR[2:])), memory)
                    memory.mainMem[realAdd][:] = self.R[:]
            elif self.IR[:2]==["C", "R"]:
                if not "".join(self.IR[2:]).strip().isnumeric():
                    self.PI = 2
                if self.TI!=0 or self.PI!=0:
                    self.masterMode(card, memory, linep, pcb, mos)
                else:
                    realAdd = self.vaToRa(int("".join(self.IR[2:])), memory)
                    if self.R[:] == memory.mainMem[realAdd][:]:
                        self.C = True
                    else:
                        self.C = False
            elif self.IR[:2]==["B", "T"]:
                if not "".join(self.IR[2:]).strip().isnumeric():
                    self.PI = 2
                if self.TI!=0 or self.PI!=0:
                    self.masterMode(card, memory, linep, pcb, mos)
                else:
                    if self.C:
                        self.IC = int("".join(self.IR[2:]))
            else:
                self.PI = 1
                self.masterMode(card, memory, linep, pcb, mos)

    def masterMode(self, card, memory, linep, pcb, mos):
        if self.TI==0 and self.SI==1:
            realAdd = self.vaToRa(int("".join(self.IR[2:])), memory)
            data = card.read()
            if data[0]=="$":
                outputLine = "EM(1) : Out of Data"
                linep.write(outputLine)
                linep.jobend(self, pcb)
                self.runLoop = False
                mos.terJob = True
                return
            wordOffSet = 0
            offset = 0
            for i in data[:-1]:
                memory.mainMem[realAdd + wordOffSet][offset] = i
                offset+=1
                if offset==4: wordOffSet+=1
                offset%=4
            return
        elif self.TI==0 and self.SI==2:
            if pcb.TLC > pcb.TLL:
                outputLine = "EM(2) : Line Limit Exceeded"
                linep.write(outputLine)
                linep.jobend(self, pcb)
                self.runLoop = False
                return
            realAdd = self.vaToRa(int("".join(self.IR[2:])), memory)
            outputLine = ""
            wordOffSet = 0
            offset = 0
            for i in range(40):
                if memory.mainMem[realAdd + wordOffSet][offset]==None:
                    break
                outputLine += memory.mainMem[realAdd + wordOffSet][offset]
                offset+=1
                if offset==4: wordOffSet+=1
                offset%=4
            print("Writing Output Line : ", outputLine)
            linep.write(outputLine)
            return
        elif self.TI==0 and self.SI==3:
            outputLine = "EM(0) : No Error"
            linep.write(outputLine)
            linep.jobend(self, pcb)
            self.runLoop = False
            return
        elif self.TI==2 and self.SI==1:
            outputLine = "EM(3) : Time Limit Exceeded"
            linep.write(outputLine)
            self.runLoop = False
            linep.jobend(self, pcb)
            return
        elif self.TI==2 and self.SI==2:
            if pcb.TLC > pcb.TLL:
                outputLine = "EM(2) : Line Limit Exceeded"
                linep.write(outputLine)
                linep.jobend(self, pcb)
                self.runLoop = False
                return
            realAdd = self.vaToRa(int("".join(self.IR[2:])), memory)
            outputLine = ""
            wordOffSet = 0
            offset = 0
            for i in range(40):
                if memory.mainMem[realAdd + wordOffSet][offset]==None:
                    break
                outputLine += memory.mainMem[realAdd + wordOffSet][offset]
                offset+=1
                if offset==4: wordOffSet+=1
                offset%=4
            print("Writing Output Line : ", outputLine)
            linep.write(outputLine)
            outputLine = "EM(3) : Time Limit Exceeded"
            linep.write(outputLine)
            linep.jobend(self, pcb)
            self.runLoop = False
            return
        elif self.TI==2 and self.SI==3:
            outputLine = "EM(0) : No Error"
            linep.write(outputLine)
            linep.jobend(self, pcb)
            self.runLoop = False
            return

        if self.TI==0 and self.PI==1:
            outputLine = "EM(4) : Operation Code Error"
            linep.write(outputLine)
            linep.jobend(self, pcb)
            self.runLoop = False
        elif self.TI==0 and self.PI==2:
            outputLine = "EM(5) : Operand Error"
            linep.write(outputLine)
            linep.jobend(self, pcb)
            self.runLoop = False
        elif self.TI==0 and self.PI==3:
            outputLine = "EM(6) : Invalid Page Fault"
            linep.write(outputLine)
            linep.jobend(self, pcb)
            self.runLoop = False
        elif self.TI==2 and self.PI==0:
            outputLine = "EM(3) : Time Limit Exceeded"
            linep.write(outputLine)
            linep.jobend(self, pcb)
            self.runLoop = False
        elif self.TI==2 and self.PI==1:
            outputLine = "EM(3) : Time Limit Exceeded"
            linep.write(outputLine)
            outputLine = "EM(4) : Operation Code Error"
            linep.write(outputLine)
            linep.jobend(self, pcb)
            self.runLoop = False
        elif self.TI==2 and self.PI==2:
            outputLine = "EM(3) : Time Limit Exceeded"
            linep.write(outputLine)
            outputLine = "EM(5) : Operand Error"
            linep.write(outputLine)
            linep.jobend(self, pcb)
            self.runLoop = False
        elif self.TI==2 and self.PI==3:
            outputLine = "EM(3) : Time Limit Exceeded"
            linep.write(outputLine)
            linep.jobend(self, pcb)
            self.runLoop = False

    def curr_ir(self):
        return self.IR[0] + self.IR[1] + self.IR[2] + self.IR[3]

    def curr_reg(self):
        return self.R[0] + self.R[1] + self.R[2] + self.R[3]

class MOS():
    def __init__(self):
        self.card = Card()
        self.linep = LinePrinter()
        self.cpu = None
        self.pcb = None
        self.memory = None
        self.terJob = False

    def load(self):
        InitJobData = None
        amjActive = False
        noOfPages = 0
        while True:
            jobData = self.card.read()
            if jobData==None:
                break
            if jobData[0]=="$":
                if jobData[:4]=="$AMJ":
                    InitJobData = jobData[:-1]
                    noOfPages = 0
                    amjActive = True
                    self.pcb = PCB(InitJobData[4:8], InitJobData[8:12], InitJobData[12:16])
                    self.cpu = Cpu()
                    self.memory = Memory()
                    self.cpu.PTR = randint(0, 29)*10
                elif jobData[:4]=="$DTA":
                    amjActive = False
                    self.cpu.executeProg(self.memory, self.card, self.linep, self.pcb, self)
                    if self.terJob:
                        amjActive = False
                        print(InitJobData, " - Done")
                        print()
                    self.terJob = False
                elif jobData[:4]=="$END":
                    amjActive = False
                    print(InitJobData, " - Done")
                    print()
                else:
                    #Error
                    pass
            elif amjActive:
                self.memory.mainMem[self.cpu.PTR + noOfPages] = [" ", " ", " ", " "]
                self.memory.setABlock(self.cpu.PTR + noOfPages)
                noOfPages+=1
                self.memory.writeToMem(jobData[:-1])
            else:
                #Error
                pass
	
mos=MOS()
mos.load()