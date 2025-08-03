# DIMACS Graph Coloring Dataset

This repository contains instances from the **DIMACS Graph Coloring Benchmark Dataset**, a standard benchmark suite widely used for evaluating algorithms on the **Graph Coloring Problem (GCP)**.

## 📌 Dataset Overview

The dataset was originally introduced as part of the:

> **Second DIMACS Implementation Challenge (1992):**  
> "Cliques, Coloring, and Satisfiability"  
> Organized by the Center for Discrete Mathematics and Theoretical Computer Science (DIMACS), Rutgers University.

Its purpose was to facilitate fair comparison between graph coloring algorithms on a wide range of real-world and synthetic instances.

## 📂 Format

All graphs are provided in the **DIMACS `.col` format**, which includes:
- A `p edge` header specifying the number of nodes and edges
- A list of `e u v` entries representing undirected edges between node `u` and node `v`

Example:
```
c Example graph
p edge 5 4
e 1 2
e 2 3
e 3 4
e 4 5
```

## 🧩 Use Cases

These instances have been widely used in:
- Benchmarking **graph coloring heuristics and exact solvers**
- Studying **clique and independent set** problems
- Evaluating **SAT/ILP/CSP-based formulations**

## Parsed Data Format
[METADATA]
File: xxxx
Description: 
......

[GCP_DATA_INFO]
Type: GCP, Graph Coloring Problem 
Node: xxx
Edge: xxx

[ADJACENCY_List] 
2: [edge that node < 2]
3: [edge that node < 3]
....

## 📚 Source

All the DIMACS benchmark and upper bound information are from:

- DIMACS Benchmark info for Graph Coloring Problem  
  👉 [https://cedric.cnam.fr/~porumbed/graphs/index.html](https://cedric.cnam.fr/~porumbed/graphs/index.html)  
  👉 [https://sites.google.com/site/graphcoloring/vertex-coloring](https://sites.google.com/site/graphcoloring/vertex-coloring)

- DIMACS Benchmark info for Clique Problem  
  👉 [https://iridia.ulb.ac.be/~fmascia/maximum_clique/](https://iridia.ulb.ac.be/~fmascia/maximum_clique/)

Additional hosting and documentation provided by **Michael Trick** at Carnegie Mellon University:

- [https://mat.tepper.cmu.edu/COLOR/instances.html](https://mat.tepper.cmu.edu/COLOR/instances.html)  
- [https://mat.tepper.cmu.edu/COLOR02](https://mat.tepper.cmu.edu/COLOR02)  
- [http://archive.dimacs.rutgers.edu/Challenges/](http://archive.dimacs.rutgers.edu/Challenges/)
