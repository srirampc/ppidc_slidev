---
# try also 'default' to start simple
theme: ext/slidev-theme-spc-gt
# addons, can be a list of package names or local paths
# Learn more: https://sli.dev/guide/theme-addon.html#use-addon
addons: []
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
duration: 3min
presenterName: Sriram Chockalingam 
affiliation: Georgia Institute of Technology
mdc: true
# Fonts
fonts:
  sans: Concourse T3
  local: Concourse T3
---


## A Parallel Algorithm for the Construction of Partial Information Decomposition-based Genome-scale Networks from Single-Cell Datasets 

####   _**SC '26 @ Chicago, USA**_

<template #extra>

Joint work with [Maneesha Aluru](#) and [Srinivas Aluru](#)

</template>

---
transition: fade-out
layout: two-cols-header
image:  /img/Network_Construction.svg
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
clicks: 10
---
## Gene Network from Data
<AllpairsMINet auto-start />


---
transition: fade-out
---
# Contributions

<v-clicks depth="2">

- **PIDC**, a partial-information decomposition (PID) based network construction method
  - Effective for single-cell datasets.
  - Takes $O(n)$ time for each pair, and hence $O(n^3)$ time for $\binom{n}{2}$ pairs.

- Our Contributions
  - A novel $O(n^2 \log n)$ sequential algorithm, a factor of $n/\log n$ improvement.
  - Distributed-memory parallelization that takes $O(n^2/p + \mathsf{T}_{\mathtt{sort}}(n^2, p))$ time. 
  - Achieves $158$X speedup over the existing PIDC implementation.
  - Scaling to Human Genome: $30,000$-gene network from $\approx800$K cells in $2.5$ hours using $2,048$ cores.

</v-clicks>
