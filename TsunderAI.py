# Muhammad Khattak, Sinan Shariff, and Robin Huo
# ICS3U1
# TsunderAI.py

# Work distribution is detailed in the storyboard, but generally:
# Robin designed the overall structure and wrote the Parser class
# Muhammad wrote the Script class
# Sinan wrote the Game class with help from the others

# Extension: Usage of classes & objects, lists, recursion

import os
import shutil

# Sets the directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Get terminal window width (default 80)
try:
  columns = shutil.get_terminal_size()[0]
except:
  columns = 80

# Parser class, takes script from a text files and converts it for internal use
# Parses the ad hoc formatting specification we made
class Parser:

  """
  Script tags in the script are placed within {braces}
  Possible tags:
  {HEAD} is placed before a line containing the optional header of the script;
  {n [X]}, where [X] is a whole number, is equivalent to '\n' + ' ' * [X]
  {n} may also be used without a [X], and the previous value of [X] is used;
  {C [name]} is placed before a line and designates the character speaking;
  {[N]}, where [N] is a natural number, introduces a list of [N] choices;
  {+[trait] [increment]}, where [trait] is a trait character and [increment]
  is an integer, is placed before the content of a choice and marks which trait
  to increment and by how much ([increment] is 0 if no trait is incremented);
  {CHOICE_END} marks the end of the content of a choice and the beginning of any
  subdialogue belonging to that choice;
  {DIALOGUE_END} marks the end of the subdialogue of a choice;
  There may be choices and more subdialogue in the subdialogue of a choice,
  infinitely deep (or until the call stack overflows).
  Our scripts never actually make use of this, though.
  Example script:
  {C TSUNDERAI} This is just an example.
  {C SLIBBERT} Yes, I know.
  {C TSUNDERAI} Really?
  {2}
  {+S 3} No. {CHOICE_END}
        {C TSUNDERAI} Liar.
        {C SLIBBERT} Am not.
  {DIALOGUE_END}
  {+S 5} Yes. {CHOICE_END} {DIALOGUE_END}
  {END}
  """

  """
  parse_script takes a string containing a script formatted as described above
  Returns a list of lines and decisions:
  Lines are formatted as pairs: ("CHARACTER","LINE");
  Decisions are formatted as lists of choices,
  Each choice is a 4-tuple: ("CONTENT","TRAIT",INCREMENT,[SUBDIALOGUE]),
  [SUBDIALOGUE] is a list of lines and decisions formatted as described above
  Example return value:
  [("TSUNDERAI","This is just an example."),("SLIBBERT","Yes, I know."),
  ("TSUNDERAI","Really?"),[("No.",'S',3,[("TSUNDERAI","Liar."),
  ("SLIBBERT","Am not.")]),("Yes.",'S',5,[])]]
  """
  def parse_script(self,script):
    
    # Initialize everything to empty, default numerical values are 0
    out = ""          # Output buffer, built up and pushed into master list
    indent = 0        # [X]
    increment = 0     # [increment]
    paths = 0         # [N]
    story = []        # Master list containing parsed script
    content = ""      # Content of a found script tag
    character = ""    # [name]
    trait = ""        # [trait]
    choice = ""       # Choice content
    decisions = []    # List containing choices at a branching point

    # Loop through each character in the script
    i = 0
    while i < len(script):

      # Begin script tag handling
      # (Is the current character '{' and is there a '}' after it somewhere?)
      if script[i] == '{' and script.find('}',i) != -1:

        # Extract the content of the script tag and split into a list
        content = script[i+1:script.find('}',i)].strip().split()

        # If the tag is empty, skip to the end brace and continue
        if not content:
          i = script.find('}',i) + 1
          continue

        # Strip whitespace from each end of the output buffer
        out = out.strip()

        # Handle {n [X]}
        if content[0] == 'n':
          try:
            indent = int(content[1])  # Set [X]
          except ValueError:
            print("Invalid argument X encountered in {n [X]}")
            return
          except IndexError:
            pass    # Accept case where no [X] provided
          out += '\n' + (' ' * indent)    # Apply {n [X]}
        elif out and not paths:
          # If output buffer is not empty and not at a branching point,
          # Flush output buffer and push line to master list
          # (This is placed here because the end of a line is always marked by
          # a script tag, except {n [X]})
          story.append((character,out))
          out = ""

        # Handle {HEAD}
        # It is treated as a line where the character speaking is "{HEAD}"
        if content[0].upper() == "HEAD":
          character = "{HEAD}"

        # Handle {C [name]}
        if content[0] == 'C':
          try:
            character = ' '.join(content[1:]) # Set [name], supports multi-word
          except IndexError:
            character = ""  # Allow empty character name

        # Handle {[N]}
        if content[0].isdecimal():
          paths = int(content[0])   # Set {[N]}

        # Handle {+[trait] [increment]}
        if paths and content[0][0] == '+':
          trait = content[0][1:].strip()    # Set [trait]
          # [trait] must be a single character
          if len(trait) > 1:
            print("Invalid argument [trait] in {+[trait] [increment]}")
            return
          try:
            increment = int(content[1])   # Set [increment]
          except ValueError:
            print("Invalid argument [increment] in {+[trait] [increment]}")
            return
          except IndexError:
            print("Missing argument [increment] in {+[trait] [increment]}")
            return

        # Handle {CHOICE_END}
        if content[0].upper() == "CHOICE_END":
          choice = out
          out = ""    # Flush output buffer
          # Add choice 4-tuple to decision list
          # and recurse to parse subdialogue
          decisions.append((choice,trait,increment,
                            self.parse_script(script[script.find('}',i)+1:])))
          paths -= 1    # Mark one choice handled

          # Find the correct {DIALOGUE_END} and jump to it (ignore subdialogue)
          end = script.find("DIALOGUE_END",i)
          while (script.count("CHOICE_END",i,end)
                 - script.count("DIALOGUE_END",i,end)) != 1:
            end = script.find("DIALOGUE_END",end+1)
          i = end

        # Handle {DIALOGUE_END}
        if content[0].upper() == "DIALOGUE_END":
          return story    # Return parsed subdialogue

        # If we've added every choice, push to master list and reset
        if decisions and not paths:
          story.append(decisions)
          decisions = []

        # Jump to the end of the script tag
        i = script.find('}',i)

      # If not a script tag, push current character to output buffer
      # (Ignore newlines and Unicode BOM character)
      elif script[i] not in ['\n','\ufeff']:
        out += script[i]

      # Increment loop
      i += 1

    # Return fully parsed script
    return story


