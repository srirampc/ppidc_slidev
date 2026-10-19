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
  - Achieves $158$X speedup over the existing method.
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

- Specific Information: Given $X \in \mathcal{X}, y \in Y$
 <FancyArrow from="(10, 20)" to="(30, 40)" />
---
transition: fade-out
---
# Algorithm : Key Insight
- Tanles

---
transition: fade-out
---
# Algorithm : Sequential Algorithm
- implementation

---
transition: fade-out
---
# Algorithm : Parallel Algorithm I
- implementation

---
transition: fade-out
---
# Algorithm : Parallel Algorithm II
- implementation

---
transition: fade-out
---
# Implementation 
- implementation

---
transition: fade-out
---
# Implementation : Parallel Algorithm
- implementation

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
# Implementation : Algorithm
- implementation

---
transition: fade-out
---
# Experiments: Datasets
- 385 x

---
transition: fade-out
---
# Results for dataset $D1$
- 385 x
![](/img/strong-scaling-small-ai.svg){width=500px lazy}
---
transition: fade-out
---
# Results : Dataset $D2$
- test
  |A|B|
  |--|--|
  | ![](/img/relative-speedup-ai.svg){width=400px lazy} | ![](/img/runtime-stacked-ai.svg){width=520px lazy} |
  |--|--|
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
![](/img/strong-scaling-big-ai.svg){width=500px lazy}

---
transition: fade-out
---
# Conclusion
- conclude
