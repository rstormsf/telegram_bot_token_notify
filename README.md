## Installation

Put name of server into var/inventory::

    [some-group]
    server-name

Create .env file::

    MONGODB_URI=mongodb://localhost:27017/gambit_bot
    TRUSTWALLET_API_URL=https://api.trustwalletapp.com/transactions?address=%(wallet)s&page=%(page)d&startBlock=%(start_block)d
    TG_API_TOKEN_PRODUCTION=***
    TG_ADMIN_ID=***

- `git clone https://github.com/lorien/cluster-roles deploy/roles`
- `./deploy_role.sh pyserver server-name`

Update ~/.ssh/config with (because pyserver role will change default SSH port)::

    Host server-name
        Port 1477

- `./deploy_role.sh mongodb server-name`
- `ansible-playbook -i var/inventory deploy/gambit.yml --extra-vars="target=server-name"`
