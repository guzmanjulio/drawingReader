import fitz
import re
import colorsys
from tkinter import *
from tkinter import filedialog  # Import for file dialog
from tkinter import ttk
from datetime import datetime
#cambio
#pattern = r"\b([TMSFP]|[a-zA-Z]{1,4})(?:\s?\-?\s?|-)?([0-9]{1,4})(?:[a-zA-Z]?)\b"
#pattern = r"\b([TMSFPH]|[a-zA-Z]{1,4}(?:\s?\-?\s?|-)?\d{1,4}(?:\s?\-?\s?|-)?(?:[a-zA-Z])?)\b"
pattern = r"\b([TMSFPH]|[A-Za-z]{1,4}(?: [-]? |[- ])?\d{1,4}(?: [-]? |[- ])?[A-Za-z0-9]{1,2}|[A-Za-z]{1,4}[ ]*?-[ ]*?[A-Za-z0-9]{1,4}|)\b"

file_path = ""
type_of_units = []
generic_TAGs = ["AHU", "AH", "BC", "BCU", "CHWP", "CU", "CUH", "CWP", "EF", "ERU", "ERV", "FC", "FCU", "FP", "H", "HWP", "M", "RTU", "S", "SF", "T", "UH", "VAV", "VV"]

class MultiSelectListbox:
  """
  This class creates a form control with two Listboxes for multi-selection.
  Items are moved from the first list to the second upon selection.
  """
  def __init__(self, master, items):
    self.master = master
    self.items = items
    self.selected_items = []

    # Create frames for listboxes
    self.frame1 = ttk.Frame(master)
    self.frame1.pack(side=LEFT, padx=5, pady=5)
    self.frame2 = ttk.Frame(master)
    self.frame2.pack(side=LEFT, padx=5, pady=5)
 
    # Create labels for listboxes
    self.label1 = ttk.Label(self.frame1, text="Available Tags:", width=35)
    self.label1.pack()
    self.label2 = ttk.Label(self.frame2, text="Selected Tags:", width=35)
    self.label2.pack()

    # Create scrollbars
    self.scrollbar1 = ttk.Scrollbar(self.frame1)
    self.scrollbar1.pack(side=RIGHT, fill=Y)
    self.scrollbar2 = ttk.Scrollbar(self.frame2)
    self.scrollbar2.pack(side=RIGHT, fill=Y)

    # Create listboxes with scrollbars
    self.listbox1 = Listbox(self.frame1, yscrollcommand=self.scrollbar1.set)
    for item in self.items:
      self.listbox1.insert(END, item)
    self.listbox1.pack(fill=BOTH, expand=True)
    self.scrollbar1.config(command=self.listbox1.yview)
    self.listbox1.bind("<<ListboxSelect>>", self.on_select1)

    self.listbox2 = Listbox(self.frame2, yscrollcommand=self.scrollbar2.set)
    self.listbox2.pack(fill=BOTH, expand=True)
    self.scrollbar2.config(command=self.listbox2.yview)
    self.listbox2.bind("<<ListboxSelect>>", self.on_select2)

  def on_select1(self, event):
    """
    This function handles selection events in the first listbox
    and moves selected items to the second listbox.
    """
    selected_indices = self.listbox1.curselection()
    selected_items = [self.listbox1.get(index) for index in selected_indices]  # Get selected items

    for item in selected_items:
      # Delete from first listbox **after** adding to second list to avoid index shift
      self.listbox2.insert(END, item)
      self.listbox1.delete(self.listbox1.get(0, END).index(item))
      self.selected_items.append(item)  # Update selected items list

  def on_select2(self, event):
    """
    This function handles selection events in the first listbox
    and moves selected items to the second listbox.
    """
    selected_indices = self.listbox2.curselection()
    selected_items = [self.listbox2.get(index) for index in selected_indices]  # Get selected items

    for item in selected_items:
      # Delete from first listbox **after** adding to second list to avoid index shift
      self.listbox1.insert(END, item)
      self.listbox2.delete(self.listbox2.get(0, END).index(item))
      self.selected_items.append(item)  # Update selected items list

  def get_all_items_listbox2(self):
      """
      This function returns a list of all items in the second listbox.
      """
      return self.listbox2.get(0, END)

  def select_item(self, item_text):
    """
    This function simulates selection for a specific item in the first listbox.
    """
    index = self.listbox1.get(0, END).index(item_text)  # Find item index
    if index != -1:  # Check if item exists
      self.listbox1.selection_set(index)  # Set selection for the index
      self.listbox1.see(index)  # Ensure the item is visible in the listbox
      self.on_select1(event=None)  # Manually trigger the on_select1 function



  def add_item(self, new_item):
    """
    This function adds a new item to the first listbox programmatically.
    """
    self.items.append(new_item)
    self.listbox1.insert(END, new_item)

  # Additional methods for functionality (optional)
  def get_selected_items(self):
    """
    This method (optional) returns a list of currently selected items.
    """
    return self.selected_items

  def clear_selected_items(self):
    """
    This method (optional) clears the list of selected items and the second listbox.
    """
    self.selected_items.clear()
    self.listbox2.delete(0, END)
  
  #End of class MultiselectListbox



