import angr

class ReturnZero(angr.SimProcedure):
    def run(self):
        return 0

class ReturnOne(angr.SimProcedure):
    def run(self):
        return 1

class DoNothing(angr.SimProcedure):
    def run(self):
        return
    
class DoErrored(angr.SimProcedure):
    def run(self):
        angr.SimError("Forced error by DoErrored hook")