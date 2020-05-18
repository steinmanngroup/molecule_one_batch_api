# molecule.one batch API
Python interface for the molecule.one chemical synthesis accessibility API.

## Usage
The API works in three stages:
 1. Submitting molecules (expressed as [SMILES](https://www.daylight.com/dayhtml_tutorials/languages/smiles/index.html)) to the batch server.
 2. Querying the batch server for the status.
 3. Retrieving results from the batch server.

### Making a Request
```python
import moleculeone as mo

my_api_key = "<your api key here>"
smiles_to_scan = ["CC(C)NC[C@@H](O)COc1cccc(c12)[nH]c3c2cccc3"]

request = mo.BatchScoreRequest(smiles_to_scan, my_api_key)
request.submit()
```
### Querying the Batch Server
```python
status = mo.BatchJobStatus(request, my_api_key)
```
It is possible to ask if the job is finished running all jobs
```python
if status.is_finished():
    # do something
```
### Retrieving Results
```python
results = mo.BatchResult(request, my_api_key)
```
which can return a list of dictionaries with the results through the `.get()` method
```python
my_results = results.get()
```
which can be printed or postprocessed.
A convenience iterator is supplied directly for the `BatchResult` object.
```python
for r in results:
    score = r["result"]
    smiles = r["targetSmiles"]
    print("{0:6.2f} {1:s}".format(score, smiles))
```