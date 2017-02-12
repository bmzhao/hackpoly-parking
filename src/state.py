import uuid
import math


class VisualState(object):
    def __init__(self, blobs):
        self.blobs = blobs







class Blob(object):
    def __init__(self, (center_x,center_y),(x,y,w,h)):
        self.id = str(uuid.uuid4())
        self.centroid = (center_x, center_y)
        self.boundingRect = (x,y,w,h)


    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not (self == other)

    def dist(self, other):
        return math.hypot(self.centroid[0] - other.centroid[0],self.centroid[1]- other.centroid[1] )
