PYTHON ?= python
export PYTHONPATH := .

.PHONY: help install counties pipeline test sample clean

help:
	@echo "make install    - install Python dependencies"
	@echo "make counties   - download the Census county boundary file"
	@echo "make pipeline    - run the full pipeline (needs data/raw/eaglei_outages_2022.csv)"
	@echo "make test        - run unit tests"
	@echo "make sample      - run the pandas chain on the synthetic sample (no geopandas needed)"
	@echo "make clean       - remove generated processed/output files"

install:
	$(PYTHON) -m pip install -r requirements.txt

counties:
	$(PYTHON) -m ianoutage.download_counties

pipeline:
	bash run_all.sh

test:
	$(PYTHON) -m pytest -q

sample:
	$(PYTHON) -m ianoutage.slice_eaglei --input data/sample/eaglei_ian_florida_sample.csv
	$(PYTHON) -m ianoutage.peak_by_county
	$(PYTHON) -m ianoutage.severity
	$(PYTHON) -m ianoutage.restoration_curve
	$(PYTHON) -m ianoutage.validate
	@echo "Sample chain ran. These are synthetic numbers for testing only."

clean:
	rm -rf data/processed/* data/outputs/* docs/RESULTS.md
	@touch data/processed/.gitkeep data/outputs/.gitkeep
