[source of knapsack dataset](https://hjemmesider.diku.dk/~pisinger/codes.html)


### Explanation
```knapPI_1_1000_1000.csv```
1: problem set
1000: total items to select
1000: 最後的 1000 不用管，是 random int 的範圍，除了 large 以外都ㄧ樣

### Exp Setting
We test our algorithm on **100** problem instances with n = {50, 100, 200}, where n denotes the total number of available items.

### Usage

You can use parser2.py to convert csv into q{i}.desc.txt, q{i}.ans.txt, where the csv is in ```original_csv```