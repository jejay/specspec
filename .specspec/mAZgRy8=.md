---
id: mAZgRy8=
type: requirement
parents:
- LtROyww=
- XzlIEcQ=
- bOXyw00=
---
# Pan and zoom the whole graph with one d3-zoom camera

A camera built on d3-zoom applies one transform to the whole graph, to the DOM cards and to the SVG of the links alike. The owner pans without limit and zooms between 12% and 250%. A drag with the middle button or on the background pans, and the wheel or a pinch zooms at the position of the pointer. Buttons zoom in steps, restore actual size and frame the graph or the selected node. On the keyboard the arrow keys pan, `+`, `=` and `-` zoom in steps, `1` restores actual size, and Home or `F` frames the graph. Zooming and framing work with the size of the viewport, and the arrangement of the nodes follows from their relationships in the world.

Each view keeps separate cameras for the overview and for the view of a selected node, together with its draft and the original node that the draft started from. Returning to the overview and refreshing keep the positions of the cameras, and framing changes them. Camera movements are animated unless the system asks for reduced motion. Inside a card the controls work as in any form: selecting text, scrolling and resizing a text field, opening a dropdown and pressing a button belong to the controls and move no camera. Moving the camera changes the presentation alone.
