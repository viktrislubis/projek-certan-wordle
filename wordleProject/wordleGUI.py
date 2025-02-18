import tkinter as tk
from tkinter import messagebox

# Set up the target word for the game
TARGET_WORD = "SOARE"  # You can change this to any word or make it random.

class WordleGame(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Wordle Game")
        self.configure(bg="#ffcccb")

        # Center the window on the screen
        self.center_window(600, 780)

        # Set up the main frame and canvas for scrolling
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame, bg="#ffcccb")
        self.scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a frame for all the content
        self.content_frame = tk.Frame(self.canvas, bg="#ffcccb")
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        # Set up the label at the top
        self.wordle_label = tk.Label(self.content_frame, text="WORDLE", width=8, height=1, font=('Arial', 18), relief="solid",
                                     bg="#ffcccb")
        self.wordle_label.pack(padx=10, pady=10)

        # Create a frame for the guess boxes and center it
        self.guess_frame = tk.Frame(self.content_frame, bg="#ffcccb")
        self.guess_frame.pack(pady=5)  # Center guess frame

        # Create 6 rows of 5 letter boxes (labels)
        self.guess_boxes = []
        for row in range(6):
            row_frame = tk.Frame(self.guess_frame, bg="#ffcccb")
            row_frame.pack(pady=5)  # Pack row frame

            row_boxes = []
            for col in range(5):
                label = tk.Label(row_frame, text="", width=4, height=2, font=("Arial", 24), borderwidth=2,
                                 relief="solid", bg="#ffcccb")
                label.pack(side=tk.LEFT, padx=5, pady=5)  # Pack labels in row frame
                row_boxes.append(label)
            self.guess_boxes.append(row_boxes)

        # Create the virtual keyboard for user to input guesses
        self.create_virtual_keyboard()

        # Update scroll region to encompass the content frame
        self.content_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # Initialize variables to track the current attempt and position
        self.current_row = 0
        self.current_col = 0
        self.max_attempts = 6
        self.max_letters = 5

        # Bind keyboard presses to the window
        self.bind("<Key>", self.on_key_press)

    def center_window(self, width, height):
        """Centers the window on the screen based on the given width and height."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the position of the window
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2) - 40

        # Set the geometry of the window (widthxheight+x+y)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_virtual_keyboard(self):
        """Creates the virtual keyboard below the guess grid."""
        self.keyboard_buttons = {}
        keyboard_frame = tk.Frame(self.content_frame, bg="#ffcccb")
        keyboard_frame.pack(pady=10)

        keys = [
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]

        for key_row in keys:
            row_frame = tk.Frame(keyboard_frame, bg="#ffcccb")
            row_frame.pack(pady=5)
            for key in key_row:
                button = tk.Button(row_frame, text=key, width=4, height=1, font=("Arial", 14),
                                   command=lambda k=key: self.on_key_press(tk.Event(keysym=k)))
                button.pack(side="left", padx=2)
                self.keyboard_buttons[key] = button

        # Center the keyboard frame within the main content frame
        keyboard_frame.pack(pady=10)

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

        # Provide feedback on the guess
        self.get_feedback(guess)

        # If the guess is correct
        if guess == TARGET_WORD:
            messagebox.showinfo("Congratulations!", "You guessed the word correctly!")
            self.reset_game()
            return

        # Move to the next row
        self.current_row += 1
        self.current_col = 0

        if self.current_row == self.max_attempts:
            messagebox.showinfo("Game Over", f"The word was: {TARGET_WORD}")
            self.reset_game()

    def get_feedback(self, guess):
        """Compares the guess to the target word and provides feedback."""
        target_letters = list(TARGET_WORD)
        guess_letters = list(guess)

        # First pass: Check for correct letters (green)
        for i in range(5):
            if guess_letters[i] == target_letters[i]:
                self.guess_boxes[self.current_row][i].config(bg="green")  # Correct position
                self.update_keyboard(guess_letters[i], "green")
                target_letters[i] = None  # Mark as used

        # Second pass: Check for misplaced letters (yellow)
        for i in range(5):
            if guess_letters[i] != TARGET_WORD[i] and guess_letters[i] in target_letters:
                self.guess_boxes[self.current_row][i].config(bg="yellow")  # Wrong position
                self.update_keyboard(guess_letters[i], "yellow")
                target_letters[target_letters.index(guess_letters[i])] = None  # Mark as used
            elif guess_letters[i] != TARGET_WORD[i]:
                self.guess_boxes[self.current_row][i].config(bg="light gray")  # Not in word
                self.update_keyboard(guess_letters[i], "light gray")

    def update_keyboard(self, letter, color):
        """Updates the keyboard button color based on the letter feedback."""
        if letter in self.keyboard_buttons:
            self.keyboard_buttons[letter].config(bg=color)

    def reset_game(self):
        """Resets the game for a new round."""
        self.current_row = 0
        self.current_col = 0
        for row in self.guess_boxes:
            for box in row:
                box.config(text="", bg="#ffcccb")
        # Reset keyboard colors
        for button in self.keyboard_buttons.values():
            button.config(bg="SystemButtonFace")


if __name__ == "__main__":
    app = WordleGame()
    app.mainloop()
