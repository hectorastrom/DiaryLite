# Add an id to all items with a format of {{item.name|lower}} + "id" so that in javascript we can select all items with that id to fill them with the right content. 

class BaseItem:
    def __init__(self):
        self.category = 0
        self.name = ""
        self.description = ""
        self.html = ''
        self.disabled_html = ''

    def __repr__(self):
        return f"category: {self.category}, name: {self.name}, description: {self.description}"

class Summary(BaseItem):
    def __init__(self):
        self.category = 1
        self.name = "Summary"
        self.description = "Write as little or as much about your day as you'd like."
        # Items with multiple inputs can have ids like summarybox1, summarybox2, etc which are then concatenated on the content string.
        self.html = '<textarea class="form-control" name="summarybox" style = "text-align: left; float: left;  width:100%;" rows = "8" placeholder="Write about your day..." type="text" autocomplete="off" id = "summaryid" ></textarea>'
        self.disabled_html = '<textarea class="form-control" name="summarybox" style = "text-align: left; float: left; background-color: #d1d1d1; width:100%;" rows = "8" placeholder="EXAMPLE: Write about your day..." type="text" autocomplete="off" readonly id = "summaryid"></textarea>'

class Happiness(BaseItem):
    def __init__(self):
        self.category = 2
        self.name = "Happiness"
        self.description = "Use the slider to indicate your mood for that day."
        self.html = '<div class="slidecontainer"><input type="range" min="1" max="100" value="50" class="slider" name="happinessbox" id = "happinessid"></div>'
        self.disabled_html = '<div style = "width: 100%" class="slidecontainer"><input type="range" min="1" max="100" value="50" class="slider" name="happinessbox" disabled id = "happinessid"></div>'

class Location(BaseItem):
    def __init__(self):
        self.category = 3
        self.name = "Location"
        self.description = "In case you are traveling, the location field can be used to remember where you were."
        self.html = '<input class="form-control form-control-lg" id = "locationid" name="locationbox" placeholder="Paris, France" type="text" autocomplete="off"><br>'
        self.disabled_html = '<input class="form-control form-control-lg" id = "locationid" name="locationbox" placeholder="Paris, France" type="text" readonly<br>'

class Gratitude(BaseItem):
    def __init__(self):
        self.category = 4
        self.name = "Gratitude"
        self.description = "Record three things you are grateful for that day. They can be as big or small as you'd like."
        self.html = ''
        self.disabled_html = ''