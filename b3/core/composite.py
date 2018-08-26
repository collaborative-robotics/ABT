import b3

__all__ = ['Composite']


class Composite(b3.BaseNode):
    category = b3.COMPOSITE

    def __init__(self, children=None):
        super(Composite, self).__init__()

        self.children = children or []
        self.action_size = 0

    def scan(self, size):
        temp = size
        for child in self.children:
            if child.category == b3.ACTION:
                size+=1
            if child.category == b3.COMPOSITE:
                size = child.scan(size)
        self.action_size = size - temp
        return size
    def HMM_build(self,matrix,i,js,jf,size):
        for current,child in enumerate(self.children):
            if child.category == b3.COMPOSITE:
                if isinstance(child,b3.Sequence):
                    print "Hit Sequence"
                    if i+len(self.children) >= size:
                        js = i+1
                        jf = size + 1
                    else:
                        js = i + 1
                        jf = i + len(self.children)
                    matrix,i,js,jf = child.HMM_build(matrix,i,js,jf,size)
                if isinstance(child,b3.Priority):
                    print "Hit Priority"
                    if i+len(self.children) >= size:
                        js = size
                        jf = i+1
                    else:
                        js = i + len(self.children)
                        jf = i + 1
                    matrix,i,js,jf = child.HMM_build(matrix,i,js,jf,size)
                else:
                    matrix,i,js,jf = child.HMM_build(matrix,i,js,jf,size)
                    i += 1
        return matrix,i,js,jf
