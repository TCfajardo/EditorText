import os
import tkinter as tk
from tkinter import ttk
import threading
import time
from tkinter import messagebox, filedialog
import enchant #To use this library it was necessary to install it in our python using the command "pip install pyenchant".
import re

class TextEditor:
    """
    This class is a text editor implemented using the tkinter library in Python. 
    The editor has several features such as opening, saving and creating new files, 
    highlighting misspelled words, searching for a word and displaying the most 
    common word in the text.
    
    Author:
        Catalina Fajardo    tania.fajardo01@uptc.edu.co
        Esteban Rincon      esteban.rincon@uptc.edu.co
        Gina Castillo       gina.castillo01@uptc.edu.co
        Zulma Samaca        zulma.samaca@uptc.edu.co
    """
    
    def __init__(self, root):
        """Default constructor.
        Args:
            root (Tk): The root argument is the Tkinter main window object.
        """
        self.root = root
        self.filename = None #indicating that no file is open yet.
        self.text = tk.Text(root, wrap="word")#The wrap="word" parameter causes the text to automatically wrap to the size of the window.
        self.text.pack(side="left", fill="both", expand=True)

        # Add a label to display the file name
        self.filename_label = tk.Label(self.root, text="New Document")
        self.filename_label.pack(side="top")
        self.separator = ttk.Separator(self.root, orient="horizontal")
        self.separator.pack(fill="x", padx=10, pady=10)

        #setting search fields
        self.search_label = tk.Label(self.root, text="Search:")
        self.search_label.pack(side="top", padx=10, pady=5)
        self.search_entry = tk.Entry(self.root)
        self.search_entry.pack(side="top", padx=10, pady=5)
        
        self.search_button = tk.Button(self.root, text="Search", command=self.search_thread)
        self.search_button.pack(side="top", padx=10, pady=5)

        self.highlight_tag = tk.StringVar()
        self.highlight_tag.set("found")
        self.text.tag_config(self.highlight_tag.get(), background="yellow")

        self.stop_event = threading.Event()

        #Buttons replace

        self.replace_entry = tk.Entry(root)
        self.replace_entry.pack(side="top", padx=10, pady=5)

        self.replace_button = tk.Button(self.root, text="Replace", command=self.replace_text)
        self.replace_button.pack(side="top", padx=10, pady=5)

        # Time in seconds between each autosave
        self.auto_save_interval = 10

        self.num_letters_label = tk.Label(root, text="Number of letters: 0")
        self.num_letters_label.pack(side="bottom")
        self.num_words_label = tk.Label(root, text="Number of word: 0")
        self.num_words_label.pack(side="bottom")
        self.most_common_word_label = tk.Label(root, text="Most common word: ")
        self.most_common_word_label.pack(side="bottom")

        self.update_counts(self)
        
        self.mode = "ligth"  # default mode ligth

        # Create a tag to highlight misspelled words
        self.text.tag_configure("misspelled", background="pink")
        # Create a thread to perform spell checking
        self.threadCheckSpelling = threading.Thread(target=self.checkSpelling)
        self.threadCheckSpelling.start()
        # Stop thread when window closes
        root.protocol("WM_DELETE_WINDOW", self.threadCheckSpellingStop)
        # We add the key listener
        self.text.bind("<KeyRelease>", self.update_counts)


    def set_light_theme(self):
        """Sets a clear theme in the graphical user interface of a word processing application.
        """
        self.mode = "ligth"
        self.root.configure(bg="#EAECE9")
        self.text.configure(bg="white", fg="black")
        self.filename_label.configure(bg="#EAECE9", fg="black")
        self.num_letters_label.configure(bg="#EAECE9", fg="black")
        self.num_words_label.configure(bg="#EAECE9", fg="black")
        self.search_label.configure(bg="#EAECE9", fg="black")
        self.most_common_word_label.configure(bg="#EAECE9", fg="black")

    def set_dark_theme(self):
        """"Sets a dark mode in the graphical user interface of a word processing application.
        """
        self.mode = "dark"
        self.root.configure(bg="#909390")
        self.text.configure(bg="#3A3A3A", fg="white")
        self.filename_label.configure(bg="#262626", fg="white")
        self.num_letters_label.configure(bg="#262626", fg="white")
        self.num_words_label.configure(bg="#262626", fg="white")
        self.filename_label.configure(bg="#909390", fg="black")
        self.search_label.configure(bg="#909390", fg="black")
        self.most_common_word_label.configure(bg="#909390", fg="black")
        self.num_letters_label.configure(bg="#909390", fg="black")
        self.num_words_label.configure(bg="#909390", fg="black")

    def checkSpelling(self):
        """ realiza un chequeo ortográfico en un campo de texto.
        """
        self.dictionary = enchant.Dict("en_US")
        while not self.stop_event.is_set():
            # get text
            words = self.text.get("1.0", "end-1c").split()
            #filters out words that are not spelled correctly, using a dictionary to perform a spell check.
            misspelled = []
            for word in words:
                if re.search("[\W_]", word):
                        word  = word[:-1]
                if word and not self.dictionary.check(word):
                    misspelled.append(word)

            #highlight misspelled words
            self.text.tag_remove("misspelled", "1.0", "end")
            for word in misspelled:
                start = "1.0"
                while True:
                    pos = self.text.search(word, start, "end", nocase=1)
                    if not pos:
                        break
                    end = f"{pos}+{len(word)}c"
                    self.text.tag_add("misspelled", pos, end)
                    start = end
            
            # Wait before checking again
            time.sleep(1)

    def threadCheckSpellingStop(self):
        """Sets the stop event and destroys the root window.

        This method sets the stop event to notify the spelling checker to stop
        running and destroys the root window to close the application.
        Returns:
        None.
        """
        self.stop_event.set()
        self.root.destroy()


    def calculate_num_letters(self, text):
        """
        The above code defines functions to calculate the number of letters and words in a given text, and
        updates the corresponding labels in a GUI, while also creating threads to calculate the most common
        word and automatically save the text.
        
        :param text: The text to be analyzed for calculating the number of letters, number of words, and the
        most common word
        """
        """counts the number of letters in the text received as a parameter 
        (ignoring blanks) and then updates the num_letters_label tag to 
        display the number of letters in the GUI.
        Args:
            text (String): the text to be analyzed
        """
        exclude = [ ' ','.', ',', ';', ':', '!', '¡', '?', '¿', '"', "'", '(', ')', '[', ']', '{', '}', '-', '_', '+', '=', '*', '/', '<', '>', '\\', '|', '@', '#', '$', '%', '^', '&', '`', '~']
        num_letters = len([ch for ch in text if ch not in exclude])
        self.num_letters_label.config(text=f"Number of letters: {num_letters}")
        
    def calculate_num_words(self, text):
        """calculates the number of words in the text provided as an argument.
        converts the text into a list of words using the split() method, 
        and then counts the number of items in the list using the len() function. 
        It then updates the num_words_label in the GUI with the number of words counted.
        Args:
            text (String): the text to be analyzed
        """
        exclude = [ '.', ',', ';', ':', '!','¡', '?','¿', '"', "'", '(', ')', '[', ']', '{', '}', '-', '_', '+', '=', '*', '/', '<', '>', '\\', '|', '@', '#', '$', '%', '^', '&', '`', '~']
        words = [word for word in text.split() if word not in exclude]
        num_words = len(words)
        self.num_words_label.config(text=f"Number of words: {num_words}")


    def update_counts(self, event=None):
        """updates the statistics of characters, words and the most common 
        word in the word processor.
        Args:
            event (self, optional): event is optional and defaults to None. 
            It is used to detect events occurring in the application that may 
            trigger a statistics update. Defaults to None.
        """
        text = self.text.get("1.0", "end-1c")
        # Create threads to calculate the number of letters and the number of words
        t1 = threading.Thread(target=self.calculate_num_letters, args=(text,))
        t2 = threading.Thread(target=self.calculate_num_words, args=(text,))
        t1.start()
        t2.start()

        # Create a thread to calculate the most common word
        t = threading.Thread(target=self.calculate_most_common_word, args=(text,))
        t.start()

        # Automatically save
        if self.filename:
            with open(self.filename, "w") as file:
                file.write(text)
                
    def calculate_most_common_word(self, text):
        """Calculates the most common word in the given text and updates the UI.
        This method processes the given text by removing certain punctuation marks
        and splitting it into individual words. It then counts the occurrences of
        each word and returns the most common word. Additionally, it updates the
        UI by calling the 'update_most_common_word' method with the most common
        word as an argument.

        Args:
            text (str): The text to process.

        Returns:
            str: The most common word in the text, or an empty string if the text
        contains no words.
        """
        # Define a list of punctuation marks to exclude from the text
        exclude = [ '.', ',', ';', ':', '!','¡', '?','¿', '"', "'", '(', ')','[', ']', '{', '}', '-', '_', '+', '=', '*', '/', '<', '>','\\', '|', '@', '#', '$', '%', '^', '&', '`', '~']

        # Remove the punctuation marks from the text
        for e in exclude:
            text = text.replace(e, "")

        # Split the text into individual words
        words = text.split()

        # If there are no words, return an empty string
        if len(words) == 0: 
            return ""

        # Count the occurrences of each word and find the most common one
        counter = {}
        for word in words:
            counter[word] = counter.get(word, 0) + 1
        most_common_word = max(counter, key=counter.get)

        # Update the UI with the most common word
        self.root.after(0, self.update_most_common_word, most_common_word)

        # Return the most common word
        return most_common_word

    def update_most_common_word(self, most_common_word):
        """Updates the UI to display the most common word.
        This method updates the UI by setting the text of the 'most_common_word_label'
        widget to display the most common word.
        Args:
            most_common_word (str): The most common word to display.
        """
        self.most_common_word_label.config(text=f"Most common word: {most_common_word}")

    def new_file(self):
        """Clears the current text and sets the filename to None.
        This method clears the current text in the editor and sets the filename to
        None, indicating that no file is currently open.
        """
        self.filename = None
        self.text.delete("1.0", "end")


    def open_file(self):
        """Opens a file and displays its contents in the editor.
        """
        self.filename = filedialog.askopenfilename(filetypes=[("Text files", ".txt"), ("All files", ".*")])
        if self.filename:
            with open(self.filename, "r") as file:
                text = file.read()
                self.text.delete("1.0", "end")
                self.text.insert("1.0", text)
            self.filename = self.filename
            self.filename_label.config(text=os.path.basename(self.filename))
            self.update_counts(self)


    def save_file(self):
        """Saves the current contents to the current file.
        This method saves the current contents of the editor to the current file.
        If no file is currently open, this method calls the save_file_as method.
        """
        if self.filename:
            with open(self.filename, "w") as file:
                file.write(self.text.get("1.0", "end"))
            self.filename_label.config(text=os.path.basename(self.filename))
        else:
            self.save_file_as()


    def auto_save_worker(self):
        """Automatically saves the contents of the editor at a set interval.
        This method is a worker thread that automatically saves the contents of the
        editor at a set interval. The interval is set by the auto_save_interval
        attribute.
        """
        while True:
            # Wait for the auto-save interval
            time.sleep(self.auto_save_interval)

            # Save the contents to the file
            self.save_file()


    def search_thread(self):
        # Get the text to search for
        search_text = self.search_entry.get()

        # If there is no text to search, do nothing
        if not search_text:
            return

        # Start a thread to search the text in the background
        threading.Thread(target=self.search_text, args=(search_text,)).start()

    def search_text(self, search_text):
        # Remove any previous highlights
        self.text.tag_remove(self.highlight_tag.get(), "1.0", tk.END)

        # get all text
        text = self.text.get("1.0", tk.END)

        # Find all occurrences of the text and highlight them
        start = "1.0"
        while True:
            # Find the next occurrence of the text
            start = self.text.search(search_text, start, tk.END)

            # If no more occurrences were found, exit the loop
            if not start:
                break

            # highlight occurrence
            end = f"{start}+{len(search_text)}c"
            self.text.tag_add(self.highlight_tag.get(), start, end)

            # Move the starting point to find the next occurrence
            start = end
    
    def replace_text(self):
        """searches for the word entered in the search field and replaces it with the word entered in the replace field.
        """
        query = self.search_entry.get()
        replace_with = self.replace_entry.get()
        if query:
            if not replace_with:
                messagebox.showwarning("Empty replace field", "Please enter a replacement term.")
                return
            start = "1.0"
            while True:
                pos = self.text.search(query, start, "end", nocase=1)
                if not pos:
                    messagebox.showinfo("End of document", "No more occurrences found.")
                    break
                end = f"{pos}+{len(query)}c"
                self.text.delete(pos, end)
                self.text.insert(pos, replace_with)
                start = pos
                self.text.mark_set("insert", pos)
                self.text.see("insert")
                self.text.focus()
        else:
            messagebox.showwarning("Empty search field", "Please enter a search term.")
    

    def show_most_common_word(self):
        """Shows a message box with the most common word in the text.

        This function extracts the text from the text widget and removes
        punctuation marks from it. It then splits the text into a list of
        words and creates a dictionary to count the frequency of each word.
        The most common word is determined by finding the key with the highest
        value in the dictionary. A message box is then displayed showing the
        most common word and the number of times it appears in the text.
        """
        text = self.text.get("1.0", "end-1c")
        exclude = [ '.', ',', ';', ':', '!','¡', '?','¿', '"', "'", '(', ')', '[', ']', '{', '}', '-', '_', '+', '=', '*', '/', '<', '>', '\\', '|', '@', '#', '$', '%', '^', '&', '`', '~']
        for e in exclude:
            text = text.replace(e, "")
        if len(text) == 0:
            messagebox.showinfo("Most common word", "No text to parse.")
            return
        words = text.split()
        counter = {}
        for word in words:
            counter[word] = counter.get(word, 0) + 1
        most_common_word = max(counter, key=counter.get)
        messagebox.showinfo("Most common word", f"The most common word is '{most_common_word}' and appears {counter[most_common_word]} times.")


    def save_file_as(self):
        """
        Opens a file dialog window and allows the user to save the current text in the Text widget as a file.
        The file extension is set to .txt by default, but the user can select other file types as well.
        The method also creates a new thread to save the file automatically.
        """
        self.filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", ".txt"), ("All Files", ".*")])
        if self.filename:
            with open(self.filename, "w") as file:
                file.write(self.text.get("1.0", "end"))
                # Create thread for auto-saving"
                self.auto_save_thread = threading.Thread(target=self.auto_save_worker, daemon=True)
                self.auto_save_thread.start()

    def exit(self):
        """_summary_
        """
        if messagebox.showinfo("Exit" ,"Are you sure you want to get out?"):
            self.root.destroy()

if __name__ == "__main__":
    # Create the root window for the application
    root = tk.Tk()
    root.title("My word processor")
    root.geometry("800x500")

    # Create an instance of the TextEditor class and pass the root window as argument
    text_editor = TextEditor(root)

    # Create the menu bar and menus for File, Statistics, and Theme
    menu_bar = tk.Menu(root)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="New", command=text_editor.new_file)
    file_menu.add_command(label="Open", command=text_editor.open_file)
    file_menu.add_separator()
    file_menu.add_command(label="Save", command=text_editor.save_file)
    file_menu.add_command(label="Save as...", command=text_editor.save_file_as)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=text_editor.exit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    stats_menu = tk.Menu(menu_bar, tearoff=0)
    stats_menu.add_command(label="Most common word", command=text_editor.show_most_common_word)
    menu_bar.add_cascade(label="Statistics", menu=stats_menu)

    theme_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Theme", menu=theme_menu)
    theme_menu.add_command(label="Light mode", command=text_editor.set_light_theme)
    theme_menu.add_command(label="Dark mode ", command=text_editor.set_dark_theme)

    # Configure the root window to use the menu bar
    root.config(menu=menu_bar)

    # Start the main event loop
    root.mainloop()
