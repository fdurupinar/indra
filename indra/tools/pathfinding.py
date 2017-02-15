import graphillion

class Pathfinder(object):
    def __init__(self, sif_str):
        lines = sif_str.split('\n')
        self.universe = []
        for lin in lines:
            if not lin:
                continue
            s, w, t = lin.split(' ')
            self.universe.append((s, t, w))
        self.graphset = graphillion.GraphSet
        self.graphset.set_universe(self.universe)

    def get_paths(self, source, target):
        paths = self.graphset.paths(source, target)
        return paths
