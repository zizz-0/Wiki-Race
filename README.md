# Wiki Race

This program finds a path from one Wikipedia article to another using only hyperlinks.
Still a work in progress.

---

## Speed and Efficiency

### Threading
The program initially only used threading in `wikiRace.py` with 20 max workers. To try and increase speed even further, threading was added to `aStar.py` with 10 max workers. In some rare cases, this cut down the program runtime by over 10 seconds. However, in most cases, it increased the runtime by over 10 seconds. 

Typically, the threading in `aStar.py` would increase runtime on shorter, less complex paths due to the overhead. For the more complex paths, it would decrease program runtime by a few seconds. I ended up making the threading in `aStar.py` optional with the default being to not use it.

### BFS
Originally, the program used Breadth-First Search to try to find the shortest possible path between the start and end articles. This solution ended up taking a very long time for the program to finish, even with threading. It took **over 180 seconds** to make a search that was two hyperlinks away (Whale Shark > Filter Feeder > Organ (biology)) and **over 200 seconds** for another search that was two hyperlinks away (Whale Shark > Japan > Formula One).

### A* Search
After testing with BFS, I switched over to A* Search. `aStar.py` was originally written using Wikipedia article title lengths to estimate the cost between two nodes. This was meant to be a placeholder until a better method was determined. Using this heuristic, the search that took BFS over 180 seconds (Whale Shark > Filter Feeder > Organ (biology)) only took A* **4 seconds.** The search that took BFS over 200 seconds (Whale Shark > Japan > Formula One) took A* **55 seconds.**

After determining A* would be a better overall search algorithm to use for this program, I tried to find a better method of estimating cost for the heuristic function. The first idea tested was using ![Wikipedia2vec](https://wikipedia2vec.github.io/wikipedia2vec/), which is a model of word2vec (which obtains vector representations of words) that was specifically trained on Wikipedia articles. However, even with threading, this method was too complex and increased the speed exponentially since it was vectorizing each Wikipedia article title. The search that took A* using title lengths as a comparison 4 seconds (Whale Shark > Filter Feeder > Organ (biology)) took A* using Wikipedia2vec **488 seconds.**

## Visualizing Graph
After completing the search, the graph is visualized using ![NetworkX](https://networkx.org/) and ![Matplotlib Pyplot](https://matplotlib.org/3.5.3/api/_as_gen/matplotlib.pyplot.html). Because the search is so complex due to the threading, displaying all nodes makes the graph *very* unreadable. I tried out three different functions to see which was the easiest to read and made the most sense visually. I also added constraints, like setting a maximum number of nodes or a threshold for nodes based on heuristics.

![spring layout](imgs/springLayout.png)
![shell layout](imgs/shellLayout.png)
![planar layout](imgs/planarLayout.png)

While adding a maximum number of nodes removes the aspect of just how complex the graph is, it is the most readable. The final visualized graph ended up being a shell layout graph with a maximum of 300 nodes and a threshold of 5 (this can change depending on the heuristic).

![visualized graph](imgs/final_thresholdMaxEdgesSpringLayout.png)

## Current Status
Currently, `wikiRace.py` is using A* Search with title lengths as estimate cost comparison. `wikiRace.py` is threaded with 20 max workers, and `aStar.py` is threaded with 10 max workers, but defaults to using no threading.

## Future Goals
In the near future, `aStar.py` will be optimized using a better cost estimation for the heuristic function. This will increase the overall speed and efficiency of the program. One possibility I will be looking into is comparing Wikipedia article categories and checking for overlap.