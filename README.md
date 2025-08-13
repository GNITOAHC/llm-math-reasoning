# Math LLM Reasoning

### Start

```
python3 main.py {tool-assisted, pure-reasoning} -i datasets/dataset_{LP/ILP, GCP, Knapsack, TSP}/parsed_output/q{i}.desc.txt -l log -r {medium, high}
```

### Prompts selection of tool assisted pipeline

For problems like TSP and GCP, you can modify the CODE_GENERATOR_PROMPT and FIX_CODE_PROMPT, which we provided in the `specific_prompts` directory
