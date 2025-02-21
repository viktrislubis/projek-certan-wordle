import random
import time

number = 0
params = ["scored, position"]


class PuzzleWords:
    def __init__(self, word_file):
        self.word_list = self.load_words(word_file)

    def load_words(self, word_file):
        with open(word_file, "r") as file:
            return [line.strip().upper() for line in file.readlines()]

    def get_random_word(self):
        import random
        return random.choice(self.word_list)

# Instantiate puzzle_words globally
puzzle_words = PuzzleWords("words-guess.txt")

class Wordle:
    def __init__(self, correct_word=None):
        # Check if the correct word is valid
        if correct_word in puzzle_words.word_list:
            self.correct_word = correct_word
        else:
            self.correct_word = puzzle_words.get_random_word()

        # List of guesses so far
        self.guesses = []



class WordList:


    def __init__(self, *files):
        # list of all the words
        global number
        number += 1
       # print(number)
       # print("debug files")
        self.word_list = []
        for file in files:
            with open(file, "r", encoding="UTF-8") as in_file:
                for line in in_file:
                    self.word_list.append(line.strip())

        # letter counts in all words in the list: {"a": 100, "b": 200, ...}
        self.letter_count = {}

        # words' scores: {"apple": 100, "fruit": 200} etc
        # score is the sum of all letters' frequencies
        self.word_scores = {}

        # Same, but scores account for letter positions
        self.position_letter_count = [{}, {}, {}, {}, {}]
        self.position_word_scores = {}

        # Generate the word scores
        # (both positional and total)
        self.gen_word_scores()
        self.gen_positional_word_scores()

    def copy(self):

        new_word_list = WordList()
        new_word_list.word_list = self.word_list.copy()
        new_word_list.word_scores = self.word_scores.copy()
        new_word_list.position_word_scores = self.position_word_scores.copy()
        return new_word_list

    def __len__(self):

        return len(self.word_list)

    def get_random_word(self):

        return random.choice(self.word_list)

    def get_hiscore_word(self, use_position=False):

        scores = self.position_word_scores if use_position else self.word_scores
        best_word = ""
        best_score = 0
        for word in self.word_list:
            print ("word: ")
            print(word)
            if scores[word] > best_score:
                best_score = scores[word]
                best_word = word
        return best_word

    def get_maximized_word(self, maximized_letters):

        self.gen_letter_count()
        best_word = ""
        best_score = 0
        for word in self.word_list:
            this_score = 0
            for letter in maximized_letters:
                if letter in word:
                    this_score += 1
            if this_score > best_score:
                best_score = this_score
                best_word = word
        return best_word

    def gen_letter_count(self):

        self.letter_count = {c: 0 for c in "abcdefghijklmnopqrstuvwxyz"}
        for word in self.word_list:
            for letter in set(word):
                self.letter_count[letter] += 1

    def gen_positional_letter_count(self):

        for i in range(5):
            self.position_letter_count[i] = \
                {c: 0 for c in "abcdefghijklmnopqrstuvwxyz"}
        for word in self.word_list:
            for i, letter in enumerate(word):
                self.position_letter_count[i][letter] += 1

    def gen_word_scores(self):

        self.gen_letter_count()
        self.word_scores = {}
        for word in self.word_list:
            word_score = 0
            for letter in set(list(word)):
                word_score += self.letter_count[letter]
            self.word_scores[word] = word_score

    def gen_positional_word_scores(self):

        self.gen_positional_letter_count()
        self.position_word_scores = {}
        for word in self.word_list:
            # Sum up scores, but if the letter is twice in the word
            # use the highest score only
            word_score = {}
            for i, letter in enumerate(word):
                if letter not in word_score:
                    word_score[letter] = self.position_letter_count[i][letter]
                else:
                    word_score[letter] = max(word_score[letter],
                                             self.position_letter_count[i][letter])
            self.position_word_scores[word] = sum(word_score.values())

    def filter_by_mask(self, yes_mask, no_mask, allowed_mask):

        new_words = []
        for word in self.word_list:

            # Yes_mask: should have that letter in that place
            for n, must_have_letters in enumerate(yes_mask):
                # use [0]: in YES mask there is no more than 1 item per slot
                if must_have_letters and word[n] != must_have_letters[0]:
                    break
            else:
                # No_mask: should NOT have that letter in that place
                fail = False
                for n, forbidden_letters in enumerate(no_mask):
                    for forbidden_letter in forbidden_letters:
                        if word[n] == forbidden_letter:
                            fail = True
                    if fail:
                        break
                else:
                    # Allowed mask: should have allowed count of letters
                    for letter in "abcdefghijklmnopqrstuvwxyz":
                        count = word.count(letter)
                        if letter not in allowed_mask[count]:
                            break
                    else:
                        new_words.append(word)
        self.word_list = new_words


