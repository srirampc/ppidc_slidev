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

- **Goal :** Identify gene interactions from gene expression data.
- **Gene Expression Data:** Snapshots of gene activity across different samples and/or conditions.
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

# Our Contributions

<v-clicks depth="2">

- Focus on **PIDC** (_Chan et. al. (2017)_)
  - Partial-information decomposition (PID) based network construction method.
  - Generates accurate networks on single-cell datasets (Benchmarked by _Pratapa et.al. (2020)_).
  - Takes $O(n)$ time for each pair, and hence $O(n^3)$ time for $\binom{n}{2}$ pairs.

- Our Contributions
  - A novel $O(n^2 \log n)$ sequential algorithm, a factor of $n/\log n$ improvement.
  - $O(n^2/p + \mathsf{T}_{\mathsf{sort}}(n^2, p))$ time distributed-memory parallelization on $p$ processes.
  - Achieve $158$X speedup over the existing parallel PIDC implementation.
  - Scale to Human Genome: $30,000$-gene network from $\approx 800$K cells in $2.5$ hours on $2,048$ distributed cores.

</v-clicks>

---
transition: fade-out
---

# Background: Random variables and MI


- $\mathcal{X}, |\mathcal{X}|=n$: Set of **discrete** random variables, each representing a gene.
- Uppercase $X, Y, Z, \ldots$ for random variables.
- Lowercase $x \in X$ denote the distinct values a random variable $X$ can take.
- $P(X,Y)$: Joint distribution of gene expression of two genes $X$ and $Y$.

<v-clicks depth="1">

- Mutual Information (MI)
  $$I(X,Y) = \sum_{x \in X} \sum_{y \in Y} p(x,y) \log \left( \frac{p(x,y)}{p(x)p(y)} \right)$$
</v-clicks>

<v-click>

::admonition{kind="warning" title="Assumption" icon="mdi:info"}
**Number of values a random variable can take is constant**
::

</v-click>


<!--
1. Discrete random variables representing genes
2. Joint distribution
2. Describe MI : 
   - dependence
   - reduces uncertainty
   - usually in terms of conditional entropy 
   - joint distributions
-->

---
transition: fade-out
layout: none
clicks: 4
---

<SpecificSpecificInfo auto-start class="absolute inset-0" />

<!--
1. Specific Information: state-dependent information 
2. "how did the uncertainty about X change upon learning Y=y?"

Source: https://www.eneuro.org/content/5/3/ENEURO.0052-18.2018.long

A Tutorial for Information Theory in Neuroscience
by Nicholas M. Timme and Christopher Lapish
-->

---
transition: fade-out
layout: none
clicks: 6
---

<Redundancy auto-start class="absolute inset-0" />

<!--
1. "what portion of Y is provided redundantly by both X and Z (what information overlap about Y exists between X and Z), "
2. "uniquely by X or Z alone (what information does X provide about Y that Z does not and vice versa)"
3. Redundancy in terms of the average of the min.
4. Make sure to emphasize the decomposition


If all of the information in I((X,Z), Y) is provided redundantly, then we know X and Z are doing the same thing, at least in an information theoretic sense. If all of the information in I((X,Z), Y) is provided uniquely by X, then we know Z is not providing information about Y
-->

---
transition: fade-out
layout: none
clicks: 5
---

<XyzpucPUC auto-start class="absolute inset-0" />

<!--
1.a "what portion of Y is provided redundantly by both X and Z (what information overlap about Y exists between X and Z), "
1.b "what portion of X is provided redundantly by both Y and Z (what information overlap about X exists between Y and Z), "

2a. "uniquely by X or Z alone (what information does X provide about Y that Z does not and vice versa)"
2a. "uniquely by Y or Z alone (what information does Y provide about Z that Z does not and vice versa)"
-->

---
transition: fade-out
---

# Bottleneck in PUC Computation

<v-click>

PUC, $\gamma(X, Y)$, can be simplified as below:
  $$
  \begin{aligned}
  \gamma(X, Y) &=  \frac{1}{I(X, Y)} \sum_{Z \not\in \{X, Y\}} \nu((X, Z); Y) + \nu((Y, Z); X)\\
   &= \frac{1}{I(X, Y)} \sum_{Z \not\in \{X, Y\}} 2I(X, Y) - \rho((X, Z); Y) - \rho((Y, Z); X) \\
   &= \frac{1}{I(X, Y)} \left( 2(n-2) I(X, Y) - \sum_{Z \not\in \{X, Y\}} \rho((X, Z); Y) - \sum_{Z\not\in \{X, Y\}} \rho((Y, Z); X) \right)
  \end{aligned}
  $$
  
