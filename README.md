# French Number Practice

This app helps you get comfortable with french numbers in range from 0 to 100.

## How to install

```shell
source .venv/bin/activate
pip install -r requirements.txt
```

## Example

```plain
$ src/french_number_practice.py
Specify the two values for the start and end of the range;
The values must be separated by a space:
input the range [from, to]: 64
Two numbers must be entered, separated by a space.
input the range [from, to]: 60 64
soixante-trois: 63
Good guess!
soixante: 60
Good guess! (consecutive good answers: 1)
soixante-deux: 62
Good guess! (consecutive good answers: 2)
soixante-quatre: 60
Guess again
soixante-quatre: 64
Good guess!
soixante et un: 61
Good guess! (consecutive good answers: 1)
soixante-quatre: 64
Good guess! (consecutive good answers: 2)
You solved all! Well done.

Summary:
  Total problems solved: 5 / 5
  Total mistakes made: 1
  Maximum successive correct answer: 3
  Total time spent: 0:15.623
```

# Testing

```shell
python3 -m unittest discover -s src/
```