class Guess:

    def __init__(self, guess_word, correct_word):
        global number
        number += 1
        #print(number)
        #print("debug triple")

        self.word = guess_word
        # Set to True, but will be switched
        self.guessed_correctly = False
        self.result = self.get_result(correct_word)

    def __str__(self):

        out = f"{self.word}: "
        for letter_result in self.result:
            if letter_result == 2:
                out += "G"
            elif letter_result == 1:
                out += "Y"
            if letter_result == 0:
                out += "_"
        return out

    def get_result(self, correct_word):

        result = [0, 0, 0, 0, 0]
        # we are using a copy to blank guessed green and yellow
        # letters (to correctly display doubles)
        correct_copy = list(correct_word)

        for i, guessed_char in enumerate(self.word):
            if guessed_char == correct_copy[i]:
                result[i] = 2
                correct_copy[i] = ""
        for i, guessed_char in enumerate(self.word):
            if self.word[i] in correct_copy and result[i] != 2:
                result[i] = 1
                for j in range(5):
                    if correct_copy[j] == self.word[i]:
                        correct_copy[j] = ""
                        break
        if result == [2, 2, 2, 2, 2]:
            self.guessed_correctly = True
        return result


class Wordle:

    def __init__(self, correct_word=None):
        global number
        #number += 1
        #print(number)
       # print("debug correct")

        # the word to guess'
        if correct_word in puzzle_words.word_list:
            self.correct_word = correct_word
        else:
            self.correct_word = puzzle_words.get_random_word()

        # list of guesses so far
        self.guesses = []

    def __str__(self):
        out = f"::{self.correct_word}::"
        for i, guess in enumerate(self.guesses):
            out += f"\n{i + 1}. {guess}"
        return out

    def guess(self, word):

        self.guesses.append(Guess(word, self.correct_word))
        # Return True/False if you got the word right
        return self.guesses[-1].guessed_correctly


