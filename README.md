# DeepSpot-H quickstart

**Keep your slides with you.**

Analyse sensitive tissue while your images stay within your environment. This
notebook prepares an H&E slide on your own machine with DeepSpot-H, the
foundation model for H&E images, so Aurora can predict its spatial gene
expression without any image leaving your machine.

Aurora predicts spatial gene expression from routine H&E images, helping
researchers explore molecular patterns across samples, cohorts and disease.

It suits the slides that have to stay where they are: the ones an ethics
approval or an institutional policy keeps in place, and the ones too large to
move.

## What you get

- Your slide prepared where it is, with every part of the tissue checked on your
  own machine.
- One file Aurora predicts from, with no image in it.
- A first look at the tissue's structure across the slide.

To predict and explore spatial gene expression from it, continue with
[deepspot-m-quickstart](https://github.com/auroraomics/deepspot-m-quickstart).

## Run it

```bash
git clone https://github.com/auroraomics/deepspot-h-quickstart.git
cd deepspot-h-quickstart
pip install -r requirements.txt
auroraomics login you@institution.edu
jupyter lab notebooks/01-tiles-and-embeddings.ipynb
```

You need access to Aurora API:
[get access](https://docs.auroraomics.org/get-access/). It runs on a laptop,
and uses a GPU when there is one.
[Your slides stay with you](https://docs.auroraomics.org/guides/embeddings/)
has the details, including a machine with no GPU.

To work on your own slide, point the notebook at your file.

Analysis is for academic and non-profit research. Commercial evaluation and use
are governed by a written agreement with Aurora.
[Discuss commercial access](https://auroraomics.org/contact).

## The example slide

One lung cancer section, `LC1`, from an open-access dataset:

> Dawo, S., Nonchev, K., & Silina, K. (2025). *10x Visium Spatial
> Transcriptomics Dataset: Kidney (3) and Lung (5) Cancer with Tertiary
> Lymphoid Structures* [Data set]. Zenodo.
> <https://doi.org/10.5281/zenodo.14620362>

## Learn more

- [DeepSpot-H](https://docs.auroraomics.org/models/deepspot-h/) and
  [your data, your workflow](https://docs.auroraomics.org/privacy/), in Aurora
  Docs.
- [deepspot-m-quickstart](https://github.com/auroraomics/deepspot-m-quickstart)
  continues from the file this notebook writes.
- [Aurora](https://auroraomics.org)

The code in this repository is open source: [LICENSE](LICENSE).
