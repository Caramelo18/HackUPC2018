# Commubot

Commubot is a Telegram bot serving as a proof of concept for a public transportation disturbance alert system. The user is able to ask the bot for status on a specific trip, specifying origin and destination, or register his regular commute and request information on that. The bot also notifies users of newly added disturbances that affect his regular commute.

## Data

The data is based on the Barcelona subway system, although the disturbances introduced are artificial (added by an administrator) and don't reflect real events.

## Technological Stack

 * Amazon DynamoDB
 * AWS Lambda
 * AWS Step Functions
 * Neo4j
 * Python
 * Serverless
 * Telegram Bot API
