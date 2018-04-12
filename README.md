## Server Initial Configuration

Put name of server into var/inventory::

    [servers]
    server-name

- `mkdir var`
- `touch var/inventory`
- `git clone https://github.com/lorien/cluster-roles deploy/roles`
- `cp -R deploy/roles var/roles`
- `./deploy_role.sh pyserver server-name`
- `./deploy_role.sh mongodb server-name`

Update local ~/.ssh/config (because pyserver role will change default SSH port)::

    Host server-name
        Port 1477

## App Initial Deployment

Prepare .env file at deploy/.env (it will be uploaded to the server)::

    MONGODB_URI=mongodb://localhost:27017/gambit_bot
    TRUSTWALLET_API_URL=https://api.trustwalletapp.com/transactions?address=%(wallet)s&page=%(page)d&startBlock=%(start_block)d
    TG_API_TOKEN_PRODUCTION=***
    TG_ADMIN_ID=***

- `ansible-playbook -i var/inventory deploy/gambit.yml --extra-vars="target=server-name"`
