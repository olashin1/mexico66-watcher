<div align="center">

# mexico66-watcher

A lightweight stock monitoring service for Onitsuka Tiger Mexico 66 shoes that automatically checks product availability and sends Discord notifications when stock changes.

</div>

## Overview

`mexico66-watcher` continuously monitors an Onitsuka Tiger Mexico 66 product page for stock availability. When availability changes, the application sends a notification to a Discord server through a configured webhook.

The service is containerized with Docker and deployed on a Google Cloud Platform Ubuntu Linux VM, allowing it to run continuously without relying on a local machine.

## Tech Stack

| Category               | Technologies                  |
| ---------------------- | ----------------------------- |
| **Language**           | Python                        |
| **Notifications**      | Discord Webhooks              |
| **Deployment**         | Docker, Google Cloud Platform |
| **Environment**        | Ubuntu Linux                  |
| **Package Management** | pip                           |

## Installation

```bash
git clone https://github.com/olashin1/mexico66-watcher
cd mexico66-watcher
python -m pip install -r requirements.txt
```

## Discord Setup

The watcher sends stock notifications to a Discord text channel using a webhook.

To create one:

1. Open your Discord server.
2. Go to **Server Settings**.
3. Select **Integrations**.
4. Open **Webhooks** and select **New Webhook**.
5. Choose the text channel where you want stock notifications to appear.
6. Copy the webhook URL.
7. Add the URL to your `.env` file as `DISCORD_WEBHOOK_URL`.

Keep the webhook URL private, as anyone with access to it can send messages to the configured channel.

## Environment Variables

Create a `.env` file and configure the following variables:

| Variable              | Description                                  |
| --------------------- | -------------------------------------------- |
| `PRODUCT_URL`         | Onitsuka Tiger product page to monitor       |
| `DISCORD_WEBHOOK_URL` | Discord webhook used for stock notifications |
| `CHECK_INTERVAL`      | Time between stock checks                    |

Example:

```env
PRODUCT_URL=<product-url>
DISCORD_WEBHOOK_URL=<discord-webhook-url>
CHECK_INTERVAL=<interval>
```

## Running the Watcher

```bash
python main.py
```

## Docker

Build the container:

```bash
docker build -t mexico66-watcher .
```

Run it:

```bash
docker run --env-file .env mexico66-watcher
```

## Deployment

The watcher is deployed on a Google Cloud Platform Compute Engine VM running Ubuntu Linux. Docker provides a consistent runtime environment while the VM allows the monitoring process to remain active independently of the local development machine.

## Project Structure

```text
mexico66-watcher/
├── scripts/          # Development and testing scripts
├── main.py           # Main stock monitoring process
├── requirements.txt  # Python dependencies
├── Dockerfile        # Container configuration
└── .env              # Local environment variables
```

## How It Works

1. The watcher periodically checks the configured Onitsuka Tiger product page.
2. Product availability is parsed from the returned page data.
3. The current stock state is evaluated for changes.
4. When relevant availability is detected, a notification is sent to the configured Discord server.
5. The process repeats according to `CHECK_INTERVAL`.