# Script class, holds methods for manipulating and advancing a script
class Script:

  # Constructor, takes a file containing a script, parses it, and stores it
  def __init__(self,script_file):
    self.parser = Parser()
    self.script = self.parser.parse_script(script_file.read())
    script_file.close()
    
    # Set header attribute if script has a header
    self.head = ""
    if self.script[0][0] == "{HEAD}":
      self.head = self.script[0][1]
      self.script = self.script[1:]
    
    self.index = [-1]   # List containing current position in the script
    # Begins at -1 because it is incremented before it is accessed
    # index[i] is the current index in the container at depth i
    # Empty once the script is finished
    
    self.current = None   # The current item at position pointed to by index

  # Recurse to find current item in script
  def get_current(self,current,i=0):
    if i == len(self.index):
      return current    # Return if at deepest indexed level (end of index)
    else:   # Otherwise recurse one level deeper
      return self.get_current(current[self.index[i]],i=i+1)

  # Find current item in script and update attribute
  def update_current(self):
    self.current = self.get_current(self.script)
    return self.current

  # Go to the next line in the script
  def next_line(self):
    while self.index:   # While script is not finished
      # Try to increment at deepest level and update new current item
      try:
        self.index[-1] += 1
        try:
          self.update_current()
        # If no more content at this level, pop out of subdialogue
        # Pop 3 times because [DIALOGUE(DECISION[(SUBDIALOGUE)])]
        except IndexError:
          self.index.pop()
          self.index.pop()
          self.index.pop()
        else:
          break   # Finish if increment and retrieval were successful
      except IndexError:  # To catch when index has been popped empty
        break

  # Update position in script for subdialogue from a choice
  def apply_decision(self,choice):
    self.index.append(choice)   # Index of choice in the decision branch
    self.index.append(3)    # List of subdialogue is at index 3 of a choice
    self.index.append(-1)   # Initialize at -1 because incremented pre-access
    
  # Script is finished if index has been popped empty
  def finished(self):
    return not self.index

  # Advance the script and return new current item
  def advance(self):
    self.next_line()
    if self.finished():
      return False
    else:
      return self.current


