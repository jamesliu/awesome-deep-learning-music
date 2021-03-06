# -*- coding: utf-8 -*-
#!/usr/bin/python
#
# Authors   Yann Bayle
# E-mails   bayle.yann@live.fr
# License   MIT
# Created   16/08/2017
# Updated   20/10/2017
# Version   1.0.0
#

"""
Description of dl4m.py
======================

Parse dl4m.bib to create a simple and readable ReadMe.md table.

..todo::
    sort bib
    add Fig for tasks, wordcloud, dataaugmentation
    bibtexparser accentuation handling in authors.md list
    error handling
    report on nb item per ENTRYTYPE
"""

import numpy as np
import matplotlib.pyplot as plt
import bibtexparser
from bibtexparser.bwriter import BibTexWriter


def write_bib(bib_database, filen="dl4m.bib"):
    """Description of write_bib
    Write the items stored in bib_database into filen
    """
    writer = BibTexWriter()
    writer.indent = '  '
    writer.order_entries_by = ('noneyear', "author")
    with open(filen, "w", encoding="utf-8") as bibfile:
        bibfile.write(writer.write(bib_database))


def read_bib(filen="dl4m.bib"):
    """Description of read_bib
    Parse a bib file and load it into memory in a python format
    """
    with open(filen, "r", encoding="utf-8") as bibtex_file:
        bibtex_str = bibtex_file.read()
    bib_database = bibtexparser.loads(bibtex_str)
    return bib_database


def load_bib(filen="dl4m.bib"):
    """Description of load_bib
    Load and return the items stored in filen
    """
    bib = read_bib(filen)
    write_bib(bib, filen)
    bib = read_bib(filen)
    return bib.entries


def articles_per_year(bib):
    """Description of main
    Display the number of articles published per year
    input: file name storing articles details
    """
    years = []
    for entry in bib:
        year = int(entry['year'])
        years.append(year)

    plt.xlabel('Years')
    plt.ylabel('Number of articles')
    year_bins = np.arange(min(years), max(years) + 2.0, 1.0)
    plt.hist(years, bins=year_bins, color="#401153", align="left")
    axe = plt.gca()
    axe.spines['right'].set_color('none')
    axe.spines['top'].set_color('none')
    axe.xaxis.set_ticks_position('bottom')
    axe.yaxis.set_ticks_position('left')
    fig_fn = "fig/articles_per_year.png"
    plt.savefig(fig_fn, dpi=200)
    print("Fig. with number of articles per year saved in", fig_fn)


def get_nb_articles(bib):
    """Description of get_nb_articles
    Count the number of articles in the database
    """
    print("There are", len(bib), "articles referenced.")
    return len(bib)


def get_authors(bib):
    """Description of get_authors
    Print in authors.md the alphabetical list of authors
    """
    authors = []
    for entry in bib:
        for author in entry['author'].split(" and "):
            authors.append(author)
    authors = sorted(set(authors))
    nb_authors = len(authors)
    print("There are", nb_authors, "researchers working on DL4M.")

    authors_fn = "authors.md"
    with open(authors_fn, "w", encoding="utf-8") as filep:
        filep.write("# List of authors\n\n")
        for author in authors:
            filep.write("- " + author + "\n")
    print("List of authors written in", authors_fn)

    return nb_authors


def generate_list_articles(bib):
    """Description of generate_list_articles
    From the bib file generates a ReadMe-styled table like:
    | [Name of the article](Link to the .pdf) | Code's link if available |
    """
    articles = ""
    for entry in bib:
        if "title" in entry:
            if "link" in entry:
                articles += "| [" + entry["title"] + "](" + entry["link"] + ") | "
            else:
                articles += "| " + entry["title"] + " | "
            if "code" in entry:
                if "No" in entry["code"]:
                    articles += "No "
                else:
                    if "github" in entry["code"]:
                        articles += "[GitHub"
                    else:
                        articles += "[Website"
                    articles += "](" + entry["code"] + ") "
            else:
                articles += "No "
            articles += "|\n"

    return articles


def generate_summary_table(bib):
    """Description of generate_summary_table
    Parse dl4m.bib to create a simple and readable ReadMe.md table.
    """
    nb_articles = str(get_nb_articles(bib))
    nb_authors = str(get_authors(bib))
    nb_tasks = str(get_field(bib, "task"))
    nb_datasets = str(get_field(bib, "dataset"))
    nb_archi = str(get_field(bib, "architecture"))
    articles = generate_list_articles(bib)

    readme_fn = "README.md"
    readme = ""
    pasted_articles = False
    with open(readme_fn, "r", encoding="utf-8") as filep:
        for line in filep:
            if "| " in line[:2] and line[2] != " ":
                if not pasted_articles:
                    readme += articles
                    pasted_articles = True
            elif "papers referenced" in line:
                readme += "- " + nb_articles + " papers referenced. "
                readme += "See the details in [dl4m.bib](dl4m.bib).\n"
            elif "unique researchers" in line:
                readme += "- " + nb_authors + " unique researchers. "
                readme += "See the list of [authors](authors.md).\n"
            elif "tasks investigated" in line:
                readme += "- " + nb_tasks + " tasks investigated. "
                readme += "See the list of [tasks](tasks.md).\n"
            elif "datasets used" in line:
                readme += "- " + nb_datasets + " datasets used. "
                readme += "See the list of [datasets](datasets.md).\n"
            elif "architecture used" in line:
                readme += "- " + nb_archi + " architectures used. "
                readme += "See the list of [architectures](architectures.md).\n"
            else:
                readme += line
    with open(readme_fn, "w", encoding="utf-8") as filep:
        filep.write(readme)
    print("New ReadMe generated")


def validate_field(field_name):
    """Description of validate_field
    Assert the validity of the field's name
    """
    fields = ["task", "dataset", "architecture", "author", "dataaugmentation",
        "link", "title", "year", "journal", "ENTRYTYPE"]
    error_str = "Invalid field provided: " + field_name + ". "
    error_str += "Valid fields: " + '[%s]' % ', '.join(map(str, fields))
    assert field_name in fields, error_str


def get_field(bib, field_name):
    """Description of tasks
    Generate insights on tasks
    """
    validate_field(field_name)
    nb_article_missing = 0
    fields = []
    for entry in bib:
        if field_name in entry:
            cur_fields = entry[field_name].split(" & ")
            for field in cur_fields:
                fields.append(field)
        else:
            nb_article_missing += 1
    print(str(nb_article_missing) + " entries are missing the " + field_name + " field.")
    nb_fields = len(set(fields))
    print(str(nb_fields) + " unique " + field_name + ".")

    field_fn = field_name + "s.md"
    with open(field_fn, "w", encoding="utf-8") as filep:
        filep.write("# List of " + field_name + "s\n\n")
        filep.write("Please refer to the list of useful acronyms used in deep ")
        filep.write("learning and music: [acronyms.md](acronyms.md).\n\n")
        for field in sorted(set(fields)):
            filep.write("- " + field + "\n")
    print("List of " + field_name + "s written in", field_fn)

    return nb_fields


def main(filen="dl4m.bib"):
    """Description of main
    Main entry point
    input: file name storing articles details
    """
    bib = load_bib(filen)
    generate_summary_table(bib)
    articles_per_year(bib)


if __name__ == "__main__":
    main("dl4m.bib")
