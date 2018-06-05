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

1. Modify the setup_rogue2yaml.sh file and update the path to rogue
2. Create the input/ directory at the same level as the rogue2yaml.py file
3. Create the output/ directory at the same level as input/
4. Run the command

    python rogue2yaml.py <pyrogue_dir_name> <pyrogue_class_file_dir_name>

   to start the conversions.
   
   Note that each Python Rogue file name must be the same as the class it contains. If not, the converter will attempt
   to adjust the capitalization of each character in the provided class name. If this also fails, the converter will
   proceed to the next Python file, and will output the unsuccessfully converted file name into the conversion failure
   list, at the summary.
   
   <pyrogue_dir_name>: The directory that contains all the pyrogue libraries
   <pyrogue_clss_file_dir_name>: The directory that contains all the Python files to be converted to YAML
   
   The output files will be in the output/ directory, keeping the same names except for the extension, which is now 
   ".yaml" 
 
   
5. Get the Converter's version:

    python rogue2yaml.py --version

6. Get the CPSW Schema version supported by the Converter:

    python rogue2yaml.py --cpsw-schema-version


Limitations:

For commands, the Converter only outputs the command names and their metadata. The command sequence (entries and
values) must be added manually.

As there could be indirect references and customized variables, the user is expected to review the output results,
and make any supplemental edits.
