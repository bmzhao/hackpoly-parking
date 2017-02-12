import uuid
import math


class VisualState(object):
    def __init__(self, blobs):
        self.blobs = blobs


class Blob(object):
    def __init__(self, x, y, w, h, area):
        self.id = str(uuid.uuid4())
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.area = area

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not (self == other)

    def dist(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)

    def close_to(self, other, ratio=0.25):
        right = self.x + ratio * self.w/2
        left = self.x - ratio * self.w/2

        bottom = self.y - ratio * self.h/2
        top = self.y + ratio * self.h/2

        otherBottom = other.y - other.h/2
        otherTop = other.y + other.h/2

        otherRight = other.x + other.w/2
        otherLeft = other.x - other.w/2

        if (otherBottom < top and otherBottom > bottom) or \
                (otherTop < top and otherTop > bottom) or \
                (otherRight < right and otherRight > left) or \
                (otherLeft < right and otherRight > left):
            return True
        else:
            return False

    def merge(self, other):
        right = self.x + self.w / 2
        left = self.x - self.w / 2

        bottom = self.y - self.h / 2
        top = self.y + self.h / 2

        otherBottom = other.y - other.h / 2
        otherTop = other.y + other.h / 2

        otherRight = other.x + other.w / 2
        otherLeft = other.x - other.w / 2

        newRight = max(right, otherRight)
        newLeft = min(left, otherLeft)
        newTop = max(top, otherTop)
        newBottom = min(bottom, otherBottom)

        newCenterX = (newRight + newLeft) / 2
        newCenterY = (newTop + newBottom) / 2

        newWidth = (newRight - newLeft) / 2 / 1.2
        newHeight = (newTop - newBottom) / 2 / 1.2
        self.x = newCenterX
        self.y = newCenterY
        self.area += other.area
        self.w = newWidth
        self.h = newHeight
