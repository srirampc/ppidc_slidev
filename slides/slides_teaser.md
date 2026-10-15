---
# try also 'default' to start simple
theme: ext/slidev-theme-spc-gt
# addons, can be a list of package names or local paths
# Learn more: https://sli.dev/guide/theme-addon.html#use-addon
addons: []
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
duration: 35min
presenterName: Sriram, A, and B
affiliation: Georgia Institute of Technology
mdc: true
---

# A _**Somewhat Long Title**_ for a Math Talk or Lecture

### Some Subtitle, Maybe Software | _**Conference**_ @ Place, Country

<template #extra>

Extra content: Joint work with [Maneesha Aluru](#) and [Srinivas Aluru](#)

</template>

---
transition: fade-out
clicks: 21
---

# Example Animation

<AllpairsMINet auto-start />

---
transition: fade-out
clicks: 3
---
# Transpose Xform

<TransposeDataT auto-start />


---

# Powered by _**Slidev**_

Slidev is a slide maker and <span v-mark.yellow>presentation tool</span> designed for developers.

This theme, leaning on the CD of the University of Graz, has been created by [Benjamin Hackl](https://benjamin-hackl.at).

<div v-click>

To start a new presentation, simply start a new file `slides.md`
with a bit of content like

</div>
<div v-click="3">

```md {none|1-5|all}{lines: true, at: '+1'}
---
theme: path/to/slidev-theme-behackl-kfu
presenterName: Benjamin Hackl
affiliation: Department of Mathematics and Scientific Computing / University of Graz
---

# Fancy Main Title

### With Some Subtitle

```
</div>
<div v-click>

Then startup the preview server using

```bash
$ npx slidev
```

</div>
