import json

class Libs(object):
    
    def error_seeker(self, line, key, tokens, productions, production_flag, ignoring, or_flag):
        # sourcery skip: low-code-quality
        Error = ''
        # If comment sections are invalid
        if '/*' in line and '*/' not in line or '*/' in line and '/*' not in line:
            Error = '-----------------\nERROR: Comment Marks Incomplete\n-----------------\n'
            return key, Error, productions, production_flag, ignoring, or_flag
        # If token-production is found
        if '%%' in line:
            key = False

        # Token Section-----------------------------------------------------------------
        if key == True:
            if line.strip() and '%token' not in line and ('/*' or '*/') not in line:
                Error = f'-----------------\nERROR: Comment Marks Syntax not Found [{line}]\n-----------------\n'
                return key, Error, productions, production_flag, ignoring, or_flag
            # If a token is identified
            if '%token' in line and '/*' not in line and '*/' not in line:
                aux_line = line.split(' ')
                # Check Individual %token Syntax
                if aux_line[0] != '%token':
                    Error = '-----------------\nERROR: Incorrect Token Syntax\n-----------------\n'
                    return key, Error, productions, production_flag, ignoring, or_flag
                # Check Uppercase N-Token Syntax
                aux_line.pop(0)
                for N in aux_line:
                    if not N.isupper():
                        Error = '-----------------\nERROR: Incorrect Token Uppercase Syntax\n-----------------\n'
                        return key, Error, productions, production_flag, ignoring, or_flag
                    else:
                        tokens.append(N.rstrip('\n'))

            # If a production is identified in token section
            if ';' in line and '/*' not in line and '*/' not in line:
                Error = '-----------------\nERROR: "%%" Division Not Found\n-----------------\n'
                return key, Error, productions, production_flag, ignoring, or_flag

            if 'IGNORE' in line:
                aux_line = self._extracted_from_error_seeker_40(line, ' ')
                aux_line.pop(0)
                for e in aux_line:
                    ignoring.append(e)

        elif key == False:
            # If a token is identified in production section
            if '%token' in line:
                Error = '-----------------\nERROR: Incorrect Token Section Position\n-----------------\n'
                return key, Error, productions, production_flag, ignoring, or_flag

            elif ':' in line:
                aux_line = self._extracted_from_error_seeker_40(line, ':')
                # If another production is started while a current one is running
                if production_flag:
                    Error = f'-----------------\nERROR: Previous Production Unfinished - Name:{production_flag}\n-----------------\n'
                    return key, Error, productions, production_flag, ignoring, or_flag

                # If the Name is wrong
                if len(aux_line) > 1:
                    Error = '-----------------\nERROR: Incorrect Name Production Syntax\n-----------------\n'
                    return key, Error, productions, production_flag, ignoring, or_flag

                # If Production Name isn't in lowercase
                if not aux_line[0].islower():
                    Error = '-----------------\nERROR: Incorrect Production Lowercase Syntax\n-----------------\n'
                    return key, Error, productions, production_flag, ignoring, or_flag

                # If Production Name has spaces in it
                if aux_line[0].find(' ') != -1:
                    Error = '-----------------\nERROR: Incorrect Production Name Syntax\n-----------------\n'
                    return key, Error, productions, production_flag, ignoring, or_flag

                production_flag = aux_line[0]
                aux_dict = []
                productions[production_flag] = aux_dict.copy()

            elif ';' in line:
                production_flag = False
                or_flag = 0

            elif production_flag:
                
                aux_line = self._extracted_from_error_seeker_40(line, ' ')
                # If an OR is found
                if '|' in aux_line:
                    index = aux_line.index('|')
                    aux_line.pop(index)
                elif '|' not in aux_line and or_flag == 0:
                    or_flag += 1
                    
                elif '|' not in aux_line and or_flag > 0:
                    Error = '-----------------\nERROR: Incorrect OR Syntax\n-----------------\n'
                    return key, Error, productions, production_flag, ignoring, or_flag
                for e in aux_line:
                    # If e is full uppercase
                    if e.isupper() and e not in tokens:
                        Error = f'-----------------\nERROR: Token not Found [{e}]\n-----------------\n'
                        return key, Error, productions, production_flag, ignoring, or_flag
                    # Verify lowercase exist
                    elif not e.islower() and not e.isupper():
                        Error = f'-----------------\nERROR: Bad Lowercase/Uppercase Syntax [{e}]\n-----------------\n'
                        return key, Error, productions, production_flag, ignoring, or_flag

                productions[production_flag].append(aux_line)

        return [key, tokens, productions, production_flag, ignoring, or_flag]

    # Rename this here and in `error_seeker`
    def _extracted_from_error_seeker_40(self, line, arg1):
        result = line.rstrip('\n')
        result = result.split(arg1)
        result = list(filter(lambda x: x != '', result))

        return result
    
    def post_error_seeker(self, productions):
        # For each element in productions
        for e in productions:
            # For each OR in productions
            for l in productions[e]:
                # For each element within each OR production
                for e2 in l:
                    if e2.islower() and e2 not in productions.keys():
                        Error = f'-----------------\nERROR: Unrecognized Production [{e2}]\n-----------------\n'
                        print(Error)
                        raise SystemExit
    
    def token_verifier(self, tokens):
        with open('YALex.json', 'r') as file:
            content = file.read()
            tokens_yalex = json.loads(content)
        tokens_yalex = [element for element in tokens_yalex if element != ""]
        for t in tokens:
            if t in tokens_yalex:
                tokens_yalex.remove(t)
        if tokens_yalex:
            Error = f'-----------------\nERROR: Missing Tokens [{tokens_yalex}]\n-----------------\n'
            print(Error)
            raise SystemExit
            
    def yalp_reader(self, path):
        tokens = []
        ignoring = []
        productions = {}
        production_flag = False
        or_flag = 0
        key = True
        # Open the file
        with open(path, 'r') as file:
            for line in file:
                # Check for Errors
                result = self.error_seeker(line, key, tokens, productions, production_flag, ignoring, or_flag)
                # If an Error is found
                if 'ERROR' in result[1]:
                    print(result[1])
                    raise SystemExit
                else:
                    key = result[0]
                    tokens = result[1]
                    productions = result[2]
                    production_flag = result[3]
                    ignoring = result[4]
                    or_flag = result[5]
            
            # verify production existence
            self.post_error_seeker(productions)
            self.token_verifier(tokens)
            print('TOKENS:',tokens, ' \nPRODUCTIONS:',productions, '\nIGNORES:',ignoring)
            return tokens, productions, ignoring
    
    def recursive_first(self, productions, production):

        aux_first = []
        
        for n_or in productions[production]:
            
            first_ele = n_or[0]
            # If the first calculation leads to same dic.key
            if first_ele == production:
                aux_first = first_ele
            
            # If the first calculation leads to different dic.key
            elif first_ele != production and first_ele in productions.keys():
                aux_first = self.recursive_first(productions, first_ele)
            
            # If the first calculation is a terminal
            elif first_ele != production and first_ele not in productions.keys():
                if first_ele not in aux_first:
                    aux_first.append(first_ele)
            
        return aux_first
                
                
    def Firsts(self,productions):
        
        firsts = {ele: '' for ele in productions}
        # check for each production
        for production in productions:
            # Check for each OR production
            first = self.recursive_first(productions, production)
            firsts[production] = first
            
        return firsts
            
                    
                
        

L = Libs()
tokens, productions, ignoring = L.yalp_reader('inputs_par/slr-1.yalp')
print('-------------Productions First:-------------\n',L.Firsts(productions))