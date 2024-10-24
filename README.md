<img src="https://github.com/edopneto/pyinsole/blob/main/img/pyinsole-img.png" alt="Insole Icon" width="1000" height="400" />

**pyinsole** is an asynchronous message dispatcher inpired by [loafer](https://github.com/georgeyk/loafer) designed to provide a flexible and efficient way to consume messages from Amazon SQS queues. The **pyinsole** simplifies the process of integrating with SQS by offering multiple consumption strategies, allowing you to choose the best approach for your application's needs.

## Usage

The script defines an asynchronous message handler function (`my_handler`) that will be invoked whenever a message is received from the SQS queue. The `SQSRoute` class is used to route messages from the `example-queue` to the handler.

### Example Code

Here’s the main code that processes messages from the `example-queue`:

```python
import os

from pyinsole import Manager
from pyinsole.ext.aws import SQSRoute

async def my_handler(message: dict, metadata: dict, **kwargs):
    print(f"message={message}, metadata={metadata}, kwargs={kwargs}")
    return True

provider_options = {
    "endpoint_url": os.getenv("AWS_ENDPOINT_URL"),
    "options": {
        "MaxNumberOfMessages": 10,
        "WaitTimeSeconds": os.getenv("AWS_WAIT_TIME_SECONDS", 20),
    },
}

routes = [
    SQSRoute('example-queue', handler=my_handler, provider_options=provider_options),
]

if __name__ == '__main__':
    manager = Manager(routes)
    manager.run()
```

### Running the Script

1. **Start LocalStack** (or ensure you have access to AWS SQS):
   - If you are using LocalStack, make sure it's running and the `example-queue` is created:
     ```bash
     aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name example-queue
     ```

2. **Run the script**:
   ```bash
   python your_script.py
   ```

### Output

The script will listen for messages on the `example-queue`, and for each message received, it will print the message content, associated metadata, and any additional keyword arguments.

### Conclusion

This setup allows you to easily process messages from an SQS queue using the `pyinsole` library. You can modify the `my_handler` function to implement your specific message processing logic.

## How to contribute

wip
