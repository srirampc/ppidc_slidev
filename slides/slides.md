---
# try also 'default' to start simple
theme: ext/slidev-theme-spc-gt
# addons, can be a list of package names or local paths
# Learn more: https://sli.dev/guide/theme-addon.html#use-addon
addons:
  - fancy-arrow
  - tikzjax
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
#background: https://cover.sli.dev
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
  local: Concourse T3
---

## A Parallel Algorithm for the Construction of Partial Information Decomposition-based Genome-scale Networks from Single-Cell Datasets

#### _**SC '26 @ Chicago, USA**_

<template #extra>

Joint work with [Maneesha Aluru](#) and [Srinivas Aluru](#)

</template>

---
transition: fade-out
layout: two-cols-header
---

# Construction of Gene Regulatory Networks (GRN)

::left::

<v-clicks>

- **Goal :** Learn gene interactions from gene expression data.
- **Gene Expression Data:** Snapshots of gene activity across different samples or conditions.
- Single-cell gene expression datasets:
  - Large datasets with millions of cells.
  - Sparse, has missing values and noisy.
  - Understand cell-specific interactions.

</v-clicks>

::right::

<div class="h-full flex flex-col justify-center items-center">

![](/img/Network_Construction.svg){width=600px}

</div>

<style>
.two-cols-header {
  column-gap: 0px; /* Adjust the gap size as needed */
}
</style>

---
transition: fade-out
layout: none
clicks: 7
---

<AllpairsPairwiseNet auto-start class="absolute inset-0" />

---
transition: fade-out
---

# Summary of Contributions

<v-clicks depth="2">

- Focus on **PIDC**
  - Partial-information decomposition (PID) based network construction method.
  - Shown to be effective for single-cell datasets.
  - Takes $O(n)$ time for each pair, and hence $O(n^3)$ time for $\binom{n}{2}$ pairs.

- Our Contributions
  - A novel $O(n^2 \log n)$ sequential algorithm, a factor of $n/\log n$ improvement.
  - Distributed-memory parallelization that takes $O(n^2/p + \mathsf{T}_{\mathtt{sort}}(n^2, p))$ time.
  - Achieves $158$X speedup over the existing PIDC implementation.
  - Scaling to Human Genome: $30,000$-gene network from $\approx800$K cells in $2.5$ hours using $2,048$ cores.

</v-clicks>

---
transition: fade-out
---

# Background : Random variables and MI

<v-clicks depth="1">

- Notations: Random Variables and Distributions
  - $\mathcal{X}, |\mathcal{X}|=n$: Set of discrete random variables, each representing a gene.
  - Uppercase $X, Y, Z, \ldots$ for random variables.
  - Lowercase $x \in X$ denote the distinct values r. v. $X$ can take.
  - $P(X,Y)$: Joint distribution of gene expression of two genes $X$ and $Y$.
- Mutual Information
  $$I(X,Y) = \sum_{x \in X} \sum_{y \in Y} p(x,y) \log \left( \frac{p(x,y)}{p(x)p(y)} \right)$$
- **Assumption: Number of values any random variable can take is constant**
</v-clicks>

<!--
Describe MI
-->

---
transition: fade-out
layout: none
clicks: 5
---

<SpecificSpecificInfo auto-start class="absolute inset-0" />

<!--
Fix mutual information
-->

---
transition: fade-out
layout: none
clicks: 5
---

<Redundancy auto-start class="absolute inset-0" />

<!--
Make sure to emphasize the decomposisiton
-->

---
transition: fade-out
layout: none
clicks: 5
---

<XyzpucPUC auto-start class="absolute inset-0" />

---
transition: fade-out
---

# PUC : Algebraic Simplification and Bottleneck

<v-clicks depth="1">

PUC, $\gamma(X, Y)$, can be simplified as below:
  $$
  \begin{aligned}
  \gamma(X, Y) &=  \frac{1}{I(X, Y)} \sum_{Z \not\in \{X, Y\}} \nu((X, Z); Y) + \nu((Y, Z); X)\\
   &= \frac{1}{I(X, Y)} \sum_{Z \not\in \{X, Y\}} 2I(X, Y) - \rho((X, Z); Y) - \rho((Y, Z); X) \\
   &= \frac{1}{I(X, Y)} \left( 2(n-2) I(X, Y) - \sum_{Z \not\in \{X, Y\}} \rho((X, Z); Y) - \sum_{Z\not\in \{X, Y\}} \rho((Y, Z); X) \right)
  \end{aligned}
  $$

 Bottleneck: <span v-mark.yellow>$\sum_{Z} \rho((X, Z); Y)$</span> and $\sum_{Z} \rho((Y, Z); X)$

</v-clicks>

---
transition: fade-out
layout: none
clicks: 13
---

<InsightAlgoInsight auto-start class="absolute inset-0" />

<!--
Remove the \mathcal{T} from the slide
-->

---
transition: fade-out
---

# Sequential Algorithm Summary

|     | Given: $P(X), \forall X \in \mathcal{X}$; $P(X, Y),\forall (X, Y)$                         |                   |
| --- | ------------------------------------------------------------------------------------------ | ----------------- |
| 1   | Compute Mutual Information, $I(X,Y)$ and tables $\mu(y; X), \forall (y, X)$                | $O(n^2)$          |
| 2   | Compute $\mathbf{S}_y$, sorted $\mu(y; X)$ tables $\forall y \in Y, Y \in \mathcal{X}$     | $O(n^2 \log n)$   |
|     | Compute $\mathbf{P}_y$, prefix sum table for all $\mathbf{S}_y$ tables                     | $O(n^2)$          |
| 3   | $\forall (X,Y)$, Compute (a) $\sum_Z\nu((X,Z); Y)$, (b)$\sum_Z\nu((Y,Z); X)$               | $O(n^2)$          |
| 4   | $\forall (X,Y)$, Compute PUC                                                               | $O(n^2)$          |

---
transition: fade-out
layout: none
clicks: 7
---

<ParInsightParAlgoInsight auto-start class="absolute inset-0" />

<!--
Update Header;
-->

---
transition: fade-out
---

# Parallel Algorithm

|     | Given $\mathbf{S}, \mathbf{P}, \mathbf{Q}, \mathbf{R}$, flat arrays of size $n \sum_{Y \in \mathcal{X}}  \|Y\|$,  distributed across $p$ processes    |                     |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| 1   | Let $j \gets$ processor's rank                                                                                                                        |                                       |
| 2   | Insert $\langle Y, X, y, s_{\mu}, p_{\mu}  \rangle$ for each entry in $\mathbf{S}^{(j)}, \mathbf{P}^{(j)}, \mathbf{Q}^{(j)}, \mathbf{R}^{(j)}$        | $O(n^2/p)$                            |
| 3   | Insert $\langle Y, X, I(X, Y) \rangle$ to $\mathsf{puc}\textrm{-}\mathsf{tuples}^{(j)}$                                                               | $O(n^2/p)$                            |
| 4   | Sort in parallel the distributed $\mathsf{puc}\textrm{-}\mathsf{tuples}$                                                                              | $\mathsf{T}_{\mathtt{sort}}(n^2, p))$ |
| 5   | Compute PUC from sorted $\mathsf{puc}\textrm{-}\mathsf{tuples}$                                                                                       | $O(n^2/p)$                            |

