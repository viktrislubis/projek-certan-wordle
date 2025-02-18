import tkinter as tk

root = tk.Tk()

root.geometry("500x500")
root.title("My First GUI")

label = tk.Label(root, text="Hello World!", font=('Arial', 18))
label.pack(padx=20, pady=20)

textbox = tk.Text(root, height=3, font=('Arial', 16))
textbox.pack()

buttonFrame = tk.Frame(root)
buttonFrame.columnconfigure(0, weight=1)
buttonFrame.columnconfigure(1, weight=1)
buttonFrame.columnconfigure(2, weight=1)

btn1 = tk.Button (buttonFrame, text="1", font=('Arial', 18))
btn1.grid(row=0, column=0, sticky="news")

btn2 = tk.Button (buttonFrame, text="2", font=('Arial', 18))
btn2.grid(row=0, column=1, sticky="news")

btn3 = tk.Button (buttonFrame, text="3", font=('Arial', 18))
btn3.grid(row=1, column=0, sticky="news")

btn4 = tk.Button (buttonFrame, text="4", font=('Arial', 18))
btn4.grid(row=1, column=1, sticky="news")

buttonFrame.pack(fill='x')

anotherbtn = tk.Button(root, text ="TEST")
anotherbtn.place(x=200, y =200, height=100, width=100)


root.mainloop()