</v-click>

<v-click>

::admonition{kind="danger" title="Computation Bottleneck" icon="mdi:info"}
$$
\sum_{Z \not \in \{X, Y\}} \rho((X, Z); Y)   \textrm{ \& } \sum_{Z \not \in \{X, Y\}} \rho((Y, Z); X)
$$
::

</v-click>


---
transition: fade-out
layout: none
clicks: 13
---

<InsightAlgoInsight auto-start class="absolute inset-0" />

<!--
1. Substitute
2. inner sum over values Y can take, outer sum over of possible values for Z
3. Visualize as n-2 table comparisons
4. Each table
-->

---
transition: fade-out
---

# Sequential Algorithm

|     | Given: $P(X), \forall X \in \mathcal{X}$; $P(X, Y),\forall (X, Y)$                         |                   |
| --- | ------------------------------------------------------------------------------------------ | ----------------- |
| 1   | Compute Mutual Information, $I(X,Y)$ and tables $\mu(y; X), \forall (y, X)$                | $O(n^2)$          |
| 2   | Compute $\mathbf{S}_y$, sorted $\mu(y; X)$ tables $\forall (y, X)$                         | $O(n^2 \log n)$   |
|     | Compute $\mathbf{P}_y$, prefix sum table for all $\mathbf{S}_y$ tables                     | $O(n^2)$          |
| 3   | $\forall (X,Y)$, Compute (a) $\sum_Z\rho((X,Z); Y)$, (b)$\sum_Z\rho((Y,Z); X)$             | $O(n^2)$          |
| 4   | $\forall (X,Y)$, Compute PUC                                                               | $O(n^2)$          |


<v-click>

::admonition{kind="warning" title="PUC Network Construction" icon="mdi:info"}
PUC Network of $n$ genes can be constructed in $O(n^2 \log n)$ time.
::

</v-click>


---
transition: fade-out
layout: none
clicks: 6
---

<ParInsightParAlgoInsight auto-start class="absolute inset-0" />

<!--
Update Header;
p processes
-->

---
transition: fade-out
---

# Parallel Algorithm

|     | Given $\mathbf{S}, \mathbf{P}, \mathbf{Q}, \mathbf{R}$, flat arrays of size $n \sum_{Y \in \mathcal{X}}  \|Y\|$,  distributed across $p$ processes    |                                       |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
|     | Let $j \gets$ processor's rank                                                                                                                        |                                       |
| 1   | Insert $\langle Y, X, y, s_{\mu}, p_{\mu}  \rangle$ to $\mathsf{puc}\textrm{-}\mathsf{tuples}^{(j)}$ for each entry in $\mathbf{S}^{(j)}, \mathbf{P}^{(j)}, \mathbf{Q}^{(j)}, \mathbf{R}^{(j)}$        | $O(n^2/p)$                            |
| 2   | Insert $\langle Y, X, I(X, Y) \rangle$ to $\mathsf{puc}\textrm{-}\mathsf{tuples}^{(j)}$                                                               | $O(n^2/p)$                            |
| 3   | Sort in parallel the distributed $\mathsf{puc}\textrm{-}\mathsf{tuples}$                                                                              | $\mathsf{T}_{\mathtt{sort}}(n^2, p))$ |
| 4   | Compute PUC from sorted $\mathsf{puc}\textrm{-}\mathsf{tuples}^{(j)}$                                                                                       | $O(n^2/p)$                            |


<v-click>

::admonition{kind="warning" title="PUC Network Construction" icon="mdi:info"}
PUC Network of $n$ genes can be constructed with $p$ processes in $O(n^2/p) + \mathsf{T}_{\mathtt{sort}}(n^2, p))$ time.
::

</v-click>


---
transition: fade-out
---

## Implementation: Platform and Data Processing

<v-clicks depth="1">

- _Chan et. al. (2017)_ PIDC implementation in `julia`
  - Modified I/O:  Read input data from `HDF5` files (`anndata` spec.) instead of `csv`.
- Our Implementation: MPI in `Rust`
  - `rsmpi` : MPI 3.1 wrapper (Experiments use `OpenMPI`).
  - `sope` : Convenience MPI library features include generic struct types, sorting etc.
  - `hdf5-rs` : Updated for MPI parallel I/O.
