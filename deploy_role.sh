#!/bin/bash

ROLE=$1
TARGET=$2
cat > var/_tmp.yml << EOF
- hosts: $TARGET
  strategy: free
  roles:
    - $ROLE
EOF

ansible-playbook -i var/inventory -f 20 var/_tmp.yml --extra-vars="deps=1" --
