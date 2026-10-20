---
theme: ext/slidev-theme-spc-gt
# addons, can be a list of package names or local paths
# Learn more: https://sli.dev/guide/theme-addon.html#use-addon
addons: 
  - fancy-arrow
  - tikzjax
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: https://cover.sli.dev
# some information about your slides (markdown enabled)
title: Parallel PIDC
info: false
# author field for exported PDF or PPTX
author: Sriram P C
# apply UnoCSS classes to the current slide
class: text-center
# https://sli.dev/features/drawing
drawings:
  persist: false
# slide transition: https://sli.dev/guide/animations.html#slide-transitions
transition: slide-left
# enable Comark Syntax: https://comark.dev/syntax/markdown
comark: true
# duration of the presentation
duration: 20min
presenterName: Sriram P Chockalingam 
affiliation: Georgia Institute of Technology
mdc: true
# Fonts
fonts:
  sans: Concourse T3
  serif: Equity Text B
  local: Concourse T3
---

## A Parallel Algorithm for the Construction of Partial Information Decomposition-based Genome-scale Networks from Single-Cell Datasets 

####   _**SC '26 @ Chicago, USA**_

<template #extra>

Joint work with [Maneesha Aluru](#) and [Srinivas Aluru](#)

</template>

---
transition: fade-out
---

# Gene Regulatory Networks (GRN) construction

- Advances in single-cell gene expression data 
  - Data size increased from tens of thousands to millions
  - Data has missing values and noisy
- Mutual Information (MI) based networks
  - Higher MI implies a stronger correlation
  - Focus on **PIDC**, a method tailored of single-cell data
  - **PIDC** handles data characteristics via. partial-information decomposition. 
  - **PIDC** takes $O(n^3)$ time 
  
---
transition: fade-out
---
# Problem Definition and Contributions

- Formal Problem Definition:
  - Input: $\mathsf{D} \in \mathbb{R}^{m \times n}$, $m$ observations of $n$ genes.  
  - Output: $\mathsf{G} \in \mathbb{R}^{n \times n}$, adjacency matrix representing a network of $n$ genes,
- Contributions
  - $O(n^2 \log n)$ sequential algorithm, a factor of $n/\log n$ improvement.
  - $O(n^2/p + \mathsf{T}_{\mathtt{sort}}(n^2, p))$ parallel algorithm. 
  - Achieves $158$X speedup over the existing PIDC implementation.
  - Scales to a human-genome: $30,000$-gene network from $\approx800$K cells in $2.5$ hours using $2,048$ cores.

---
transition: fade-out
---
# Background : Random variables and MI

- Notations
  - Uppercase alphabet $X, Y, Z$: Random variables
  - $\mathcal{X}, |\mathcal{X}|=n$: Set of discrete random variables, each representing a gene.
  - $x \in X$ to also denote the distinct values, random variable $X$ can take.
  - $P(X,Y)$ joint distribution of two genes represented by $X$ and $Y$.
  - $p(x, y)$: probability value  $P(X=x,Y=y)$ 
- Mutual Information:
  $$I(X,Y) = \sum_{x \in X} \sum_{y \in Y} p(x,y) \log \left( \frac{p(x,y)}{p(x)p(y)} \right)$$

---
transition: fade-out
---
# Background : Redundancy and Unique Contribution

- Specific Information: Given $X \in \mathcal{X}, y \in Y$
    $$
        I_{s}(y; X) = \sum_{x \in X} \frac{p(x,y)}{p(y)} \log \left( \frac{p(x,y)}{p(x) \cdot p(y)} \right)
    $$
- Redundancy
  - $\rho((X, Y); Z) = \sum_{z \in Z} p(z) \min (I_{s}(z; X), I_{s}(z; Y) )$ 
- Partial Information Decomposition
  - Unique Contribution, $\nu((X, Z); Y)) =  I(X, Y) - \rho((X, Z); Y)$
---
transition: fade-out
---
# Background : PUC

- Unique Contribution, $\nu((X, Z); Y)) =  I(X, Y) - \rho((X, Z); Y)$
- PUC, $\gamma(X, Y)$, is formally defined as,
  $$
  \begin{aligned}
  \gamma(X, Y) &=  \sum_{Z \in \mathcal{T}} \frac{\nu((X, Z); Y) + \nu((Y, Z); X)}{I(X, Y)}\\
   &= \sum_{Z \in \mathcal{T}} \frac{2I(X, Y) - \rho((X, Z); Y) - \rho((Y, Z); X)}{I(X, Y)} \\
   &=  \frac{1}{I(X, Y)} \left( 2(n-2) I(X, Y) - \sum_{Z \in \mathcal{T}} \rho((X, Z); Y) + \rho((Y, Z); X) \right)
  \end{aligned}
  $$
---
transition: fade-out
---
# Algorithm : Key Insight
- Tanles

