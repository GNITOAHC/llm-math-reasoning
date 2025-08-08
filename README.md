# Math LLM Reasoning

### Start

1. tool-assisted

```
python3 -m tool-assisted \ -i datasets/dataset_{LP/ILP or GCP or Knapsack or TSP}/parsed_output/q{i}.desc.txt \ -l log \ -r {medium or high}
```

2. pure reasoning

```
python3 -m pure-reasoning \ -i datasets/dataset_{LP/ILP or GCP or Knapsack or TSP}/parsed_output/q{i}.desc.txt \ -l log \ -r {medium or high}
```

### Prompts selection of tool assisted pipeline

For problems like TSP and GCP, you can modify the CODE_GENERATOR_PROMPT and FIX_CODE_PROMPT, which we provided in the `specific_prompts` directory
