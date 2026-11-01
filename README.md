# JudoShiai Utilities

## Database initialisation

The script has a command line interface.
In the working directory:

```shell
python ~/git_repos/judoshiai_utilities/init_shiai_db.py \ 
 --template ~/Desktop/judoshiai_test/masters_template.shi  \ 
 --competitors ~/Desktop/judoshiai_test/MASTERS_2023_TEST/Meldungen_2023.xlsx \ 
 --name "masters_2023"
```

## Competition result GUI

The script has a command line interface.

```shell
python ~/git_repos/judoshiai_utilities/main.py --host localhost
```

## Aggregate results

In the working directory of the competition.

### show category results

```shell
python ~/git_repos/judoshiai_utilities/result_summary.py 
 --results-directory results/
```

```shell
python ~/git_repos/judoshiai_utilities/result_summary.py 
 --results-directory results/ 
 --cat-pattern "Men|Women"
```

### show group results

```shell
python ~/git_repos/judoshiai_utilities/result_summary.py 
 --results-directory results/ 
 --no-cat-results 
 --group-results 
 --group-cert-template urkunde/urkunde_template.svg
```

### show medal needs

```shell
python ~/git_repos/judoshiai_utilities/medal_needs.py
```

### compare with cash registration

```shell
python ~/git_repos/judoshiai_utilities/result_summary.py 
 --results-directory results/ 
 --no-cat-results 
 --create-starts-overview
```

## Notes

The GUI requires a special build of JudoShiai to make use of the "reset matches" functionality.
