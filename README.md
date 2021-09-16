# Span-based Causality Extraction for Financial Documents
This repository contains the supporting code for the FinCausal 2020 submission titled `Span-based Causality Extraction for Financial Documents`. The model extracts cause and effect spans from financial documents, for example:

|Text|Cause|Effect|
| ------------- |:-----------------------:| ---------------------:|
|Boussard Gavaudan Investment Management LLP bought a new position in shares of GENFIT S A/ADR in the second quarter worth about $199,000. Morgan Stanley increased its stake in shares of GENFIT S A/ADR by 24.4% in the second quarter.Morgan Stanley now owns 10,700 shares of the company’s stock worth $211,000 after purchasing an additional 2,100 shares during the period|Morgan Stanley increased its stake in shares of GENFIT S A/ADR by 24.4% in the second quarter|Morgan Stanley now owns 10,700 shares of the company’s stock worth $211,000 after purchasing an additional 2,100 shares during the period.|
|Zhao found himself 60 million yuan indebted after losing 9,000 BTC in a single day (February 10, 2014)|losing 9,000 BTC in a single day (February 10, 2014)|Zhao found himself 60 million yuan indebted|

(sample from the [task description: Data Processing and Metrics for FinCausal Shared Task, 2020, Mariko et al.](https://drive.google.com/file/d/1LUTJVj9ItJMZzKvy1LrCTuBK2SITzr1z/view))

please cite the original author of this code:

```latex
@inproceedings{
 Becquin-fincausal-2020, 
 title ={{GBe at FinCausal 2020, Task 2: Span-based Causality Extraction for Financial Documents}}, 
 author = {Becquin, Guillaume}, 
 booktitle ={{The 1st Joint Workshop on Financial Narrative Processing and MultiLing Financial Summarisation (FNP-FNS 2020}}, 
 year = {2020}, 
 address = {Barcelona, Spain} 
}
```

## Instructions

0. Install requirements provided in `reuiquirements.py` (it is advised to use a virtual environment)
1. Generate the train / development data split running running the `./utils/split_dataset.py`

### Training:
2. run `main.py --train`

### Evaluation:
2. run `main.py --eval`

### Generate predictions:
2. run `main.py --test`
