# CDF Scrapers

This is a library of scrapers for producing easy-to-consume JSON files of
information for [CDF](http://www.cdf.toronto.edu/) services.


## Library Reference

### Lab machine availability

##### Data
<http://www.cdf.toronto.edu/~g3cheunh/cdflabs.json>

##### Scraper source
<http://www.cdf.toronto.edu/usage/usage.html>

##### Output format
```js
{
    "timestamp": String,
    "labs": [{
        "name": String,
        "available": Number,
        "busy": Number,
        "total": Number,
        "percent": Number,
    }]
}
```

------

### Printer job queues

##### Data
<http://www.cdf.toronto.edu/~g3cheunh/cdfprinters.json>

##### Scraper source
Output of the `lpq -a` command on a CDF machine.

##### Output format
```js
{
    "timestamp": String,
    "printers": [{
        "name": String,
        "description": String,
        "length": Number
        "jobs": [{
            "rank": String,
            "job": String,
            "size": String,
            "time": String,
            "error": String
        }]
    }]
}
```

## Usage

To use the scripts, run them using [Python 3](http://python.org/).

```shell
$ python3 SCRIPT_NAME.py -o [OUTPUT_PATH] -f [FILE_NAME]
```

If no output path nor filename is given, the script prints the output to stdout.

If a filename is specified but no output path is provided, it will output the
file into the same directory as the script.

If an output path is specified but no file name is provided, it simply uses the
default file name:

| Script      | Default file name |
|-------------|-------------------|
| labs.py     | cdflabs.json      |
| printers.py | cdfprinters.json  |

You can use the `-h` flag to see information about the script usage at any time:

```shell
$ python3 SCRIPT_NAME.py -h
```


### Running on CDF

The scripts are currently being run via Cron jobs on the CDF wolf server:

```
*/5 * * * * /local/bin/python3 ~/cdf-scrapers/printers/printers.py -o ~/public_html
*/10 * * * * * /local/bin/python3 ~/cdf-scrapers/labs/labs.py -o ~/public_html
```
