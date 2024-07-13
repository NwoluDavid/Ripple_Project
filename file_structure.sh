#!/bin/bash

# Base directory
base_dir="fastapi-project"

# # Create base directory and subdirectories
# mkdir -p ${base_dir}/{alembic,src/{auth,aws,posts},tests/{auth,aws,posts},templates,requirements}

# # Create files in the auth module
# touch ${base_dir}/src/auth/{router.py,schemas.py,models.py,dependencies.py,config.py,constants.py,exceptions.py,service.py,utils.py}

# # Create files in the aws module
# touch ${base_dir}/src/aws/{client.py,schemas.py,config.py,constants.py,exceptions.py,utils.py}

# # Create files in the posts module
# touch ${base_dir}/src/posts/{router.py,schemas.py,models.py,dependencies.py,constants.py,exceptions.py,service.py,utils.py}

# # Create global config and other files in src
# touch ${base_dir}/src/{config.py,models.py,exceptions.py,pagination.py,database.py,main.py}

# # Create template file
# touch ${base_dir}/templates/index.html

# # Create requirements files
# touch ${base_dir}/requirements/{base.txt,dev.txt,prod.txt}

# # Create other root level files
# touch ${base_dir}/{.env,.gitignore,logging.ini,alembic.ini}

touch src/user/{router.py,schemas.py,models.py,dependencies.py,config.py,constants.py,exceptions.py,service.py,utils.py}


echo "Project structure created successfully."
