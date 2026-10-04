# DeepSpot-H quickstart

**Your slides stay with you.**

Analyse sensitive tissue while your images stay within your environment. This
notebook prepares an H&E slide on your own machine with DeepSpot-H, the
foundation model for H&E images, which turns each tile of your slide into one
embedding. No image is uploaded.

Aurora predicts spatial gene expression from routine H&E images, helping
researchers explore molecular patterns across samples, cohorts and disease.
DeepSpot-M, the model that predicts spatial gene expression, reads the file this
notebook writes, and
[**deepspot-m-quickstart**](https://github.com/auroraomics/deepspot-m-quickstart)
continues from it.

- [Aurora](https://auroraomics.org)
- [Aurora Docs](https://docs.auroraomics.org)

## What you get

- Your slide prepared where it is: cut into tiles, and every tile checked, on
  your own machine.
- One embeddings file: for each tile, its embedding, its position on the slide
  and the quality measurements that kept it. There is no tile, no thumbnail, no
  slide label and no macro image in it.
- A first look at the tissue in those embeddings.

It suits the slides that stay where they are: the ones an ethics approval keeps
in place, the ones an institutional policy holds, and the ones too large to
move. To send a slide without writing code, upload it on the website with
[Aurora Direct](https://auroraomics.org/upload).

Analysis is for academic and non-profit research. Commercial evaluation and use
are governed by a written agreement with Aurora.
[Discuss commercial access](https://auroraomics.org/contact).

## Run it

You need Python 3.10 or newer and an API key. Your key lets the package ask the
service which release of the weights to use, so every machine computes the same
numbers. Access is granted per account, so ask before you need it:
[Get access](https://docs.auroraomics.org/get-access/).

It runs on a CPU. A GPU is used when there is one.

```bash
git clone https://github.com/auroraomics/deepspot-h-quickstart.git
cd deepspot-h-quickstart
pip install -r requirements.txt
auroraomics login you@institution.edu
jupyter lab notebooks/01-tiles-and-embeddings.ipynb
```

On a machine with no GPU, ask for the CPU build as well:

```bash
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
```

Run the cells top to bottom:

1. Fetch an example slide
2. Open the slide
3. Ask the service what to use
4. Check the tiles
5. Run DeepSpot-H
6. Check what the file holds
7. Explore the embeddings

## Your own slide

Point `SLIDE` at your file and delete the line that fetches the example.
`ao.open_slide` reads the resolution from the file. If your file records none,
pass it with `ao.open_slide(path, mpp=...)`. Everything after that is
unchanged.

## Next

To predict spatial gene expression from your embeddings, continue with
[**deepspot-m-quickstart**](https://github.com/auroraomics/deepspot-m-quickstart).
DeepSpot-M turns those embeddings into spatial gene expression on our service,
and no image is sent.

| | |
|---|---|
| [DeepSpot-H](https://docs.auroraomics.org/models/deepspot-h/) | The foundation model for H&E images |
| [Your slides stay with you](https://docs.auroraomics.org/guides/embeddings/) | This route in the docs |
| [Check tile quality](https://docs.auroraomics.org/check-tiles/) | Why a tile was dropped |
| [What you get back](https://docs.auroraomics.org/results/) | The result of a prediction |
| [Your data, your workflow](https://docs.auroraomics.org/privacy/) | Where your data goes |

## The example slide

One lung cancer section, `LC1`, from an open-access dataset:

> Dawo, S., Nonchev, K., & Silina, K. (2025). *10x Visium Spatial
> Transcriptomics Dataset: Kidney (3) and Lung (5) Cancer with Tertiary
> Lymphoid Structures* [Data set]. Zenodo.
> <https://doi.org/10.5281/zenodo.14620362>

`notebooks/example_slide.py` fetches that one slide without downloading the
whole archive.

## Licence

The code in this repository is MIT licensed, in [`LICENSE`](LICENSE). The
`auroraomics` package carries its own licence.