def get_spectrum_colors(names):
  """
  Generates a dictionary of colors across the visual spectrum for a list of names.

  Args:
      names: A list of strings as keys for the color dictionary.

  Returns:
      A dictionary where keys are the names from the input list and values are RGB color tuples.
  """
  # Ensure unique names (avoiding duplicate colors)
  names = list(set(names))

  # Calculate the number of color steps (one for each name)
  num_colors = len(names)
  
  if num_colors < 2:
    step_size = 1
  else:
    step_size = 1.0 / (num_colors - 1)  # Normalize step size across the spectrum (0 to 1)

  # Generate hues linearly across the spectrum, starting from red
  hues = [i * step_size for i in range(num_colors)]

  # Convert hues to RGB colors with high saturation and medium brightness
  colors = [colorsys.hsv_to_rgb(h, 1, 1) for h in hues]
  return dict(zip(names, colors))

def get_first_letters(text):
  """
  This function extracts the first letters of a word made by letters and numbers.

  Args:
      text: The string to analyze.

  Returns:
      A string containing only the first letters of the word, or an empty string if no letters are found.
      Examples:
        "VAV123"    returns "VAV"
        "AHU - 456" returns "AHU"
        "EF-78H"     returns "EF"
  """
  first_letters = ""
  for char in text:
    if char.isalpha():
      first_letters += char
    else:
       break
  
  return first_letters


def get_type_of_units(pattern, file_path):
     # Open the PDF file
    pdf_document = fitz.open(file_path)

    # Compile the regular expression pattern
    regex = re.compile(pattern)

    # Variable to store all matches
    all_matches = []

    # Iterate through each page in the PDF
    for page_index in range(len(pdf_document)):
        # Get the current page
        page = pdf_document[page_index]

        # Get the text of the page
        page_text = page.get_text()

        # Search for matches using the regular expression pattern
        matches = regex.findall(page_text)
        
        # Store matches in the variable
        all_matches.extend(matches)

    # Close the PDF document
    pdf_document.close()

    all_matches = list(set(all_matches))
    
    type_of_units = list(map(lambda x: get_first_letters(x), all_matches))
    type_of_units = sorted(set(type_of_units))

    for unit in type_of_units:
      listbox_control.add_item(unit)
      if unit in generic_TAGs:
         listbox_control.select_item(unit)

    return type_of_units

    

def highlight_specific_pattern(pattern):
  
    labelmark.config(text = "Done")
    
    type_of_units = listbox_control.get_all_items_listbox2()
    """
    Aquí tenemos que crear type_of_units-de-1-letra y type_of_units-de-mas-letras
    para luego usar las de 1 letra para las t,m,p,etc y las de más letras para las VAV, AHU, EF, etc
    """
    color_dict = get_spectrum_colors(type_of_units)
    file_path = label.cget("text")

    # Open the PDF file
    pdf_document = fitz.open(file_path)

    # Compile the regular expression pattern
    regex = re.compile(pattern)

    # Maintain a set to store unique patterns
    unique_patterns = set()
    set_of_found_tags = set()
    if(1):
      # Iterate through each page in the PDF
      for page_index in range(len(pdf_document)):
        # Get the current page
        page = pdf_document[page_index]
        
        # Get the text of the page
        bloques_blocks = page.get_text("blocks") #check if "blocks" works better for special tags like inside a pokeball
        bloques_words  = page.get_text("words")
        
        
        tables = page.find_tables() #USE THIS IN THE FUTURE TO GET TABLE LOCATIONS AND AVOID HIGHLIGHTING TAGS ON SCHEDULES.
        #for table in tables:
          # Extract table boundaries
          

        type_of_units_1_letter = set(filter(lambda s: len(s) == 1, type_of_units))
        type_of_units_X_letter = set(filter(lambda s: len(s) >  1, type_of_units))
                                     
        nested_fors(type_of_units_1_letter, regex, unique_patterns, set_of_found_tags, page, bloques_words , color_dict)  
        nested_fors(type_of_units_X_letter, regex, unique_patterns, set_of_found_tags, page, bloques_blocks, color_dict)  
      
      set_of_found_tags = sorted(set_of_found_tags)
      print(set_of_found_tags)
      
      # Save the modified PDF without incremental mode
      output_path = file_path[:-4] + " - Mk " + datetime.now().strftime("%y-%m-%d %H-%M-%S") + ".pdf"
      pdf_document.save(output_path, garbage=4)
      labelmark.config(text = "Done")

    # Close the PDF document
    pdf_document.close()