---
transition: fade-out
---
# Sequential Algorithm

  ||Given: $P(X), \forall X \in \mathcal{X}$; $P(X, Y),\forall (X, Y)$ ||
  |--|--|--|
  |1| Compute Mutual Information, $I(X,Y)$ |$O(n^2)$|
  |2| Compute tables $\mu(y; X), \forall (y, X)$ |$O(n^2 d)=O(n^2)$|
  |3| $\forall y \in Y, Y \in \mathcal{X}, \mathbf{S}_y \gets$ Sorted $\mu(y; X)$ table | $O(n^2 \log n)$|
  |3| $\forall y \in Y,Y \in \mathcal{X}, \mathbf{P}_y \gets$ Prefix summed $\mathbf{S}_y$ table | $O(n^2)$|
  |4| $\forall (X,Y)$, Compute (a) $\sum_Z\nu((X,Z); Y)$, (b)$\sum_Z\nu((Y,Z); X)$  |  $O(n^2)$|
  |5| $\forall (X,Y)$, Compute PUC  | $O(n^2)$|

---
transition: fade-out
---
# Parallel Algorithm : Data Structures

- Flat arrays, uniformly distributed across $p$ processes
  - $\mathbf{S}$, concatenation of all the $\mathbf{S}_y$
  - $\mathbf{P}$, concatenation of all the $\mathbf{P}_y$
  - $\mathbf{Q}$,  an array of size $|\mathbf{S}|$
    - $\mathbf{Q}[i]$ holds the value $y$ corresponding to the $\mu(y; X)$ value in $\mathbf{S}[i]$.
  - $\mathbf{R}$,  an array of size $|\mathbf{S}|$
    -  $\mathbf{R}[i]$ holds the variable $X$ corresponding to the $\mu(y; X)$ value in $\mathbf{S}[i]$.
 - Each array size of $n\sum_{Y \in \mathcal{X}} |Y| = O(n^2)$
---
transition: fade-out
---
# Parallel Algorithm 
  ||Given $\mathbf{S}, \mathbf{P}, \mathbf{Q}, \mathbf{R}$||
  |-|-|-|
  |1|Let $j \gets$ processor's rank||
  |2| Compute $\langle X, Y,  \sum \nu((X, Z); Y) \rangle$ for each entry $\mathbf{S}^{(j)}, \mathbf{P}^{(j)}, \mathbf{Q}^{(j)}, \mathbf{R}^{(j)}$|$O(n^2/p)$|
  |3|Insert $\langle X, Y,  \sum \nu((X, Z); Y) \rangle$ to $\mathbf{R}^{(j)}$|$O(n^2/p)$|
  |4|Insert $\langle X, Y,  I(X, Y) \rangle$ to $\mathbf{R}^{(j)}$|$O(n^2/p)$|
  |5|Parallel Sort the distributed $\mathbf{R}$|$\mathsf{T}_{\mathtt{sort}}(n^2, p))$|
  |6|Compute PUC from sorted $\mathbf{R}^{(j)}$ |$O(n^2/p)$|

---
transition: fade-out
---
# Implementation : Platform and Data Processing   
- fa 

---
transition: fade-out
---
# Implementation : Computing $P(X)$
- implementation

---
transition: fade-out
---
# Implementation : Computing $P(X,Y)$
- implementation
![](/img/block-dist.svg){width=300px lazy}

---
transition: fade-out
---
# Implementation : Parallel Algorithm
- implementation

---
transition: fade-out
---
# Experiments: Datasets
| Dataset | Tissue | $m$ | $n$ | $\mathsf{D}$ (GB) | $\sum \|P(X,Y)\|$ (GB) |
|:-|:-:|-:|-:|-:|-:|
|D1 |  PBMC |  23,766 |   5,000 |   0.44 |     47.38 |  
|D2 |  Lung |  91,068 |   5,000 |   1.82 |    121.10 | 
|   |   "   |         |  10,000 |   3.39 |    476.46 | 
|   |   "   |         |  15,000 |   5.08 |  1,131.42 | 
|D3 | PBMC  | 794,170 |  20,000 |  57.63 |  8,828.66 | 
|   |   "   |         |  30,000 |  86.45 | 19,570.00 | 

---
transition: fade-out
layout: two-cols
image: /img/strong-scaling-small-ai.svg
---
# Results for dataset $D1$
- 385 x
- 385 x
 
::right::
### Speedup vs. number of cores
![](/img/strong-scaling-small-ai.svg){width=800px lazy}
---
transition: fade-out
---
# Results : Dataset $D2$
  | ![](/img/strong-scaling-big-ai.svg){width=400px lazy} | ![](/img/runtime-stacked-ai.svg){width=520px lazy} |
  |--|--|
- Max speedup of 
---
transition: fade-out
---
# Results : Weak Scaling
- Weak
![](/img/runtime-growth-n-ai.svg){width=500px lazy}
---
transition: fade-out
---
# Results : Big Datasets
![](/img/relative-speedup-ai.svg){width=500px lazy}

---
transition: fade-out
---
# Conclusion
- conclude
