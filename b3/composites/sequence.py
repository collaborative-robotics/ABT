import b3

__all__ = ['Sequence']

class Sequence(b3.Composite):

    def __init__(self, children=None):
        super(Sequence, self).__init__(children)
        self.Name = '*Sequence*'

    def tick(self, tick):
        tmpCost = 0
        for node in self.children:
            status = node._execute(tick)
            #Add in cost of selected leaf (requires zero cost for Seq node)
            #print node.Name + ':  Cost: '+str(node.Cost)
            tmpCost += node.Cost
            if status != b3.SUCCESS:
                self.Cost = tmpCost
                return status
        self.Cost = tmpCost
        return b3.SUCCESS
    def compositeid(self): # Identifies the Succss and Failure of every composite node
        print "Sequence Hit"
        if self.ifroot:
            self.suc = self.children_size
            self.fail = self.children_size+1
        for current,child in enumerate(self.children):
            if child.category == b3.COMPOSITE:
                child.suc =  child.children_start+child.children_size
                child.fail = self.fail
                if current == len(self.children)-1:
                    #print "HITttto"
                    child.suc = self.suc
                child.compositeid()
            if child.category == b3.ACTION:
                child.suc =  child.description+1
                child.fail = self.fail
                if current == len(self.children)-1:
                    #print "HITttto"
                    child.suc = self.suc
                print "For Child",child.description,":::::::Success :", child.suc," Failiure: ", child.fail
        print "Success :", self.suc," Failiure: ", self.fail






    # def HMM_build(self,matrix,i,js,jf,size):
    #     for current,child in enumerate(self.children):
    #         if isinstance(child,b3.Sequence):
    #             child.HMM_build(matrix,i,js,jf,size)