# Game class, contains methods for game progression and user interaction
class Game:

  # Static lists containing the filenames of the script files
  # ENCODE ALL FILES IN UTF-8 OR THINGS WILL BREAK
  common_scripts = ["Stage1-1","Interlude1","Stage2-1","Interlude2","Stage3-1",
                    "Stage3-2","Interlude3","Stage4-1"]
  ending_scripts = ["Ending1 - I love you TsunderAI",
                    "Ending2 - Not so Okey-Doki",
                    "Ending3 - Bay of (3D) Pigs",
                    "Ending4 - The Cruel Tutelage of Aasaa Maseson",
                    "Ending5 - Get a feeling so complicated",
                    "Ending6 - Ninjularity",
                    "Ending7 - Endless 26",
                    "Ending8 - My Neural Network Cant Be This Elitist!"]
  scripts = common_scripts + ending_scripts
  
  def __init__(self):
    # Initialize traits and control attributes
    self.affinity = 0
    self.disdain = 0
    self.humour = 0
    self.memes = 0
    self.sympathy = 0
    self.taste = 0
    self.weeb = 0
    self.script_file = None
    self.script_index = 0   # Index of current script in Game.scripts
    self.ending = False     # At an ending?
    self.finished = False   # Game finished?

  # Takes arguments from a choice and increments the corresponding trait
  # Also prints a message for whichever trait incremented (+-sign is explicit)
  def increment_trait(self,trait,increment):
    trait = trait.upper()
    if trait == "A":
      self.affinity += increment
      # Only print a message if increment is not 0
      # Explicitly print the sign of the value, positive or negative
      if increment:
        print("{:+}".format(increment),
              "Affinity for Naruto Shippuuden Opening 16!")
    elif trait == "D":
      self.disdain += increment
      if increment:
        print("{:+}".format(increment),"Disdain for Normies!")
    elif trait == "H":
      self.humour += increment
      if increment:
        print("{:+}".format(increment),"Humour!")
    elif trait == "M":
      self.memes += increment
      if increment:
        print("{:+}".format(increment),"Memes!")
    elif trait == "S":
      self.sympathy += increment
      if increment:
        print("{:+}".format(increment),"Sympathy!")
    elif trait == "T":
      self.taste += increment
      if increment:
        print("{:+}".format(increment),"Taste!")
    elif trait == "W":
      self.weeb += increment
      if increment:
        print("{:+}".format(increment),"Weebiness!")
    print()

  # Put decision to user and take choice
  def take_decision(self,decision):
    # Print and number each decision (1-based)
    for i in range(len(decision)):
      print(i+1,": ",decision[i][0],sep="")
      print()

    # Get user input and retry until valid
    chosen = None
    while not chosen:
      try:
        chosen = int(input().strip(". "))   # Take input, strip '.' and ' '
        if chosen < 1 or chosen > len(decision):
          raise ValueError    # Retry if choice out of bounds
      except:
        print("Please enter a valid value.")    # Retry
        chosen = None
      else:
        break   # Finish if successful
    chosen -= 1   # Decrement decision because of 1-based enumeration

    # Increment the selected trait and return the user choice
    self.increment_trait(decision[chosen][1],decision[chosen][2])
    return chosen

  # Execute a given script
  def execute_script(self,script):
    # Initialize control variables
    changed_character = True    # Controls if character name is printed anew
    override = True   # Overrides automatic detection of if character changed
    character = ""    # Name of character currently speaking
    line = ""         # Line being spoken
    # Print header if the script has one
    # Centre it on screen and surround it with '-'
    if script.head:
      print("{:-^{columns}}".format(script.head,columns=columns))
      print()
    # Run through the script
    while not script.finished():
      current = script.advance()    # Advance the script and get current item
      if script.finished():
        break   # End if script is finished

      # If current item is a pair, then it must be a character's line
      if isinstance(current,tuple) and len(current) == 2:
        # Override automatic detection of whether the character changed
        # And thus whether to print the character name anew
        if override:
          override = False
        # Check if the character changed from last iteration
        else:
          if character != current[0]:
            changed_character = True
          else:
            changed_character = False
        character,line = current  # Set character and line to items of the pair
        # Print the character name if the character changed
        if changed_character and character:
          print(character,": ",sep="",end="")
        # Otherwise, print spaces to be flush with the character's first line
        elif character and not changed_character:
          print(' ' * (len(character) + 2),end="")
        print(line)   # Print the line spoken
        input()
      # If current item is not a pair, then it must be a list of choices
      else:
        # Take and apply decision to the script
        script.apply_decision(self.take_decision(current))
        # Force print character name next iteration
        override = True
        changed_character = True

  # Advances to the next script (includes ending selector)
  def next_script(self):
    # If we have gone past the common scripts, we must choose an ending
    if self.script_index >= len(Game.common_scripts) - 1:
      if self.ending:   # If an ending was already played, we are finished
        self.finished = True
        return
      # List of traits, in the order that corresponds with the ending scripts
      traits = [self.sympathy, self.taste, self.weeb, self.memes, self.affinity,
                self.humour, self.disdain]
      # Find highest and lowest trait
      max_trait = max(traits)
      min_trait = min(traits)
      # Set script_index to the beginning of the ending scripts
      self.script_index = len(Game.common_scripts)
      # Take the first ending if all traits are within 4 points of one another
      if abs(max_trait - min_trait) < 4:
        pass
      # If sympathy is the lowest trait, take the low sympathy ending
      elif min_trait == self.sympathy:
        self.script_index += traits.index(self.sympathy) + 1
      # Otherwise, take the ending of the highest trait (excluding sympathy)
      else:
        self.script_index += traits.index(max(traits[1:])) + 1
      self.ending = True
    # If we are still in the common scripts, simply increment by 1
    else:
      self.script_index += 1

  # Execute the game
  def execute(self):
    # Loop while not finished and there are still scripts left
    while not self.finished and self.script_index < len(Game.scripts):
      # All our script files are encoded in UTF-8
      encoding = "utf-8"
      # Open the current script file from Game.scripts
      self.script_file = open("Scripts\\"+Game.scripts[self.script_index]+".txt",
                              encoding=encoding)
      # Instantiate a script object with the script file and execute it
      self.execute_script(Script(self.script_file))
      self.script_file.close()  # Redundant, but better safe than sorry
      # Handle the recursion ending (if "Endless" is in the name of the script)
      if "ENDLESS" in Game.scripts[self.script_index].upper():
        Game().execute()
      # Otherwise, just go to the next script
      else:
        self.next_script()
    # Print a centred message "THE END" surrounded by '-' at the end
    print("{:-^{columns}}".format("THE END",columns=columns))

# Start the game
Game().execute()
