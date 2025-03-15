import re
import pandas as pd

class LexicalAnalyzer:
    def __init__(self, **token_patterns):
        """
        Initialize the LexicalAnalyzer class with token patterns.
        
        In compiler design, the lexical analyzer (also known as a scanner or tokenizer) is the first phase
        that breaks down the input source code into a sequence of lexical tokens. If no patterns are provided,
        the analyzer won't recognize any tokens and will mark everything as UNRECOGNIZED.
        
        Args:
            **token_patterns: Keyword arguments defining token patterns
        """
        self.token_specs = None
        self.combined_pattern = None
        
        # Set patterns from arguments
        self.patterns = self.get_token_patterns(**token_patterns)
        
        # If patterns exist, update them
        if self.patterns:
            self.update_patterns()
        else:
            # Empty pattern - won't match anything
            self.token_specs = []
            self.combined_pattern = r'(?!)'  # Negative lookahead that never matches
        
    def get_token_patterns(self, **kwargs):
        """
        Define regex patterns for different token types using keyword arguments.
        
        In a compiler, token patterns define how to recognize different elements of the language syntax.
        The method takes keyword arguments where:
        - The name of each argument becomes the token type name
        - The value of each argument is the regex pattern
        
        Args:
            **kwargs: Keyword arguments where names are token types and values are regex patterns
            
        Returns:
            dict: Dictionary mapping token type names to their regex patterns
        """
        return kwargs
    
    def update_patterns(self, **kwargs):
        """
        Update token patterns and regenerate token specifications.
        """
        if kwargs:
            # Update with new patterns
            new_patterns = self.get_token_patterns(**kwargs)
            self.patterns.update(new_patterns)
            
        # If no patterns, set an empty pattern
        if not self.patterns:
            self.token_specs = []
            self.combined_pattern = r'(?!)'  # Negative lookahead that never matches
            return
            
        # Create an ordered list of token specs based on pattern specificity
        pattern_items = list(self.patterns.items())
        
        # Order matters: put more specific patterns first
        # Move FLOAT before NUMBER if both exist
        if 'FLOAT' in self.patterns and 'NUMBER' in self.patterns:
            float_item = ('FLOAT', self.patterns['FLOAT'])
            pattern_items.remove(float_item)
            
            number_index = next(i for i, (name, _) in enumerate(pattern_items) if name == 'NUMBER')
            pattern_items.insert(number_index, float_item)
        
        # Move COMMENT near the beginning if it exists
        if 'COMMENT' in self.patterns:
            comment_item = ('COMMENT', self.patterns['COMMENT'])
            pattern_items.remove(comment_item)
            pattern_items.insert(0, comment_item)
            
        # Put WHITESPACE at the end (lowest priority)
        if 'WHITESPACE' in self.patterns:
            whitespace_item = ('WHITESPACE', self.patterns['WHITESPACE'])
            if whitespace_item in pattern_items:
                pattern_items.remove(whitespace_item)
                pattern_items.append(whitespace_item)
        
        # NEW CODE: Sort patterns by their length/specificity
        # This will ensure longer patterns are tried before shorter ones
        pattern_items.sort(key=lambda x: len(x[1]), reverse=True)
        
        # Regenerate token specifications and combined pattern
        self.token_specs = pattern_items
        self.combined_pattern = self.build_combined_pattern(self.token_specs)    
    
    def build_combined_pattern(self, token_specs):
        """
        Build a combined regex pattern with named capture groups.
        
        This is a key aspect of the lexical analyzer as it creates a single regex pattern
        that can match all possible tokens in the language, with each token type being a 
        named capture group.
        
        Args:
            token_specs (list): List of (token_type, pattern) tuples
            
        Returns:
            str: Combined regex pattern
        """
        if not token_specs:
            return r'(?!)'  # Negative lookahead that never matches
            
        return '|'.join('(?P<%s>%s)' % (name, pattern) for name, pattern in token_specs)
    
    def process_unrecognized_tokens(self, tokens, expression, start, end):
        """
        Process unrecognized characters in the expression.
        
        This is important for error reporting in the compiler. Characters that don't
        match any defined token pattern are marked as UNRECOGNIZED.
        
        Args:
            tokens (list): List to append tokens to
            expression (str): The expression being tokenized
            start (int): Start index of unrecognized section
            end (int): End index of unrecognized section
        """
        for char in expression[start:end]:
            tokens.append({'lexeme': char, 'token_type': 'UNRECOGNIZED'})
    
    def identify_token_type(self, match, tokens):
        """
        Identify the token type from a match and add it to tokens list if not whitespace.
        
        This method extracts the matched lexeme and its corresponding token type from
        the regex match object.
        
        Args:
            match (re.Match): Regex match object
            tokens (list): List to append the token to
        """
        for token_type, _ in self.token_specs:
            lexeme = match.group(token_type)
            if lexeme is not None:
                if token_type != 'WHITESPACE':  # Ignore spaces
                    tokens.append({'lexeme': lexeme, 'token_type': token_type})
                break  # Move to next match
    
    def tokenize_math_expression(self, expression):
        """
        Tokenizes a math expression and detects unrecognized tokens properly.
        
        This is the main scanning function of the lexical analyzer, which processes
        the input expression and produces a sequence of tokens.
        
        Args:
            expression (str): A math expression
            
        Returns:
            list: A list of dictionaries with 'lexeme' and 'token_type'.
        """
        tokens = []
        
        # If no patterns defined, mark everything as unrecognized
        if not self.token_specs:
            for char in expression:
                tokens.append({'lexeme': char, 'token_type': 'UNRECOGNIZED'})
            return tokens
            
        last_match_end = 0  # Tracks the last matched index
        
        # Find all matches
        for match in re.finditer(self.combined_pattern, expression):
            start, end = match.start(), match.end()
            
            # Capture unrecognized characters between matches
            if start > last_match_end:
                self.process_unrecognized_tokens(tokens, expression, last_match_end, start)
            
            # Identify the token type
            self.identify_token_type(match, tokens)
            
            last_match_end = end  # Update last matched index
        
        # Capture any remaining unrecognized characters at the end
        if last_match_end < len(expression):
            self.process_unrecognized_tokens(tokens, expression, last_match_end, len(expression))
    
        return tokens
    
    def display_token_table(self, tokens):
        """
        Display tokens in a pandas DataFrame.
        
        This provides a structured visualization of the token stream, which is useful
        for debugging and understanding the lexical analysis process.
        
        Args:
            tokens (list): List of token dictionaries
            
        Returns:
            pandas.DataFrame: DataFrame containing the tokens
        """
        df = pd.DataFrame(tokens)
        df = df.rename(columns={'lexeme': 'Lexemes', 'token_type': 'Tokens'})
        return df
    
    def analyze_expression(self, expression):
        """
        Analyze a math expression and display its token table.
        
        This is a utility method that combines tokenization and display, making it
        easier to test and visualize the lexical analysis results.
        
        Args:
            expression (str): A math expression
            
        Returns:
            pandas.DataFrame: DataFrame containing the token analysis
        """
        print(f"Expression: {expression}")
        tokens = self.tokenize_math_expression(expression)
        
        df_tokens = self.display_token_table(tokens)
        print("\nTokens:")
        print(df_tokens)
        
        print("\n")
        return df_tokens
    
    # def interactive_test(self):
    #     """
    #     Run an interactive test session for the lexical analyzer.
        
    #     This method provides a command-line interface for testing expressions.
    #     Users can enter expressions one at a time and see the token analysis results.
    #     After each analysis, the user is asked if they want to continue or quit.
        
    #     This is particularly useful during compiler development to test how the lexical
    #     analyzer handles different input patterns and edge cases.
    #     """
    #     print("\n" + "="*50)
    #     print("LexicalAnalyzer Interactive Testing Mode")
    #     print("="*50)
    #     print("Enter expressions to analyze. The analyzer will tokenize each input.")
    #     print("Current token patterns:", ", ".join(name for name, _ in self.token_specs))
    #     print("="*50)
        
    #     while True:
    #         # Get user input for the expression
    #         print("\n")
    #         expression = input("Enter an expression to analyze (or 'q' to quit): ")
            
    #         # Check if the user wants to quit
    #         if expression.lower() == 'q':
    #             print("\nExiting interactive test mode.")
    #             break
            
    #         # Analyze the expression
    #         self.analyze_expression(expression)
            
    #         # Ask if the user wants to continue
    #         continue_choice = input("\nPress Enter to analyze another expression or 'q' to quit: ")
    #         if continue_choice.lower() == 'q':
    #             print("\nExiting interactive test mode.")
    #             break
    def interactive_test(self):
        """
        Run an interactive test session for the lexical analyzer.
        
        This method provides a command-line interface for testing expressions.
        Users can enter expressions one at a time and see the token analysis results.
        After each analysis, the user is asked if they want to continue or quit.
        """
        print("\n" + "="*50)
        print("LexicalAnalyzer Interactive Testing Mode")
        print("="*50)
        print("Enter expressions to analyze. The analyzer will tokenize each input.")
        print("Current token patterns:", ", ".join(name for name, _ in self.token_specs))
        print("="*50)
        
        continue_testing = True
        
        while continue_testing:
            # Get user input for the expression - accept any input here
            print("\n")
            expression = input("Enter an expression to analyze: ")
            
            # Analyze the expression (any expression, including 'q')
            self.analyze_expression(expression)
            
            # Separate prompt for continuation decision
            print("\n" + "-"*40)
            continue_choice = input("Do you want to analyze another expression? (Enter 'quit' to exit or press Enter to continue): ")
            
            # Check if the user wants to quit - only check here
            if continue_choice.lower() in ['quit', 'exit', 'q']:
                continue_testing = False
        
        # Only show exit message when actually exiting
        print("\nExiting interactive test mode.")
