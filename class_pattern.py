# Written by Shaked Bitan
# pattern class
class Pattern:
    def __init__(self):
        # pattern attributes
        self.pattern_name = None  # name of pattern
        self.pictures = []  # array of pictures of the pattern
        self.beginning = None  # type of beginning
        self.rounds = None  # number of rounds
        self.rounds_list = []  # all rounds list
        self.category = "" # pattern's category
        self.d_level = 0  # pattern's difficulty level
        self.subcategory = ""
        self.hook = ""
        self.materials = []
        self.date = ""
        self.username = ""
        self.sum_time = 0

    def print_pattern(self):
        #prints the pattern nicely
        print("Name: " + self.pattern_name + "\n" + "rounds list: ", end="")
        print(self.rounds_list)
        print("beginning"+self.beginning+"\n number of rounds: " + self.rounds+"\n category: "+self.category+"\n subcategory: " +self.subcategory+"\n hook"+self.hook+"\n materials: ", end ="")
        print(self.materials)

    def get_username(self):
        return self.username

    def get_date(self):
        return self.date

    def get_pattern_name(self):
        return self.pattern_name

    def get_category(self):
        return self.category

    def get_subcategory(self):
        return self.subcategory

    def get_d_level(self):
        return self.d_level

    def get_sum_time(self):
        return self.sum_time

    # [ [sc], 6, [sc, hdc,slst], 3]

    #def upload_pattern_to_server(self, ):
    #[[],[],[]]
    #[ [stitch, stitch, stitch...] , times, how many stitches are supposed to be at the end of the round?]
    #[ [stitch, stitch, stitch...] , times/repaets, total stitches, additional comments]
    # materials: [[1, size], 1, 1, 1, [1, amount, size]]
    #              eyes, scissors, needle, polyfiber, buttons
    # [[[sc, hdc],2,4],[[sc],12,12]]