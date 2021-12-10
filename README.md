# inobulles.github.io

Website for everything from the Inobulles organization. Currently, the website only displays very basic information for aquaBSD, but it will soon be updated.

## Framework

The website comes with its own very primitive framework.
To build the website, run:

```sh
% python3 framework/main.py [input directory] [output directory]
```

By default, `input directory` & `output directory` are `site` & `out` respectively.

## Deploying

Because GitHub Pages does not allow us a wide range of options for selecting which directory to deploy our website from, we must use [this](https://gist.github.com/cobyism/4730490) trick.
The gist of it is that we create a subtree of `out` and then push it to the `gh-pages` branch:

```sh
% git subtree push --prefix out origin gh-pages
```