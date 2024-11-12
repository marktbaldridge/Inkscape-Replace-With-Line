#!/usr/bin/env python3
import inkex
from inkex import PathElement

class SolidLineExtension(inkex.EffectExtension):
    def effect(self):
        # Get selected elements
        selection = self.svg.selection
        paths = [node for node in selection if isinstance(node, PathElement)]
        if not paths:
            inkex.errormsg("Please select at least one path.")
            return

        # Collect all nodes from the selected paths
        nodes = []
        for path in paths:
            # Get the cumulative transformation matrix for the path
            transform = path.composed_transform()

            # Get the path data and apply the transformation
            csp = path.path.transform(transform).to_superpath()

            for subpath in csp:
                for ctl_pt in subpath:
                    node = ctl_pt[1]  # The current point
                    nodes.append(node)

        if len(nodes) < 2:
            inkex.errormsg("Need at least two nodes to create a line.")
            return

        # Find the two nodes that are furthest apart
        max_distance = 0
        max_pair = None
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                node1 = nodes[i]
                node2 = nodes[j]
                dx = node1[0] - node2[0]
                dy = node1[1] - node2[1]
                distance = (dx**2 + dy**2)**0.5
                if distance > max_distance:
                    max_distance = distance
                    max_pair = (node1, node2)

        if not max_pair:
            inkex.errormsg("Could not find the furthest nodes.")
            return

        # Create a new path data with a line between the two furthest nodes
        new_path_data = [
            ['M', max_pair[0]],
            ['L', max_pair[1]]
        ]

        # Create a new path element
        new_path = PathElement()
        new_path.style = paths[0].style if paths else {}
        new_path.path = inkex.Path(new_path_data)
        
        # Append the new path to the current layer or root if no layer is found
        current_layer = self.svg.get_current_layer()
        if current_layer is None:
            current_layer = self.svg.getroot()
        current_layer.append(new_path)

        # Delete the original dashed paths
        for path in paths:
            path.delete()

if __name__ == '__main__':
    SolidLineExtension().run()
