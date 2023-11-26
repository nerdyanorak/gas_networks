#!/bin/sh

for test_case in `cat test_cases.txt`; do
	python driver.py --input=../data/test/$test_case/pulp/data --output=../data/test/$test_case/pulp/results --verbose
done

exit 0

