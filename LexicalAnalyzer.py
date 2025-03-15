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
        self.token_priority = {}  # Store token priority for ordering

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

    def set_token_priority(self, **priorities):
        """
        Set priority order for token types to determine matching precedence.
        
        Higher priority numbers will be matched before lower ones.
        If no priority is specified for a token type, it defaults to 0.
        
        Args:
            **priorities: Keyword arguments mapping token types to their priority values (integers)
        """
        self.token_priority.update(priorities)
        # Re-apply patterns to update token specs with new priorities
        if self.patterns:
            self.update_patterns()

    def update_patterns(self, **kwargs):
        """
        Update token patterns and regenerate token specifications.

        This allows you to modify the lexical analyzer's recognition patterns during its lifecycle,
        which can be useful for language extensions or context-specific scanning.

        Args:
            **kwargs: New token patterns to add or update
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

        # Create a list of token specs
        pattern_items = list(self.patterns.items())
        
        # Sort based on priorities (default 0 if not specified)
        pattern_items.sort(key=lambda x: self.token_priority.get(x[0], 0), reverse=True)

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

    def process_unrecognized_tokens(self, tokens, input_text, start, end):
        """
        Process unrecognized characters in the input text.

        This is important for error reporting in the compiler. Characters that don't
        match any defined token pattern are marked as UNRECOGNIZED.

        Args:
            tokens (list): List to append tokens to
            input_text (str): The input being tokenized
            start (int): Start index of unrecognized section
            end (int): End index of unrecognized section
        """
        for char in input_text[start:end]:
            tokens.append({'lexeme': char, 'token_type': 'UNRECOGNIZED'})

    def tokenize_input(self, input_text, include_whitespace=False):
        """
        Tokenizes input text and detects unrecognized tokens properly.

        This is the main scanning function of the lexical analyzer, which processes
        the input text and produces a sequence of tokens.

        Args:
            input_text (str): The text to be tokenized
            include_whitespace (bool): Whether to include whitespace tokens in the output

        Returns:
            list: A list of dictionaries with 'lexeme' and 'token_type'.
        """
        tokens = []

        # If no patterns defined, mark everything as unrecognized
        if not self.token_specs:
            for char in input_text:
                tokens.append({'lexeme': char, 'token_type': 'UNRECOGNIZED'})
            return tokens

        last_match_end = 0  # Tracks the last matched index

        # Find all matches
        for match in re.finditer(self.combined_pattern, input_text):
            start, end = match.start(), match.end()

            # Capture unrecognized characters between matches
            if start > last_match_end:
                self.process_unrecognized_tokens(tokens, input_text, last_match_end, start)

            # Identify the token type
            for token_type, _ in self.token_specs:
                lexeme = match.group(token_type)
                if lexeme is not None:
                    # Add token if it's not whitespace or if include_whitespace is True
                    if token_type != 'WHITESPACE' or include_whitespace:
                        tokens.append({'lexeme': lexeme, 'token_type': token_type})
                    break  # Move to next match

            last_match_end = end  # Update last matched index

        # Capture any remaining unrecognized characters at the end
        if last_match_end < len(input_text):
            self.process_unrecognized_tokens(tokens, input_text, last_match_end, len(input_text))

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

    def analyze_input(self, input_text, include_whitespace=False):
        """
        Analyze input text and display its token table.

        This is a utility method that combines tokenization and display, making it
        easier to test and visualize the lexical analysis results.

        Args:
            input_text (str): The text to be analyzed
            include_whitespace (bool): Whether to include whitespace tokens in the output

        Returns:
            pandas.DataFrame: DataFrame containing the token analysis
        """
        print(f"Input: {input_text}")
        tokens = self.tokenize_input(input_text, include_whitespace)

        df_tokens = self.display_token_table(tokens)
        print("\nTokens:")
        print(df_tokens)

        print("\n")
        return df_tokens

    def interactive_test(self, include_whitespace=False):
        """
        Run an interactive test session for the lexical analyzer.

        This method provides a command-line interface for testing input text.
        Users can enter text one at a time and see the token analysis results.
        After each analysis, the user is asked if they want to continue or quit.

        Args:
            include_whitespace (bool): Whether to include whitespace tokens in the output
        """
        print("\n" + "="*50)
        print("LexicalAnalyzer Interactive Testing Mode")
        print("="*50)
        print("Enter text to analyze. The analyzer will tokenize each input.")
        print("Current token patterns:", ", ".join(name for name, _ in self.token_specs))
        print("="*50)

        continue_testing = True

        while continue_testing:
            # Get user input - accept any input here
            print("\n")
            input_text = input("Enter text to analyze: ")

            # Analyze the input (any input, including 'q')
            self.analyze_input(input_text, include_whitespace)

            # Separate prompt for continuation decision
            print("\n" + "-"*40)
            continue_choice = input("Do you want to analyze another input? (Enter 'quit' to exit or press Enter to continue): ")

            # Check if the user wants to quit - only check here
            if continue_choice.lower() in ['quit', 'exit', 'q']:
                continue_testing = False

        # Only show exit message when actually exiting
        print("\nExiting interactive test mode.")