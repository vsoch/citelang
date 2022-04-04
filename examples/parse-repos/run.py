import citelang.utils as utils
import citelang.main.parser as parser
import os

# This is an example of using citelang to parse two repos,
# and to generate a software citation tree that combines BOTH
# Here we choose two projects with overlapping dependencies
repos = {}
for name in ["vsoch/django-river-ml", "vsoch/django-oci"]:
    repos[name] = utils.clone(name)

# You can use a find here, but here I know there are requirements.txt!
cli = parser.RequirementsParser()
for name, repo_dir in repos.items():
    require_text = os.path.join(repo_dir, "requirements.txt")
    cli.gen(name, filename=require_text)
    
    # you can tweak credit params here too!
    # cli.gen(name, filename=require_text, min_credit=0.001)

# Summarize across packages!   
table = cli.prepare_table()

print(table.render())
with open("requirements-example.md", 'w') as fd:
    fd.write(table.render())
    
# Run for the Description file in testdata
cli = parser.RequirementsParser()
result = cli.gen("r-lib", filename="../../citelang/tests/testdata/DESCRIPTION")   
with open("description-example.md", 'w') as fd:
    fd.write(result.render())

# Run for the setup.py in testdata
cli = parser.RequirementsParser()
result = cli.gen("python-lib", filename="../../citelang/tests/testdata/setup.py")   
with open("setup-py-example.md", 'w') as fd:
    fd.write(result.render())

# Run for Gemfile in testdata
cli = parser.RequirementsParser()
result = cli.gen("ruby-lib", filename="../../citelang/tests/testdata/Gemfile")   
with open("gemfile-example.md", 'w') as fd:
    fd.write(result.render())
    
# Parse go mod file
cli = parser.RequirementsParser()
result = cli.gen("go-lib", filename="../../citelang/tests/testdata/go.mod")   
with open("go-mod-example.md", 'w') as fd:
    fd.write(result.render())
        
# Parse an npm package.json
cli = parser.RequirementsParser()
result = cli.gen("npm-lib", filename="../../citelang/tests/testdata/package.json")   
with open("npm-example.md", 'w') as fd:
    fd.write(result.render())
