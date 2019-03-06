import b3

__all__ = ['Composite']


class Composite(b3.BaseNode):
    category = b3.COMPOSITE

    def __init__(self, children=None):
        super(Composite, self).__init__()

        self.children = children or []
        self.children_size = 0
        self.children_start = 0
        self.ifroot = False
    def scan(self, size): # Idenftify the size of the ABT and size of every composite node
        temp = size
        self.children_start = size
        for child in self.children:
            if child.category == b3.ACTION:
                child.description = size
                print "Sequence No.:",child.description
                size+=1
            if child.category == b3.COMPOSITE:

                size = child.scan(size)
        self.children_size = size - temp
        #print "Size of this one is  :", self.children_size
        return size

    def HMM(self,matrix):
        for child in self.children:
            if child.category == b3.ACTION:
                matrix = child.HMM_build(matrix)
            if child.category == b3.COMPOSITE:
                matrix = child.HMM(matrix)
        return matrix
    # def HMM_build(self,matrix,i,js,jf,size):
    #     for current,child in enumerate(self.children):
    #         if child.category == b3.COMPOSITE:
    #             if isinstance(child,b3.Sequence):
    #                 print "Hit Sequence"
    #                 if i+len(self.children) >= size:
    #                     js = i+1
    #                     jf = size + 1
    #                 else:
    #                     js = i + 1
    #                     jf = i + len(self.children)
    #                 matrix,i,js,jf = child.HMM_build(matrix,i,js,jf,size)
    #             if isinstance(child,b3.Priority):
    #                 print "Hit Priority"
    #                 if i+len(self.children) >= size:
    #                     js = size
    #                     jf = i+1
    #                 else:
    #                     js = i + len(self.children)
    #                     jf = i + 1
    #                 matrix,i,js,jf = child.HMM_build(matrix,i,js,jf,size)
    #             else:
    #                 matrix,i,js,jf = child.HMM_build(matrix,i,js,jf,size)
    #                 i += 1
    #     return matrix,i,js,jf
