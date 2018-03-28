## Installation

- Install heroku package on local computer
- Go to project directory
- `heroku create`
- `git push heroku master`
- `heroku ps:scale bot=1`
- `heroku ps:scale checker=1`
- `heroku config:set TG_API_TOKEN_PRODUCTION=SECRET-TELEGRAM-API-KEY`
- `heroku config:set TRUSTWALLET_API_URL="https://api.trustwalletapp.com/transactions?address=%(wallet)s&page=%(page)d&startBlock=%(start_block)d"
- `heroku config:set TG_ADMIN_ID=<TG-USER_ID>`
- `heroku addons:create mongolab` # will create sandbox plan
- Use bot UI to set up wallet, token and channel

## Some notes

I was able to activate new dyno for checker proces (on free plan) only via heroku web dashboard

## MongoDB

By default free plan is used. To use paid plan run command `heroku addons:create mongolab:shared-cluster-1`
If you need to keep existing data read https://devcenter.heroku.com/articles/mongolab#changing-plans
