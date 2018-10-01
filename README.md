# Rogue2Yaml
A Converter that serializes a Python Rogue object into a CPSW YAML file.

## Prerequisites
slaclab rogue (https://github.com/slaclab/rogue)


## Installing Rogue2Yaml
You must first install rogue as it is what this Rogue2Yaml utility is built for.

In doing so, you must first satisfy the [rogue prerequisites](https://github.com/slaclab/rogue#python-packages-required, "Rogue Requirements for Python").

Next, clone rogue from GitHub:

```sh
git clone https://github.com/slaclab/rogue.git
```

Now, clone the Rogue2Yaml utility repo:
```sh
git clone https://github.com/slaclab/rogue2yaml.git
pip install .[all]
```

## Running Rogue2Yaml

1. Note the path to your cloned rogue repo
2. Copy the rogue files you want to convert into a directory
3. Create a directory for your output CPSW YAML files 

```
source export_rogue2yaml_envs.sh
rogue2yaml <rogue_python_dir_path> <rogue_python_class_file_dir_path> [output_directory]
```
   * rogue_python_dir_path: The path to the entire Rogue Python library
   * rogue_python_class_file_dir_path: The path to the collection of the Rogue Python files to be converted
   * output_directory [optional]: The path to the directory where the CPSW YAML output files are to be saved. If not
   specified, the output files will be in the output/ sub-directory of the execution directory.
   
   Notes:
   
   1. Each Python Rogue file name must be the same as the class it contains. If not, the converter will attempt
      to adjust the capitalization of each character in the provided class name. If this also fails, the converter will
      proceed to the next Python file, and will output the unsuccessfully converted file name into the conversion
      failure list, at the summary.
   
   2. If a YAML file has already been output for the current Rogue Python file, the conversion for that file will be
      skipped, and the converter will move on to the next file in the Rogue Python file batch. If you want the skipped
      file to be re-converted, delete its YAML output file and run the converter again. The names of the skipped files
      will be provided in the summary.
      
   3. The output files will be in the output/ directory, keeping the same names except for the extension, which is now 
      ".yaml" 

### Excluding Files from Conversion

For rogue files that cannot be automatically converted in a batch, and will require manual conversion, i.e. having
Python syntax error or requiring a network connection, you can exclude them from the Rogue2Yaml conversion batch.

Go to settings/exclusions.json, and follow the JSON examples there to exclude rogue files. The general syntax is

```
{
  "excluded_filename": "Exclusion Reason."
}
```
   
### Additional Commands

* Get the Converter's version:

    ```python rogue2yaml.py --version```

* Get the CPSW Schema version supported by the Converter:

    ```python rogue2yaml.py --cpsw-schema-version```

### Current Limitations

For commands, the Converter only outputs the command names and their metadata. The command sequence (entries and
values) must be added manually.

As there could be indirect references and customized variables, the user is expected to review the output results,
and make any supplemental edits.
