<div align="center">
    <img src="img/pyinsole-img.png" style="width:100px;height:100px;" alt="Circular Image">
</div>
<br>
<p align="center">
  <em><b>pyinsole</b> is an asynchronous message dispatcher inpired by <a href="https://github.com/georgeyk/loafer">loafer</a> designed to provide a flexible and efficient way to consume messages from Amazon SQS queues. The <b>pyinsole</b> simplifies the process of integrating with SQS by offering multiple consumption strategies, allowing you to choose the best approach for your application's needs.</em>
</p>
<br>

## 💻 Usage

The script defines an asynchronous message handler function (`my_handler`) that will be invoked whenever a message is received from the SQS queue. The `SQSRoute` class is used to route messages from the `example-queue` to the handler.

#### Example Code

Here’s the main code that processes messages from the `example-queue`. The script will listen for messages on the `example-queue`, and for each message received, it will print the message content, associated metadata, and any additional keyword arguments.

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

#### Running the Script

This setup allows you to easily process messages from an SQS queue using the `pyinsole` library. You can modify the `my_handler` function to implement your specific message processing logic.

1. **Start LocalStack** (or ensure you have access to AWS SQS). If you are using LocalStack, make sure it's running and the `example-queue` is created:
    ```bash
    aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name example-queue
    ```

2. **Run the script**:
   ```bash
   python your_script.py
   ```

3. **Push some messages**:
    ```
    aws --endpoint-url=http://localhost:4566 sqs send-message --queue-url http://localhost:4566/000000000000/example-queue --message-body "Your message body"
    ```

<br>

## 🎯 Roadmap

You can find the project roadmap [here](./ROADMAP.md).

This document outlines future improvements, features, and tasks planned for the project.

<br>

## 🫱🏻‍🫲🏽 How to contribute

We welcome contributions of all kinds to make **pyinsole** better! To contribute to the project, follow these steps:

1. **Fork the repository**: Click on the "Fork" button at the top right of the repository page.

2. **Clone your fork**:
   ```bash
   git clone https://github.com/edopneto/pyinsole
   cd pyinsole
   ```

3. **Create a new branch**: It's best practice to create a feature branch for your changes.
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes**: Work on your feature, bug fix, or documentation improvement.

5. **Test your changes**: Ensure everything is working as expected.

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add a brief message describing your changes"
   ```

7. **Push to your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request**: Go to the repository on GitHub, and you’ll see a button to "Compare & Pull Request." Submit a pull request with a clear title and description of your changes.