def nested_fors(type_of_units, regex, unique_patterns, set_of_found_tags, page, bloques, color_dict):
    for i,bloque in enumerate(bloques):
        x0, y0, x1, y1, texto, *_ = bloque
            
        for match in regex.finditer(texto):
            if get_first_letters(match.string) in type_of_units:
              texto_encontrado = match.group()

              text_instances = page.search_for(texto_encontrado)
              if len(get_first_letters(texto_encontrado)) == 1 and len(texto_encontrado) > 1:
                 continue

              if text_instances is None: #not sure what happened. I started getting errors because text_instances was a none_type... :(
                 continue

              for inst in text_instances:
                  if inst not in unique_patterns:
                      if (inst.x0 >= x0 and inst.x1 <= x1 and inst.y0 >= y0 and inst.y1 <= y1): #check if this should be '==' instead of '>='
                          unique_patterns.add(inst) #sometimes the names repeat themselves and the script ends adding several comments. To avoid this, we keep track of the markups
                          try:
                            color = color_dict[get_first_letters(texto_encontrado)] #DO NOT DELETE! This ensures that the possible error is captured before highlighting on the following line
                            highlight = page.add_highlight_annot(inst)
                            highlight.set_colors({'stroke': color})
                            set_of_found_tags.add(texto_encontrado)
                            highlight.set_info({'title':"Auto Comentador", 'content':texto_encontrado})
                            match texto_encontrado:
                              case "T":
                                  highlight.set_info({'subject':'Space Temperature Sensor'})
                              case "M":
                                  highlight.set_info({'subject':'Motorized Damper'})
                              case "H":
                                  highlight.set_info({'subject':'Humidity Sensor'})
                              case "S":
                                  highlight.set_info({'subject':'Sensor'})
                              case _:
                                  highlight.set_info({'subject':get_first_letters(texto_encontrado)})
                          except:
                              highlight.set_info({'subject':"PROBLEMA EN CODIGO"})
                             #pass
                                 
                          highlight.set_opacity(0.67)
                          highlight.update()

    
def get_regex_format(text_example):
  """
  This function attempts to extract a potential regex format from a text example
  by iterating over characters and classifying them.

  Args:
      text_example (str): A string representing the text example.

  Returns:
      str: A potential regex format based on the text example, 
          or None if no clear pattern is found.
  """
  regex_parts = []

  for char in text_example:
    if char.isalpha():
      regex_parts.append("[a-zA-Z]")  # Letters
    elif char.isdigit():
      regex_parts.append("[0-9]")  # Numbers
    elif char in " -":
      regex_parts.append(re.escape(char))  # Escaped separators (space or hyphen)
    else:
      # Handle other characters (might need adjustment based on your use case)
      return None  # Indicate no clear pattern if unexpected characters are found
  
  # Combine regex parts into a single format
  return "".join(regex_parts)
  


def get_file_path(pattern):
  """Opens a file dialog and returns the selected file path."""
  """
  ###############################################
  #Get the pattern from an example on the textbox
  text = text_box.get("1.0", END)  # Get text from Text widget. First argument is initial LINE.CHARACTER, Second argument is final LINE.CHARACTER
  lines = text.splitlines()  # Split text by newlines
  patterns = []
  
  for line in lines:
    patterns.append(get_regex_format(line))
  
  pattern = "|".join(patterns)
  pattern = r"\b(" + pattern + r")\b"
  ###############################################
  """
  
  file_path = filedialog.askopenfilename(title="Select a file")
  if file_path:
    type_of_units = get_type_of_units(pattern, file_path)
    label.config(text = file_path)
    highlight_button.pack(pady=10)
    


# Create the main window
window = Tk()
window.title("Auto Drawing Markup")
window.geometry("500x500")  # Adjust width and height as needed

# Create the label for the text box
label = Label(window, text="Select file path:")
label.pack()

# Create button to get file path
get_file_button = Button(window, text="Get File Path", command= lambda: get_file_path(pattern))
get_file_button.pack()

# Create button to highlight TAGs
highlight_button = Button(window, text="Highlight TAGs", command= lambda: highlight_specific_pattern(pattern))
highlight_button.pack()

labelmark = Label(window, text="")
labelmark.pack()

# Create the multiselect listbox
items = []
listbox_control = MultiSelectListbox(window, items)

"""
# Create the label for the text box
label = Label(window, text="Enter some TAG examples:")
label.pack()

# Create the multiline text box entry field
text_box = Text(window, height = 5, width = 20)
text_box.pack()
"""

# Run the main loop
window.mainloop()
#######################################################






