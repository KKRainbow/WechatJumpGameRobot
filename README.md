# Requirements
Only need ADB installed.

# Usage

1. Preparation

    Use ``pip install -r requirements.txt`` to install dependencies first

2. Mark start and end point in a screenshot

    ```
    ./jump.py screenshot.png
    ```

3. Make a jump when phone is connected and game is running.
    ```
    ./jump.py
    ```

4. Use following command to run repeatedly.
    ```
    for ((x=0;x<100;x++));do sleep 1; ../jump.py;done
    ```
