from random import randint

n = randint(0, 100)
guessed = False
num_guesses = 0


while not guessed:
    guess = input('Guess a number: ')

    try:
        guess = int(guess)
    except ValueError:
        print('That is not a number!')
        continue

    num_guesses += 1

    if guess < n:
        print('Too low!')
    elif guess > n:
        print('Too high!')
    else:
        guessed = True

    print()


print('You guessed correctly')
print('It took you', num_guesses, 'guesses')
