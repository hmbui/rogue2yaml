import versioneer
from setuptools import setup, find_packages

setup(
    name='rogue2yaml',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    # Author details
    author='SLAC National Accelerator Laboratory',

    packages=find_packages(),
    package_dir={'rogue2yaml':'rogue2yaml', 'rogue2yaml_launcher':'rogue2yaml_launcher'},
    description='Tool to convert pyrogue files to CPSW YAML',
    url='https://github.com/slaclab/rogue2yaml',
    entry_points={
        'gui_scripts': [
            'rogue2yaml=rogue2yaml_launcher.main:main'
        ]
    },
    license='BSD',
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
