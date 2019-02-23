* Update changelog in docs/changelog.rst and commit.

* Tag commit

        git tag -a x.x.x -m "Version x.x.x"

* Push to github

        git push --tags

* Upload to PyPI

        git clean -xfd  # remove all files in directory not in repository
        python setup.py sdist bdist_wheel --universal  # make packages
        twine upload dist/*  # upload packages

* Increase version number

    Change \_\_version\_\_ = 'x.x.x' in arlib/\_\_init\_\_.py
    
* Build conda recipe
