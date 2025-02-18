import tkinter as tk
from tkinter import messagebox
from wordle import Wordle, Player, WordList, Guess
import random

class WordleGame(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Wordle Game")
        self.center_window(600, 780)
        self.configure(bg="#ffcccb")

        self.canvas = tk.Canvas(self, bg="#ffcccb")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', self.center_content)

        self.content_frame = tk.Frame(self.canvas, bg="#ffcccb")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="n")

        self.guess_boxes = []
        for row in range(6):
            row_boxes = []
            for col in range(5):
                label = tk.Label(self.content_frame, text="", width=4, height=2, font=("Arial", 24), borderwidth=2,
                                 relief="solid", bg="#ffcccb")
                label.grid(row=row, column=col, padx=0, pady=5)
                row_boxes.append(label)
            self.guess_boxes.append(row_boxes)

        self.keyboard_buttons = {}  # Dictionary to hold keyboard button references
        self.create_virtual_keyboard()

        self.current_row = 0
        self.current_col = 0
        self.max_attempts = 6
        self.max_letters = 5

        self.bind("<Key>", self.on_key_press)

        self.puzzle_word = WordList("words-guess.txt")
        self.guessing_words = WordList("words-guess.txt", "words-all.txt")

        self.wordle = Wordle()
        self.player = Player(self.guessing_words)

        self.target_word = random.choice(self.puzzle_word.word_list)

        self.bot_button = tk.Button(self.content_frame, text="Make Guess", command=self.bot_make_guess, font=("Arial", 12), width=10, height=2)
        self.bot_button.grid(row=7, column=0, columnspan=5, pady=10)

        # Initialize the keyboard color mapping
        self.keyboard_colors = {chr(i): "#ffcccb" for i in range(ord('A'), ord('Z') + 1)}  # Default colors for all letters

    def on_key_press(self, event):
        """Handle key press from both physical and virtual keyboard."""
        key = event.keysym.upper()

        # Handle letter input
        if key.isalpha() and len(key) == 1 and self.current_col < self.max_letters:
            self.guess_boxes[self.current_row][self.current_col].config(text=key)
            self.current_col += 1

        # Handle Backspace
        elif key == "BACKSPACE" and self.current_col > 0:
            self.current_col -= 1
            self.guess_boxes[self.current_row][self.current_col].config(text="")

        # Handle Enter
        elif key == "RETURN" and self.current_col == self.max_letters:
            self.submit_guess()

    def submit_guess(self):
        """Submit the current guess and move to the next row."""
        guess = "".join([self.guess_boxes[self.current_row][col].cget("text") for col in range(5)])

        if len(guess) != 5:
            messagebox.showwarning("Invalid Input", "Please enter a 5-letter word.")
            return

        # Create a Guess object to evaluate the guess
        guess_object = Guess(guess, self.target_word)

        # Provide feedback on the guess
        self.get_feedback(guess_object)

        # Update player knowledge based on the guess and feedback
        self.player.update_mask_with_guess(guess_object)

        # If the guess is correct
        if guess_object.guessed_correctly:
            messagebox.showinfo("Congratulations!", "You guessed the word correctly!")
            self.reset_game()
            return

        # Move to the next row
        self.current_row += 1
        self.current_col = 0

        if self.current_row == self.max_attempts:
            messagebox.showinfo("Game Over", f"The word was: {self.target_word}")
            self.reset_game()

    def create_virtual_keyboard(self):
        """Creates the virtual keyboard below the guess grid."""
        keyboard_frame = tk.Frame(self.content_frame, bg="#ffcccb")
        keyboard_frame.grid(row=6, column=0, columnspan=5, pady=10)

        keys = [
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]

        for key_row in keys:
            row_frame = tk.Frame(keyboard_frame, bg="#ffcccb")
            row_frame.pack(pady=5)
            for key in key_row:
                button = tk.Button(row_frame, text=key, width=4, height=1, font=("Arial", 14), state=tk.NORMAL)  # Set to NORMAL
                button.pack(side="left", padx=2)
                self.keyboard_buttons[key] = button  # Store button references

    def get_feedback(self, guess_object):
        """Updates the GUI based on the feedback from the Guess object."""
        result = guess_object.result
        print(guess_object)

        for i, letter_result in enumerate(result):
            letter = guess_object.word[i]  # Get the letter being evaluated
            if letter_result == 2:
                self.guess_boxes[self.current_row][i].config(bg="green")  # Correct position (green)
                self.update_keyboard_color(letter, "green")
            elif letter_result == 1:
                self.guess_boxes[self.current_row][i].config(bg="yellow")  # Wrong position (yellow)
                self.update_keyboard_color(letter, "yellow")
            else:
                self.guess_boxes[self.current_row][i].config(bg="light gray")  # Not in word (gray)
                self.update_keyboard_color(letter, "light gray")

    def update_keyboard_color(self, letter, color):
        """Updates the color of the virtual keyboard button for the given letter."""

        if letter.upper() in self.keyboard_buttons:
            current_color = self.keyboard_colors[letter.upper()]


            # Determine the new color
            if current_color == "#ffcccb" or current_color == "light gray":  # Default or gray letters can change
                self.keyboard_buttons[letter.upper()].config(bg=color)
                self.keyboard_colors[letter.upper()] = color  # Update the stored color
            elif current_color == "yellow" and color == "green":
                self.keyboard_buttons[letter.upper()].config(bg=color)  # Green overrides yellow
                self.keyboard_colors[letter.upper()] = color

    def reset_game(self):
        """Resets the game for a new round."""
        self.current_row = 0
        self.current_col = 0
        for row in self.guess_boxes:
            for box in row:
                box.config(text="", bg="#ffcccb")

        guessing_words = WordList("words-guess.txt", "words-all.txt")
        self.target_word = random.choice(guessing_words.word_list)

        self.reset_player()

    def reset_player(self):
        """Resets the player object with a fresh word list and allowed mask."""
        guessing_words = WordList("words-guess.txt", "words-all.txt")
        self.player = Player(guessing_words)

    def bot_make_guess(self):
        """Makes a guess using the bot and displays it in the GUI."""
        if self.current_row < self.max_attempts:
            players_guess = self.player.make_guess()

            for col in range(self.max_letters):
                self.guess_boxes[self.current_row][col].config(text=players_guess[col])

            guess_object = Guess(players_guess, self.target_word)

            self.player.update_mask_with_guess(guess_object)
            self.player.remove_word(players_guess)

            self.player.filter_word_list()
            self.player.update_mask_with_remaining_words()

            self.get_feedback(guess_object)

            self.current_row += 1
            self.current_col = 0

            if guess_object.guessed_correctly:
                messagebox.showinfo("Congratulations!", "The bot guessed the word correctly!")
                self.reset_game()

            if self.current_row == self.max_attempts:
                messagebox.showinfo("Game Over", f"The word was: {self.target_word}")
                self.reset_game()

    def center_window(self, width, height):
        """Centers the window on the screen based on the given width and height."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def center_content(self, event):
        """Centers the content when the window is resized."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    game = WordleGame()
    game.mainloop()