- $P(X)$ computation: `BayesianBlocks` histogram method for $n/p$ genes per process and broadcast to all processes.
- $P(X, Y)$, $\mu(y; X)$ and $\mu(x; Y)$ computation : $\binom{n}{2}/p$ pairs per processes.

</v-clicks>

---
transition: fade-out
layout: two-cols-header
---

## Scaling vs. sequential algorithm and current PIDC

::left::

<v-click>

- **Setup:** 72-core Intel® Xeon® E7-8870 2.7 GHz CPU with 1 TB shared memory.
- **Dataset:** Human PBMC, $m=23,766 ; n= 5,000$.
</v-click>

<v-click>

- **Key Takeaways:**
  - Max. speedup of 52 on 64 cores w.r.t. our sequential algorithm.
  - 158X times faster than PIDC, runtime reduced from $10.8$ hours to $\approx4$ min.
  - Communication and I/O times are a small fraction ($<12$% on 64 cores).
</v-click>

::right::

##### Speedup vs. number of cores (Novel sequential algorithm for $p=1$)

![](/img/strong-scaling-small-ai.svg){width=700px lazy}

---
transition: fade-out
layout: none
clicks: 9
---

<DataB auto-start class="absolute inset-0" />

<!--
1. Each pair two rows
2. Represent the computation as upper triangular matrix
3. Reduce memory foot print via block wise work decomposition and processing in batches
4. Blocks and corresponding rows
5. Parallel reading/writing of contiguous data non-overlapping data
-->

---
transition: fade-out
---

# Results : Scaling to Human-genome

<v-clicks depth=1>

- Integrated human gene expression datasets include up to 30K genes at the genome-scale.
- **Setup:** Distributed cluster with 24-core Intel® Xeon® 6226 2.7 GHz processor/node (Used 16 cores/node).
- **Dataset:**  794,170 cells and 30,000 genes (Total size of $P(X,Y)$ is 19.1TB).
- **Key Takeaways:**
   -  $\approx$ 4.1 hours and $\approx$ 2.5 hours, respectively, with 1, 024 cores and 2, 048 cores.
   - Construction of $P(X), P(X,Y)$ and $\mu(y; X)$ dominates the runtime.
   - $\mu(y;X) \rightarrow \gamma(\cdot, \cdot)$ time is less than 1% of the total runtime.
</v-clicks>

<v-click>

::admonition{kind="warning" title="Observation" icon="mdi:info"}
**With our improved PIDC algorithm,  computing histograms dominates runtime.**
::
</v-click>

<!--
Months
-->

---
transition: fade-out
---
# Conclusions and Future Work

- Novel $O(n^2 \log n)$ sequential algorithm and  $O(n^2/p + \mathsf{T}_{\mathtt{sort}}(n^2, p))$ distributed parallel algorithm.
- To our knowledge, the 30K network is the largest network covering the complete human genome.
- Future work
  - Address the cases where the gene expression values need to be treated as continuous.
  - I/O scalability via asynchronous read/writes.
  - Improve scalability histogram computations.


<v-click>

::admonition{kind="gt" title="Acknowledgements" icon="mdi:info"}
Supported in part by the U.S. National Science Foundation under DBI-2233887
::

</v-click>


---
transition: fade-out
layout: intro
---
# Q & A


---
transition: fade-out
layout: intro
---
# Additional Slides


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
---

# Results : Dataset $D2$

| ![](/img/strong-scaling-big-ai.svg){width=400px lazy} | ![](/img/runtime-stacked-ai.svg){width=520px lazy} |
| ----------------------------------------------------- | -------------------------------------------------- |

- Distributed cluster: 24-core Intel® Xeon® 6226 2.7 GHz processor/node.
- Max speedup of speedup of 96 with 512 cores, which then drops to 55 with 1, 024 cores


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


---
transition: fade-out
layout: two-cols-header
---

# Results : Scaling on a distributed cluster

::left::

- **Setup:** Distributed cluster: 24-core Intel® Xeon® 6226 2.7 GHz processor/node.
- **Dataset:** Human Lung Cancer dataset, $m=$ 91,068; $n=$ 5,000 
- **Speedup:** Max speedup of 96 on 512 cores, then drops to 55 with 1,024 cores.
  - Lack of scaling in communication and I/O time. 
  - Work per process gets comparatively meager (Only 28.26 when $p = 1024$).

::right::

##### Speedup vs. number of cores

![](/img/strong-scaling-big-ai.svg){width=400px lazy}

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