class Player:
    def __init__(self, guessing_words):
        global number
        number += 1
       # print(number)
        #print("debug guessing")

        self.guessing_words = guessing_words
        self.remaining_words = guessing_words.word_list  # Initialize the list of remaining words


        # Mask
        # Yes mask: this letters should be in these places
        self.yes_mask = [[] for _ in range(5)]
        # No mask: this letters should NOT be in these places
        self.no_mask = [[] for _ in range(5)]
        # Count mask: Word can have (n) such letters
        # [[letters that can be 0 of], [1 of], [2 of], [3 of]]
        self.allowed_mask = [set("abcdefghijklmnopqrstuvwxyz") for _ in range(4)]

        # which letter has to be in the word, from green and yellow letters
        self.must_use = set()
        # copy of the global word set (we'll be removing unfit words from it)
        self.remaining_words = guessing_words.copy()

    def filter_word_list(self):

        self.remaining_words.filter_by_mask(
            self.yes_mask, self.no_mask, self.allowed_mask)

    def reuse_green(self):

        def count_vowels(letters):

            count = 0
            vowels = set(list("aoieu"))
            for letter in letters:
                if letter in vowels:
                    count += 1
            return count

        # Temp Yes mask is empty
        temp_yes_mask = [[] for _ in range(5)]

        # Temp No mask is actual Yes mask
        temp_no_mask = self.yes_mask

        # Prioritize those that are present in all "allowed _mask[1]"
        # (meaning they have never been grey) minus all yellow and greens
        greens_n_yellows = set()
        for letters in self.yes_mask + self.no_mask:
            for letter in letters:
                greens_n_yellows.add(letter)

        # Add vowels if needed
        priority_letters = self.allowed_mask[1].difference(greens_n_yellows)
        letters_for_allowed_mask = priority_letters
        if count_vowels(priority_letters) == 0:
            letters_for_allowed_mask = set.union(priority_letters, set(list("aoe")))

        # Temp Allowed mask: priority letters and some vowels
        # [0] has all letters - any letter can be missed
        temp_allowed_mask = [set("abcdefghijklmnopqurstuvwxyz")] + [
            letters_for_allowed_mask for i in range(3)]

        # Find the word to fit temporary mask, with maximized prioritized letters
        temp_words = guessing_words.copy()
        temp_words.filter_by_mask(temp_yes_mask, temp_no_mask, temp_allowed_mask)
        if len(temp_words) > 0:
            return temp_words.get_maximized_word(list(priority_letters))

        return ""

    def make_guess(self):
        # Use random word if:
        # 1. "scored" is no set
        # 2. "firstrandom" is set and this is the first guess
        # (word list has not been filtered yet)
        if "scored" not in params or "firstrandom" in params and len(self.remaining_words) == len(guessing_words):
            return self.remaining_words.get_random_word()

        # list of masks' lengths
        has_greens = 5 - self.yes_mask.count([])
        # Conditions for "re-use green" logic:
        # has Green; more than 2 potential answers
        if "easymode" in params and has_greens > 0 \
                and len(self.remaining_words) > 2:
            # if reusing green is successful, return that word
            reuse_green_word = self.reuse_green()
            if reuse_green_word != "":
                return reuse_green_word

        # recount / don't recount all scores
        if "recount" in params:
            self.remaining_words.gen_word_scores()
            self.remaining_words.gen_positional_word_scores()

        # use / don't use position letter weights
        if "position" in params:
            return self.remaining_words.get_hiscore_word(use_position=True)
        return self.remaining_words.get_hiscore_word(use_position=False)

    def update_yes_mask(self, guess):
        print(guess)
        for i, letter_result in enumerate(guess.result):
            if letter_result == 2:  # green: should have this letter here

                if guess.word[i] not in self.yes_mask[i]:
                    self.yes_mask[i].append(guess.word[i])

    def update_no_mask(self, guess):

        # Delete the letter in the same place in the mask
        for i, letter_result in enumerate(guess.result):
            if letter_result == 1:  # yellow: should not have this letter here
                if guess.word[i] not in self.no_mask[i]:
                    self.no_mask[i].append(guess.word[i])
            # This is grey, but not the only letter in the word
            if letter_result == 0 and guess.word.count(guess.word[i]) > 1:
                if guess.word[i] not in self.no_mask[i]:
                    self.no_mask[i].append(guess.word[i])

    def update_allowed_mask(self, guess):

        # count colors for each letter, like this
        # {"a":[2,0], "b":[2,1], "c":[0]}
        letter_count = {}
        for i, letter in enumerate(guess.word):
            if letter in letter_count:
                letter_count[letter].append(guess.result[i])
            else:
                letter_count[letter] = [guess.result[i]]

        # Go through each letter count and update count_mask
        for letter, stats in letter_count.items():

            # Case Grey:
            # Word should have no more that {count of other numbers except 0}
            # of this letter. e.g. [0] - none [2,0] - 1, [2,1,0] - 2
            if 0 in stats:
                allowed_count = len(stats) - stats.count(0)
                for i in range(allowed_count + 1, 4):
                    if letter in self.allowed_mask[i]:
                        self.allowed_mask[i].remove(letter)

            # Case Yellow / Green
            # Word should have at leaset {count of 1&2s letters} of these
            if 1 in stats or 2 in stats:
                required_count = stats.count(1) + stats.count(2)
                for i in range(0, required_count):
                    if letter in self.allowed_mask[i]:
                        self.allowed_mask[i].remove(letter)
        return

    def update_mask_with_guess(self, guess):

        self.update_yes_mask(guess)
        self.update_no_mask(guess)
        self.update_allowed_mask(guess)

    def update_mask_with_remaining_words(self):
        # Update allow_mask, knowing letter count of remaining words
        self.remaining_words.gen_letter_count()
        for letter, count in self.remaining_words.letter_count.items():
            # If there is no such words in the whole list
            # remove it from mask
            if count == 0:
                for i in range(1, 3):
                    if letter in self.allowed_mask[i]:
                        self.allowed_mask[i].remove(letter)

    def remove_word(self, word):

        if word in self.remaining_words.word_list:
            self.remaining_words.word_list.remove(word)


