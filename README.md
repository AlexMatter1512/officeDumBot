## Getting Started
- Create a .dev.env file in the root of the project. You can use the `.dev.env.sample` as a template.
  - The only variables you need to change are: 
    - `TOKEN_DEV` : your telegram bot token
    - `REGISTRATION_COMMAND` : the secret message that will be sent to the bot to register as an authorized user
- Run `docker compose --profile dev up` to start the application.
