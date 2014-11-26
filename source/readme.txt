Command line options/flags:

-n N: N is the path to the Node csv file
-n is a required argument

-e E: E is the path to the Edge csv file
-a A: A is the path to the Adjacency Matrix csv file
Either -e or -a option should be used. 

-l L: L is the path to the lobe csv file
Use if you want to specify the extents of the lobes manually

-s S: S is a number that specifies that only edges with a weight in the top s percent of the full range of edge weights will be rendered
-t T: T is a number that specifies that t% of edges will be rendered. Those edges will be those with the highest weights. If there is a tie between candidates of the same weight, it will be broken non-deterministically
Either -s, or -t, or neither can be used, but not both at the same time. 

-o O: O is the path to the output file
Optional (default is fmri-viz.pdf)
