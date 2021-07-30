[![nlpsandbox.io](https://nlpsandbox.github.io/nlpsandbox-themes/banner/Banner@3x.png)](https://nlpsandbox.io)

# Spark NLP-based NLP Sandbox PHI Annotator

[![GitHub Release](https://img.shields.io/github/release/nlpsandbox/phi-annotator-spark-nlp.svg?include_prereleases&color=94398d&labelColor=555555&logoColor=ffffff&style=for-the-badge&logo=github)](https://github.com/nlpsandbox/phi-annotator-spark-nlp/releases)
[![GitHub CI](https://img.shields.io/github/workflow/status/nlpsandbox/phi-annotator-spark-nlp/CI.svg?color=94398d&labelColor=555555&logoColor=ffffff&style=for-the-badge&logo=github)](https://github.com/nlpsandbox/phi-annotator-spark-nlp/actions)
[![GitHub License](https://img.shields.io/github/license/nlpsandbox/phi-annotator-spark-nlp.svg?color=94398d&labelColor=555555&logoColor=ffffff&style=for-the-badge&logo=github)](https://github.com/nlpsandbox/phi-annotator-spark-nlp/blob/main/LICENSE)
[![Docker](https://img.shields.io/badge/docker-blue.svg?color=94398d&labelColor=555555&logoColor=ffffff&style=for-the-badge&label=nlpsandbox&logo=data:image/svg%2bxml;base64,PHN2ZyByb2xlPSJpbWciIHZpZXdCb3g9IjAgMCAyNCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJtMy4yIDcuOS0xLjctMXYxMS40bDkuOSA1LjdWMTIuNkw1LjYgOS4zIDMuMiA3Ljl6bTE3LjEtMS4zIDEuNS0uOUwxMiAwIDIuMiA1LjdsMi42IDEuNS4xLjEgMS43IDEgNS41IDMuMiA1LjEtMyAzLjEtMS45ek0xMiA5LjUgOS4zIDcuOSA3LjQgNi44bC0xLjctMS0uMS0uMWgtLjFMMTIgMS45bDYuNSAzLjhMMTYuMyA3IDEyIDkuNXptOC44LTEuNi0yLjQgMS40LS41LjItNS4zIDMuMVYyNGw5LjktNS43VjYuOWwtMS43IDF6IiBmaWxsPSIjZmZmIi8+PC9zdmc+)](https://www.synapse.org/#!Synapse:syn26015391 "Get the Docker image of this tool on NLPSandbox.io")
[![Leaderboard](https://img.shields.io/badge/leaderboard-blue.svg?color=94398d&labelColor=555555&logoColor=ffffff&style=for-the-badge&label=nlpsandbox&logo=data:image/svg%2bxml;base64,PHN2ZyByb2xlPSJpbWciIHZpZXdCb3g9IjAgMCAyNCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJtMy4yIDcuOS0xLjctMXYxMS40bDkuOSA1LjdWMTIuNkw1LjYgOS4zIDMuMiA3Ljl6bTE3LjEtMS4zIDEuNS0uOUwxMiAwIDIuMiA1LjdsMi42IDEuNS4xLjEgMS43IDEgNS41IDMuMiA1LjEtMyAzLjEtMS45ek0xMiA5LjUgOS4zIDcuOSA3LjQgNi44bC0xLjctMS0uMS0uMWgtLjFMMTIgMS45bDYuNSAzLjhMMTYuMyA3IDEyIDkuNXptOC44LTEuNi0yLjQgMS40LS41LjItNS4zIDMuMVYyNGw5LjktNS43VjYuOWwtMS43IDF6IiBmaWxsPSIjZmZmIi8+PC9zdmc+)](https://www.synapse.org/#!Synapse:syn22277123/wiki/608544 "View the performance of this tool on NLPSandbox.io")
[![Discord](https://img.shields.io/discord/770484164393828373.svg?color=94398d&labelColor=555555&logoColor=ffffff&style=for-the-badge&label=Discord&logo=discord)](https://nlpsandbox.io/discord "Realtime support / chat with the community and the team")

## Introduction

[NLPSandbox.io] is an open platform for benchmarking modular natural language
processing (NLP) tools on both public and private datasets. Academics, students,
and industry professionals are invited to browse the available tasks and
participate by developing and submitting an NLP Sandbox tool.

This repository provides an example implementation of the [NLP Sandbox PHI
Annotator API] written in Python-Flask. An NLP Sandbox PHI annotator takes as
input a clinical note (text) and outputs a list of predicted PHI annotations
found in the clinical note. Here PHIs are identified using regular expressions.

This NLP Sandbox tool uses a model from [Spark NLP] to annotate PHI in clinical
notes. Because NLP Sandbox tools must run without access to internet connection,
this implementation install and configure Spark NLP to run offline.


## Contents

- [Specification](#Specification)
- [Requirements](#Requirements)
- [Usage](#Usage)
  - [Creating the configuration file](#Creating-the-configuration-file)
  - [Running with Docker](#Running-with-Docker)
  - [Running with Python](#Running-with-Python)
  - [Accessing this NLP Sandbox tool User
    Interface](#Accessing-this-NLP-Sandbox-tool-User-Interface)
- [Development](#Development)
  - [Configuring your GitHub repository](#Configuring-your-GitHub-repository)
- [Versioning](#Versioning)
  - [GitHub release tags](#GitHub-release-tags)
  - [Docker image tags](#Docker-image-tags)
- [Benchmarking on NLPSandbox&#46;io](#Benchmarking-on-NLPSandbox&#46;io)
- [Contributing](#Contributing)
- [License](#License)


## Specification

- NLP Sandbox schemas version: 1.2.0
- NLP Sandbox tool version: 0.1.0
- Docker image: [docker.synapse.org/syn22277124/phi-annotator-spark-nlp]
- Apache Spark version: 3.1.1
- Spark NLP version: 3.1.1
- Models
  - NER: [ner_deid_large] (en, 2.5.3_2.4_1595427435246)
  - Embeddings: [embeddings_clinical] (en, 2.4.0_2.4_1580237286004)

> Note: The Docker image includes models from [Spark NLP for Healthcare] that
> requires a trial or paid subscription. Therefore the Docker image cannot be
> made publicly available.


## Requirements

- [Docker Engine] >=19.03.0


## Usage

### Creating the configuration file

Create the configuration file and update the configuration values.

```console
cp .env.example .env
```

### Running with Docker

The command below starts this NLP Sandbox PHI annotator locally.

```console
docker compose up --build
```

You can stop the container run with `Ctrl+C`, followed by `docker compose down`.

### Running with Python

Install [Apache Spark] and [Spark NLP] on your system. The Dockerfile included
with this project shows how to install them on a Debian-based distribution.

Create a Conda environment.

```console
conda create --name phi-annotator-spark-nlp python=3.9 -y
conda activate phi-annotator-spark-nlp
```

Install and start this NLP Sandbox PHI annotator.

```console
cd server && pip install -r requirements.txt
python -m openapi_server
```

### Accessing this NLP Sandbox tool User Interface

This NLP Sandbox tool provides a web interface that you can use to annotate
clinical notes. This web client has been automatically generated by
[openapi-generator]. To access the UI, open a new tab in your browser and
navigate to one of the following address depending on whether you are running
the tool using Docker (production) or Python (development).

- Using Docker: http://localhost/ui
- Using Python: http://localhost:8080/ui


## Development

Interested in creating your own NLP Sandbox tool based on this implementation?
Start by creating a new GitHub repository based on [this GitHub template].

This NLP Sandbox tool is based on the [NLP Sandbox PHI Annotator example].
Please refer to the *Development* section of this example tool for general
information on how to develop an NLP Sandbox tool. The sections listed below
provide additional information about the present tool.

### Configuring your GitHub repository

After creating your GitHub repository based on this [this GitHub template], you
must update your project to enable the CI/CD workflow to automatically build and
push your tool as a Docker image to [Synapse], then enabling you to submit your
tool to [NLPSandbox.io].

1. Update the CI/CD workflow file `.github/workflows/ci.yml`
   - Update the environment variable `docker_repository`
2. Add the following [GitHub Secrets] to your repository

    Name | Description
    -----|------------
    `SPARK_LICENSE_SECRET` | Your Spark NLP license secret.
    `SPARK_AWS_ACCESS_KEY_ID` | Your Spark NLP AWS access key ID.
    `SPARK_AWS_SECRET_ACCESS_KEY` | Your Spark NLP AWS secret access key.
    `SYNAPSE_USERNAME` | Your Synapse username.
    `SYNAPSE_TOKEN` | A [Synapse personal access token] for your Synapse account.

> Note: The trial version of Spark NLP works only with a specific version of
> Spark NLP. If your license is for a more recent version of Spark NLP, you will
> need to update the Spark NLP version in the files of this project:
> `Dockerfile`, `.github/workflows/ci.yml`.


## Versioning

### GitHub release tags

This repository uses [semantic versioning] to track the releases of this tool.
This repository uses "non-moving" GitHub tags, that is, a tag will always point
to the same git commit once it has been created.

### Docker image tags

The artifact published by the [CI/CD workflow] of this GitHub repository is a
Docker image pushed to the Synapse Docker Registry. This table lists the image
tags pushed to the registry.

| Tag name                    | Moving | Description
|-----------------------------|--------|------------
| `latest`                    | Yes    | Latest stable release.
| `edge`                      | Yes    | Latest commit made to the default branch.
| `edge-<sha>`                | No     | Same as above with the reference to the git commit.
| `<major>.<minor>.<patch>`   | No     | Stable release.

You should avoid using a moving tag like `latest` when deploying containers in
production, because this makes it hard to track which version of the image is
running and hard to roll back.


## Benchmarking on NLPSandbox&#46;io

Visit [nlpsandbox.io] for instructions on how to submit your NLP Sandbox tool
and evaluate its performance.


## Contributing

Thinking about contributing to this project? Get started by reading our
[contribution guide].


## License

[Apache License 2.0]

<!-- Links -->

[nlpsandbox.io]: https://www.synapse.org/nlpsandbox
[docker.synapse.org/syn22277124/phi-annotator-spark-nlp]: https://www.synapse.org/#!Synapse:syn26015391
[Synapse.org]: https://synapse.org
[Docker Engine]: https://docs.docker.com/engine/install/
[Apache License 2.0]: https://github.com/nlpsandbox/phi-annotator-spark-nlp/blob/main/LICENSE
[semantic versioning]: https://semver.org/
[contribution guide]: https://github.com/nlpsandbox/phi-annotator-spark-nlp/blob/main/.github/CONTRIBUTING.md
[CI/CD workflow]: https://github.com/nlpsandbox/phi-annotator-spark-nlp/blob/main/.github/workflows/ci.yml
[openapi-generator]: https://github.com/OpenAPITools/openapi-generator
[NLP Sandbox PHI Annotator API]: https://nlpsandbox.github.io/nlpsandbox-schemas/phi-annotator/latest/docs/

[Apache Spark]: https://spark.apache.org/
[Spark NLP]: https://nlp.johnsnowlabs.com/
[Spark NLP for Healthcare]: https://www.johnsnowlabs.com/spark-nlp-health/
[ner_deid_large]: https://nlp.johnsnowlabs.com/2020/07/22/ner_deid_large_en.html
[embeddings_clinical]: https://nlp.johnsnowlabs.com/2020/01/28/embeddings_clinical_en.html
[NLP Sandbox PHI Annotator example]: https://github.com/nlpsandbox/phi-annotator-example
[this GitHub template]: https://github.com/nlpsandbox/phi-annotator-spark-nlp/generate
[GitHub Secrets]: https://docs.github.com/en/actions/reference/encrypted-secrets
[Synapse personal access token]: https://www.synapse.org/#!Synapse:syn22277123/wiki/609139
