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
    
# Run for the Description file here
cli = parser.RequirementsParser()
result = cli.gen("r-lib", filename="DESCRIPTION")   
with open("description-example.md", 'w') as fd:
    fd.write(result.render())

