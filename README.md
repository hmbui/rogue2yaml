# rogue2yaml
A Converter that serializes a Python Rogue object into a CPSW YAML file

Requirements:

Python:

    PyYAML
    Pyro4
    parse
    recordclass
    click

    Optional, but recommended:

        Python 3.6
        Miniconda (or Anaconda)

slaclab Clones:

    rogue (https://github.com/slaclab/rogue)
    cryo-det (https://github.com/slaclab/cryo-det)
    amc-carrier-core (https://github.com/slaclab/amc-carrier-core)


How to Use:

1. Modify the setup_rogue2yaml.sh file and update the paths to rogue, acm-carrier-core, and cryo-det appropriately.
2. Copy the Python Rogue file to the input/ directory
3. Create the output/ directory at the same level as input/
4. Run the command

    python rogue2yaml.py <className>

   to start the conversion. The output file will be in the output/ directory, having the name of <className>.yaml

   Note that the Python Rogue file name must be the same as the class it contains.
5. Get the Converter's version:

    python rogue2yaml.py --version

6. Get the CPSW Schema version supported by the Converter:

    python rogue2yaml.py --cpsw-schema-version


Limitations:

For commands, the Converter only outputs the command names and their metadata. The command sequence (entries and
values) must be added manually.

As there could be indirect references and customized variables, the user is expected to review the output results,
and make any supplemental edits.
