## Installation

- Install heroku package on local computer
- Go to project directory
- `heroku create`
- `heroku push heroku master`
- `heroku ps:scale bot=1`
- `heroku ps:scale process_ops=1`
- `heroku config:set TG_API_TOKEN_PRODUCTION=SECRET-TELEGRAM-API-KEY`
- `heroku addons:create mongolab` # will create sandbox plan
- # To create paid mongodb plan: `heroku addons:create mongolab:shared-cluster-1`
- Use bot UI to set up wallet, token and channel
