
class BubbleText():
    def __init__(self, id, coordinates, text, translation):
        self.id = id
        self.xmin = int(coordinates[0])
        self.ymin = int(coordinates[1])
        self.xmax = int(coordinates[2])
        self.ymax = int(coordinates[3])
        self.width = self.xmax - self.xmin
        self.height = self.ymax - self.ymin

        self.text = text
        self.translation = translation