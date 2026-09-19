# DeepSpot-H quickstart

**Turn an H&E image into embeddings on your own machine. The slide stays there.**

DeepSpot-H is the foundation model for H&E images. It turns each tile of your
slide into one embedding. This repository is a notebook that runs it end to
end: it fetches one published slide, cuts the tiles the model reads, computes
an embedding for each of them and writes one file. No image is uploaded at any
point, and the notebook prints exactly what the file it wrote contains.

That file is also the input to the second half, which predicts spatial gene
expression from those embeddings and runs on our service:
[**deepspot-m-quickstart**](https://github.com/auroraomics/deepspot-m-quickstart).
This repository stops at the embeddings on purpose. Stopping there is a
complete result for anyone who wanted the numbers, and it is the decision point
for everyone else.

- Product: <https://auroraomics.org>
- Documentation: <https://docs.auroraomics.org>

## Who this is for

Someone with a slide and a reason it cannot be uploaded: an ethics approval
that keeps it in place, an institutional policy, a file too large to move, or a
data-governance review that has to be able to open whatever does leave and read
it. If none of that applies to you, sending the tiles is fewer steps and the
[quickstart](https://docs.auroraomics.org/quickstart/) is the shorter path.

Analysis is for academic and non-profit research. Commercial evaluation and use
run under a separate written agreement: <https://auroraomics.org/contact>.

## What leaves your machine

This is the point of the repository, so it is a table rather than a paragraph.

| Step | What leaves | What stays |
|---|---|---|
| Fetching the example slide | nothing of yours | — |
| Reading the slide, cutting tiles, judging them | nothing | the image, its label, its file metadata |
| Asking which model and which encoder | your API key, and nothing about the slide | everything about the slide |
| Fetching the pinned weights, on the first run only | nothing of yours | — |
| Running DeepSpot-H | nothing | the image, and every tile cut from it |
| **Total, for this notebook** | **no image, and nothing derived from one** | **the slide** |
| If you continue to the second half | the embeddings file, and only that | the image |

The embeddings file carries three things per tile: the embedding, the tile's
centre on the slide, and the quality measurements that kept it. No tile, no
overview image, no slide label, no scanner metadata. The last cell of the
notebook opens the file and lists what is in it, so the claim is checked rather
than believed.

These numbers are derived from the image. Partial reconstruction of image
content from them is a known research capability. Aurora attempts none and has
no path to your pixels. [Privacy and
retention](https://docs.auroraomics.org/privacy/) is the full statement.

## What you need

| | |
|---|---|
| Python | 3.10 or newer |
| Package | `auroraomics`, with the `embed` extra |
| Hardware | a CPU is enough; a GPU is used when there is one |
| API key | yes, for two calls that send nothing about your slide |
| Disk | about 300 MB for the example slide |
| Network | about 210 MB to fetch it |

**Why a key at all, on the route where nothing is uploaded.** Two of the
notebook's calls read the service: which model you intend to submit to, and
which encoder it was served with. Those two answers are what make your
embeddings comparable with anyone else's, and computing them against the wrong
encoder produces a file that looks right and means something different. Both
calls send your key and nothing else. [Get a
key](https://docs.auroraomics.org/get-access/) explains how one is granted; a
request is reviewed by a person, so ask before you need it.

## Run it

```bash
git clone https://github.com/auroraomics/deepspot-h-quickstart.git
cd deepspot-h-quickstart
pip install -r requirements.txt
auroraomics login you@institution.edu
jupyter lab notebooks/01-tiles-and-embeddings.ipynb
```

On a machine with no GPU, ask for the CPU build of the tensor runtime as well,
which is several gigabytes smaller:

```bash
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
```

Then run the cells top to bottom. The notebook is a straight line:

1. fetch one published slide, without downloading the archive it sits in
2. open it and read its resolution out of the file
3. ask the service what the model reads and which encoder it was served with
4. look at where the tiles fall and which ones are kept
5. run DeepSpot-H over them and write the embeddings file
6. open that file and check what it holds
7. see the tissue in the embeddings

Step 5 is the only slow one. It walks the tiles one batch at a time and reports
what it kept. Before committing to a whole slide, `auroraomics doctor --model
<id> --tiles <n>` times a single pass on your own machine and multiplies it out,
so you read the hours first rather than discovering them.

## Your own slide

Replace one path and one line. The notebook opens the example with
`ao.open_slide(path)`, which reads the resolution out of the file and refuses to
open a file that records none; `ao.open_slide(path, mpp=...)` is how you say so
yourself. Everything after that is unchanged. Pyramidal formats a scanner writes
are read a window at a time, so the slide never has to fit in memory.

The tile is a physical size in micrometres, not a pixel count, which is what
makes a tile cut from a 0.25 µm/px scan and one from a 0.5 µm/px scan the same
measurement. The notebook takes that size from the model's own card and the
resolution from your slide, and the package divides one by the other. No number
in the notebook is typed from memory.

## Then what

The embeddings file is a complete result on its own: one row per tile, with the
position each row came from. Cluster it, retrieve against it, or train on it.

To go on to spatial gene expression, submit that file to
[**deepspot-m-quickstart**](https://github.com/auroraomics/deepspot-m-quickstart),
which picks it up where this notebook leaves off. DeepSpot-M turns those
embeddings into spatial gene expression, and it runs on our service on both
routes.

## The example slide

One lung-cancer section from an open-access Visium dataset:

> Dawo, S., Nonchev, K., and Silina, K. (2025). *10x Visium Spatial
> Transcriptomics Dataset: Kidney (3) and Lung (5) Cancer with Tertiary
> Lymphoid Structures*. Zenodo. <https://doi.org/10.5281/zenodo.14620362>

Published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You
may use it, including commercially, as long as you credit the authors above.

It is published inside a two-gigabyte archive of eight slides and their assays,
and the notebook needs one of them. It reads the archive's own member directory
over the network, then pulls that one member out by its byte span and inflates
it as it arrives: five requests, about 210 MB, and the member's own checksum is
verified before the file is written. `notebooks/example_slide.py` is that code,
and it is not specific to Aurora.

## Licence

The example code in this repository is MIT, in `LICENSE`. Lift any of it.

The `auroraomics` package it calls is published under its own separate licence,
which is not MIT and not permissive. Read it before you build on the package:
<https://docs.auroraomics.org/quickstart/>. Model weights carry their own
separate terms, which the model's card names.

## Where to look next

| | |
|---|---|
| What DeepSpot-H is | <https://docs.auroraomics.org/models/deepspot-h/> |
| The route this repository takes | <https://docs.auroraomics.org/guides/embeddings/> |
| Cutting and checking tiles | <https://docs.auroraomics.org/check-tiles/> |
| Getting a key | <https://docs.auroraomics.org/get-access/> |
| Quotas and size caps | <https://docs.auroraomics.org/limits/> |
| What a result file holds | <https://docs.auroraomics.org/results/> |
| One real slide, end to end | <https://docs.auroraomics.org/examples/whole-slide/> |
