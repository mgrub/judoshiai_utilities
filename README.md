# JudoShiai Utilities

## Database initialisation

The script has a command line interface.
In the working directory:

```shell
. ~/python_envs/judo_utils/bin/activate
python ~/git_repos/judoshiai_utilities/init_shiai_db.py 
 --template masters_template.shi 
 --competitors Meldungen_2026.xlsx 
 --name "masters_2026"
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

### JudoShiai special build

The GUI requires a special build of JudoShiai to make use of the "reset matches" functionality.

### JudoShiai 4.4 and Debian 13

Running JudoShiai 4.4 under Debian 13 required a modification of the *.deb file.

```shell
mkdir oldpack newpack newpack/DEBIAN

# unpack deb content (bins and control)
dpkg -x judoshiai_4.4.1-1_amd64.deb oldpack
dpkg-deb -e judoshiai_4.4.1-1_amd64.deb oldpack/DEBIAN

# ... rename the package "libgdk-pixbuf2.0-0" to "libgdk-pixbuf-2.0-0" in newpack/DEBIAN/control

# rebuild package
dpkg-deb -Z xz -b oldpack/ newpack/
```
