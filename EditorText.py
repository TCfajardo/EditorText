import os
import tkinter as tk
from tkinter import ttk
from tkinter import *
import threading
import time
from tkinter import messagebox, filedialog
import enchant
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

        self.replace_button = Button(self.root, text="Replace", command=self.replace_text)
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

        # Crear una etiqueta para resaltar las palabras mal escritas
        self.text.tag_configure("misspelled", background="pink")
        # Crear un hilo para realizar la verificación ortográfica 
        self.threadCheckSpelling = threading.Thread(target=self.checkSpelling)
        self.threadCheckSpelling.start()
        # Detener el hilo cuando se cierra la ventana
        root.protocol("WM_DELETE_WINDOW", self.threadCheckSpellingStop)
        # Agregamos el key listener
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
        self.dictionary = enchant.Dict("en_US")
        while not self.stop_event.is_set():
            # obtener texto
            words = self.text.get("1.0", "end-1c").split()
            #filtra las palabras que no están correctamente escritas, utilizando un diccionario para realizar la verificación de ortografía.
            misspelled = []
            for word in words:
                if re.search("[\W_]", word):
                        word  = word[:-1]
                if word and not self.dictionary.check(word):
                    misspelled.append(word)

            #resaltar palabras mal escritas
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
            
            # Esperar antes de verificar nuevamente
            time.sleep(1)

    def threadCheckSpellingStop(self):
        self.stop_event.set()
        self.root.destroy()

    def calculate_num_letters(self, text):
        """counts the number of letters in the text received as a parameter 
        (ignoring blanks) and then updates the num_letters_label tag to 
        display the number of letters in the GUI.
        Args:
            text (String): the text to be analyzed
        """
        letters_only = re.sub(r'[^a-zA-Z]', '', text)
        num_letters = len(letters_only)
        self.num_letters_label.config(text=f"Number of letters: {num_letters}")

    def calculate_num_words(self, text):
        """calculates the number of words in the text provided as an argument.
        converts the text into a list of words using the split() method, 
        and then counts the number of items in the list using the len() function. 
        It then updates the num_words_label in the GUI with the number of words counted.
        Args:
            text (String): the text to be analyzed
        """
        words_only = re.findall(r'\b[a-zA-Z]+\b', text)
        num_words = len(words_only)
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
        num_letters = len(text.replace(" ", ""))
        num_words = len(text.split())
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
        words = text.split()
        if len(words) == 0: 
            return ""
        counter = {}
        for word in words:
            counter[word] = counter.get(word, 0) + 1
        most_common_word = max(counter, key=counter.get)
        self.root.after(0, self.update_most_common_word, most_common_word)
        
    def update_most_common_word(self, most_common_word):
        self.most_common_word_label.config(text=f"Most common word: {most_common_word}")

    def new_file(self):
        self.filename = None
        self.text.delete("1.0", "end")

    def open_file(self):
        self.filename = filedialog.askopenfilename(filetypes=[("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")])
        if self.filename:
            with open(self.filename, "r") as file:
                text = file.read()
                self.text.delete("1.0", "end")
                self.text.insert("1.0", text)
            self.filename = self.filename
            self.filename_label.config(text=os.path.basename(self.filename))
            self.update_counts(self)

    def save_file(self):
        if self.filename:
            with open(self.filename, "w") as file:
                file.write(self.text.get("1.0", "end"))
        else:
            self.save_file_as()

    def auto_save_worker(self):
        while True:
            # Wait for auto-save time
            time.sleep(self.auto_save_interval)

            # Save content to file
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
        text = self.text.get("1.0", "end-1c")
        words = text.split()
        if len(words) == 0:
            messagebox.showinfo("Most common word", "No text to parse.")
            return
        counter = {}
        for word in words:
            counter[word] = counter.get(word, 0) + 1
        most_common_word = max(counter, key=counter.get)
        messagebox.showinfo("Most common word", f"The most common word is '{most_common_word}' and appears {counter[most_common_word]} times.")


    def save_file_as(self):
        self.filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if self.filename:
            with open(self.filename, "w") as file:
                file.write(self.text.get("1.0", "end"))
                # Crear hilo para guardar automáticamente
                self.auto_save_thread = threading.Thread(target=self.auto_save_worker, daemon=True)
                self.auto_save_thread.start()

    def exit(self):
        if messagebox.askyesno("Exit" ,"Are you sure you want to get out?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("My word processor")
    root.geometry("800x500")

    text_editor = TextEditor(root)
        # Crear el menú
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

    # Crear el menú de estadísticas
    stats_menu = tk.Menu(menu_bar, tearoff=0)
    stats_menu.add_command(label="Most common word", command=text_editor.show_most_common_word)
    menu_bar.add_cascade(label="Statistics", menu=stats_menu)

    theme_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Theme", menu=theme_menu)
    theme_menu.add_command(label="Light mode", command=text_editor.set_light_theme)
    theme_menu.add_command(label="Dark mode ", command=text_editor.set_dark_theme)

    root.config(menu=menu_bar)
    root.mainloop()