---
transition: fade-out
---

# Implementation : Platform and Data Processing

- PIDC implementation in `julia`
  - Updated to read input data from `HDF5` input instead of `csv` files
- Our MPI Implementation in `Rust`
  - `rsmpi` : MPI 3.1 wrapper (Experiments use `OpenMPI`)
  - `sope` : Convenience library features include generic struct types, sorting etc
  - `hdf5-rs` : Updated for parallel I/O
- I/O of HDF5 files with `anndata` specifications
  - Save $\mathsf{D}^T$ with genes as rows for faster parallel I/O


---
transition: fade-out
---

# Implementation : Computing $P(X)$ and $P(X,Y)$

- Marginal distributions, $P(X)$
  - Block distribute $n$ genes across $p$ processes
  - Compute histogram with BayesianBlocks method for $n/p$ genes
- Joint Distribution
  - Copy of $P(X), \forall X$ in every process (Only 26MB for 30K genes).
  - Each process computes $P(X, Y)$ $\approx \binom{n}{2}$ genes.
  - Sorted order of $(X, Y)$ enable constant time ownership id.

<!--
Consider removing this
-->

---
transition: fade-out
layout: none
clicks: 5
---

<DataB auto-start class="absolute inset-0" />

---
transition: fade-out
layout: two-cols-header
---

# Implementation : Handling large datasets

::left::
![](/img/block-dist.svg){width=300px lazy}

::right::

- Datasets with $m$ exceeding millions of cells.
- Batch-wise processing of pair blocks with only $O(mn/p)$ data per process.
- Row/column-wise distribution
  - Parallel I/O of non-contiguous overlapping rows of $\mathsf{D}^T$.
