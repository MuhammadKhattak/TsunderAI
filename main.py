import os

# For setting the right path when run
os.chdir(os.path.dirname(os.path.realpath(__file__)))

class Parser:
  
  def parse_script(self,script):
    
    out = ""
    indent = 0
    increment = 0
    paths = 0
    story = []
    content = ""
    character = ""
    trait = ""
    choice = ""
    decisions = []

    i = 0
    while i < len(script):
      
      if script[i] == '{' and script.find('}',i) != -1:
        
        content = script[i+1:script.find('}',i)].strip().split()
        
        if not content:
          i = script.find('}',i) + 1
          continue

        out = out.strip()
        
        if content[0] == 'n':
          try:
            indent = int(content[1])
          except ValueError:
            print("Invalid argument X encountered in {n [X]}")
            return
          except IndexError:
            pass
          out += '\n' + (' ' * indent)
        elif out and not paths:
          story.append((character,out))
          out = ""
          
        if content[0] == 'C':
          try:
            character = content[1]
          except IndexError:
            character = ""
            
        if content[0].isdecimal():
          paths = int(content[0])
          
        if paths and content[0][0] == '+':
          trait = content[0][1:].strip()
          if len(trait) > 1:
            print("Invalid argument [trait] in {+[trait] [increment]}")
            return
          try:
            increment = int(content[1])
          except ValueError:
            print("Invalid argument [increment] in {+[trait] [increment]}")
            return
          except IndexError:
            print("Missing argument [increment] in {+[trait] [increment]}")
            return
          
        if content[0].upper() == "CHOICE_END":
          choice = out
          out = ""
          decisions.append((choice,trait,increment,self.parse_script(script[script.find('}',i)+1:])))
          paths -= 1
          end = script.find("DIALOGUE_END",i)
          while script.count("CHOICE_END",i,end) - script.count("DIALOGUE_END",i,end) != 1:
            end = script.find("DIALOGUE_END",end+1)
          i = end
          
        if content[0].upper() == "DIALOGUE_END":          
          return story
                  
        if decisions and not paths:
          story.append(decisions)
          decisions = []
        
        i = script.find('}',i)
          
      elif script[i] not in ['\n']:
        out += script[i]
      
      i += 1
          
    return story


class Script:
  
  def __init__(self,script_file):
    self.parser = Parser()
    self.script = self.parser.parse_script(script_file.read())
    self.index = [0]
    self.current = None
    
  def get_current(self,current,i=0):
    if i == len(self.index) - 1:
      return current
    else:
      return self.get_current(current[self.index[i]],i=i+1)
      
  def update_current(self):
    self.current = self.get_current(self.script)
    return self.current
    
  def next_line(self):
    while self.index:
      try:
        self.index[-1] += 1
        try:
          self.update_current()
        except IndexError:
          self.index.pop()
          self.index.pop()
          self.index.pop()
        else:
          break
      except IndexError:  # To catch when index has been popped empty
        break
  
  def advance(self):
    self.next_line()
    if isinstance(self.current,list):
      pass    # Implement decision handling
    else:
      return self.current

class Game:
  
  def __init__(self):
    pass
