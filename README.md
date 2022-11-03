# ebd_table_to_graph

![Unittests status badge](https://github.com/Hochfrequenz/ebd_table_to_graph/workflows/Unittests/badge.svg)
![Coverage status badge](https://github.com/Hochfrequenz/ebd_table_to_graph/workflows/Coverage/badge.svg)
![Linting status badge](https://github.com/Hochfrequenz/ebd_table_to_graph/workflows/Linting/badge.svg)
![Black status badge](https://github.com/Hochfrequenz/ebd_table_to_graph/workflows/Black/badge.svg)
![PyPi Status Badge](https://img.shields.io/pypi/v/ebd_table_to_graph)

This repository contains the source code of the Python package `ebd_table_to_graph`.

## Rationale

Assume, that you scraped the Entscheidungsbaumdiagramm tables by EDI@Energy from their somewhat "digitized" PDF/DOCX files.
Also assume, that the result of your scraping is a [`ebd_table_to_graph.models.EbdTable`](src/ebd_table_to_graph/models/ebd_table.py).

The package `ebd_table_to_graph` contains logic to convert your scraped data into a graph.
This graph can then be exported e.g. as UML.

## How to use this Repository on Your Machine (for development)

Please follow the instructions in
our [Python Template Repository](https://github.com/Hochfrequenz/python_template_repository#how-to-use-this-repository-on-your-machine)
. And for further information, see the [Tox Repository](https://github.com/tox-dev/tox).

## Contribute

You are very welcome to contribute to this template repository by opening a pull request against the main branch.
