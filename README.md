# doi2ietf

This port of Ruby [doilit](https://github.com/cabo/kramdown-rfc2629/blob/master/bin/doilit) script to Python 3.

## Dependencies
These scripts are written in Python 3.
Dependencies for Python 3 for all scripts are
included in `requirements.txt` and can be installed
using `pip` with `pip3 install -r requirements.txt`.

## Usage

Just pass list of [DOI ID](https://dx.doi.org/) separated by space as argument to `doi2ietf.py` script.
By default output will be in YAML. To get XMl output use option: `-x` or `--xml`.

Also you can use option `-c` (or `--cache`) to cache HTTP-requests to data.crossref.org

Example:

`./doi2ietf.py -c -x 10.1109/5.771073 10.1109/MIC.2012.29`

To test and compare results you can use additional script `test/test_results.py`.
Before start you need to edit and save config. Copy `config.py.sample` to `config.py` and edit values. At least you should write correct path to `doilit` at `path_to_ruby_doilit` variable. If this script not available, you can test and compare values saved at `path_to_test_output_dir`. To fetch new values via `doilit` you need to use `-nc` or --`no-cache` option:
 
`./test/test_results.py -nc`