def play_one_game(quiet=True, correct_word=None):

    game = Wordle(correct_word)

    player = Player(guessing_words)
    done = False

    print("Starting the game...")

    if correct_word:
        print(f"Correct word set to: {correct_word}")

    # Cycle until we are done
    while not done:
        # Make a guess
        print(game)

        players_guess = player.make_guess()
        print(f"Player's guess: {players_guess}")

        # Play the guess, see if we are done
        if game.guess(players_guess):
            done = True
            print("Guess is correct!")

        # Post-guess action:
        # Remove the words we just played
        player.remove_word(players_guess)
        # print(f"Word {players_guess} removed from possible guesses.")

        # Update mask with guess results
        player.update_mask_with_guess(game.guesses[-1])
        # print("Updated masks with guess results.")

        # Filter the word down according to the new mask
        player.filter_word_list()
        # print(f"Filtered remaining words. {len(player.remaining_words.word_list)} words left.")

        print("Upadted")
        # Update the mask according to remaining words
        player.update_mask_with_remaining_words()
        # print("Updated allowed mask based on remaining words.")

    if not quiet:
        print(game)

    if game.guesses[-1].guessed_correctly:
        print(f"Game won in {len(game.guesses)} turns!")
        return game.guesses
    else:
        print("Game lost.")
        return -1  # This shouldn't happen


def parse_results(results):

    frequencies = {}
    lengths = []
    complete = 0
    turns_sum = 0
    for result in results:
        length = len(result)
        lengths.append(length)
        if length in frequencies:
            frequencies[length] += 1
        else:
            frequencies[length] = 1
        turns_sum += length
        if length <= MAX_TURNS:
            complete += 1

    print(f"Wins: {complete}, Losses: {len(results) - complete}")
    print(f"Winrate: {complete * 100 / len(results):.1f}%")

    if complete > 0:
        print(f"Average length: {turns_sum / len(results):.1f}")

    print(f"Median length: {sorted(lengths)[len(results) // 2]}")


def write_log(results):

    filename = f"wordle_log_{int(time.time())}.txt"
    with open(filename, "w", encoding="utf-8") as log_file:
        for result in results:
            for i, guess in enumerate(result):
                log_file.write(guess.word)
                if i != len(result) - 1:
                    log_file.write(" ")
                else:
                    log_file.write("\n")


def simulation(number_of_runs):

    print(f"Parameters: {params}, Runs: {number_of_runs}")
    simulation_results = []
    words_to_solve = puzzle_words.word_list.copy()

    for _ in range(number_of_runs):
        if number_of_runs == 2315:
            word = words_to_solve.pop()
            simulation_results.append(play_one_game(correct_word=word))
        else:
            simulation_results.append(play_one_game())

    parse_results(simulation_results)
    write_log(simulation_results)


def main():

    start_time = time.time()

    if N_GAMES == 1:
        play_one_game(quiet=False)
    else:
        simulation(N_GAMES)

    print(f"Time: {time.time() - start_time}")


if __name__ == "__main__":
    # Word lists to use:
    # List that wordle game uses as a target word
     #print("debug")

    puzzle_words = WordList("words-guess.txt")
    # List that the "player" program uses
     #print("debug")

    guessing_words = WordList("words-guess.txt", "words-all.txt")

    # Game length (the game will go on, but it will affect the % of wins)
    MAX_TURNS = 6

    # Player's settings:
    # With everything off uses the naive greedy method (limit the potential
    # answers and randomly chose a word from the remaining list)
    # "scored": weight words by the frequency of the words
    #   "recount": recalculate weights for every guess
    #   "firstrandom": random first guess
    #       (worse results but more interesting to watch)
    #   "position": use positional letter weights
    # "easymode": don't have to use current result (reuse green space)


    # Number of games to simulate
    # if == 1, plays one random game, shows how the game went
    # if == 2315, runs simulation for all Wordle words (for deterministic methods)
    # other numbers - play N_GAMES games with random words from puzzle_words
    N_GAMES = 1

    main()