- Diagonal distribution
  - Uniform block-distributed parallel read of the input HDF5

---
transition: fade-out
---

# Implementation : Parallel Algorithm

- Compute MI and $\mu(\cdot, \cdot)$
  - $I(X, Y )$
  - $\mu(x; Y) \forall x \in Y$, and $\mu(y; X), \forall y \in Y$.
  - Distribute $\mu(x; Y)$ values in the order of $Y$ , followed by $y$, and then by X.
- Compute PUC, $\gamma(X, Y)$
  - $\mathbf{Q}$ and $\mathbf{R}$ are not explicitly computed
    - Derived from the ordering of $X$ and $x \in X$
  - Radix sorting with a single `MPI_all2allv`

---
transition: fade-out
---

# Experiments: Datasets

| Dataset | Tissue |     $m$ |    $n$ | $\mathsf{D}$ (GB) | $\sum \|P(X,Y)\|$ (GB) |
| :------ | :----: | ------: | -----: | ----------------: | ---------------------: |
| D1      |  PBMC  |  23,766 |  5,000 |              0.44 |                  47.38 |
| D2      |  Lung  |  91,068 |  5,000 |              1.82 |                 121.10 |
|         |   "    |         | 10,000 |              3.39 |                 476.46 |
|         |   "    |         | 15,000 |              5.08 |               1,131.42 |
| D3      |  PBMC  | 794,170 | 20,000 |             57.63 |               8,828.66 |
|         |   "    |         | 30,000 |             86.45 |              19,570.00 |

---
transition: fade-out
layout: two-cols-header
---

# Results for dataset $D1$

::left::

- Machine: Shared memory machine with 72-core Intel® Xeon® E7-8870 2.7 GHz CPU
- Max. speedup of 52 on 64 cores
- Communication and I/O times are a small fraction (at most 11% with 64 cores)
- 158X times faster than PIDC, reducing the runtime from 10.8 hours to about $4$ minutes.

::right::

##### Speedup vs. number of cores

![](/img/strong-scaling-small-ai.svg){width=800px lazy}

---
transition: fade-out
---

# Results : Dataset $D2$ w. 5K genes

| ![](/img/strong-scaling-big-ai.svg){width=400px lazy} | ![](/img/runtime-stacked-ai.svg){width=520px lazy} |
| ----------------------------------------------------- | -------------------------------------------------- |

- 484-node cluster where each node has a 24-core Intel® Xeon® 6226 2.7 GHz processor
- Max speedup of speedup of 96 with 512 cores, which then drops to 55 with 1, 024 cores

---
transition: fade-out
---
# Results : Big Datasets

| $n$                     |    20K |    20K |    30K |    30K |
| ----------------------- | -----: | -----: | -----: | -----: |
| $p$                     | 1, 024 | 2, 048 | 1, 024 | 2, 048 |
| Distributions, µ (min.) | 116.89 |  71.08 | 243.39 | 149.36 |
| µ →PUC (min.)           |   0.91 |   1.02 |   1.63 |   1.90 |
| Total Runtime (min.)    | 117.80 |  72.10 | 245.02 | 151.26 |

- 20K-gene network took 1.9 hours and 1.2 hours, respectively, with 1, 024 cores and 2, 048 cores.
- 30K-gene network took 4.1 hours and 2.5 hours, respectively, with 1, 024 cores and 2, 048 cores.
- No linear scaling from 1, 024 to 2, 048 cores due to the increase in I/O time.

---
transition: fade-out
---
# Conclusions

- Key Contributions
  - $O(n^2 \log n)$ sequential algorithm, a factor of $n/\log n$ improvement.
  - $O(n^2/p + \mathsf{T}_{\mathtt{sort}}(n^2, p))$ distributed parallel algorithm on $p$ processors.
  - To our knowledge, the 30K network is the largest network covering the complete human genome.
- Future work
  - Improve scalability of computing the distributions by better process assignment.
  - Address the cases where the gene expression values need to be treated as continuous.
  - I/O scalability via asynchronous read/writes.


---
transition: fade-out
layout: intro
---
# Misc. Results


---
transition: fade-out
layout: two-cols-header
---

# Results : Runtime vs. number of gene Weak Scaling

::left::

- D2 using 256 cores, varying network size from 1, 000 genes
  to 18, 000 genes.
- Observed growth is close to $O(n^2)$ rather than $O(n^2 \log n)$
  because parallel sort does not dominate the run-time .

::right::

![](/img/runtime-growth-n-ai.svg){width=500px lazy}
