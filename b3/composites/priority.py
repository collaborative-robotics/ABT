import b3

__all__ = ['Priority']

class Priority(b3.Composite):
    def __init__(self, children=None):
        super(Priority, self).__init__(children)
        self.Name = '*Priority*'

    def tick(self, tick):
        self.Cost = 0
        for node in self.children:
          status = node._execute(tick)
          #Add in cost of selected leaf (requires zero cost for Seq node)
          self.Cost += node.Cost
          if status != b3.FAILURE:
                return status

        return b3.FAILURE
    def compositeid(self): # Identifies the Succss and Failure of every composite node
        print "Priority Hit"
        if self.ifroot:
            self.suc = self.children_size
            self.fail = self.children_size+1
        for current,child in enumerate(self.children):
            if child.category == b3.COMPOSITE:
                child.suc = self.suc
                child.fail =  child.children_start+child.children_size
                if current == len(self.children)-1:
                    child.fail = self.fail
                child.compositeid()
            else:
                child.suc = self.suc
                child.fail =  child.description+1
                if current == len(self.children)-1:
                    child.fail = self.fail
                print "For Child",child.description,":::::::Success :", child.suc," Failiure: ", child.fail
        print "Success :", self.suc," Failiure: ", self.fail


    # def HMM_build(self,matrix,i,js,jf,size):
    #     for current,child in enumerate(self.children):
    #         if isinstance(child,b3.Sequence):
    #             jf = self.children_start + self.children_size
    #             child.HMM_build(matrix,i,js,jf,size)
    #         else:
    #             jf = i+1
    #             child.HMM_build(matrix,i,js,jf,size)
    #             i+=1
