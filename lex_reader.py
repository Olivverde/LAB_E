# Abrir archivo
import json
from NFA_lab import *
from labB import *
import copy
class Lexer(object):

    def __init__(self) -> None:
        self.pre_exist_patterns = self.pre_fab()

    def pre_load(self, path):
        
        with open(path) as file:
            pos_status = False
            for line in file:
                
                if 'let' in line:
                    pos_status = True
                if 'tokens' in line and pos_status == False:
                    print('---------------------------------------')
                    print("ERROR: NO SE ENCONTRÓ EXPRESIONES REGULARES PREVIAS A LOS TOKENS!!!")
                    print('---------------------------------------')
                    raise SystemExit
                if 'rule' in line:
                    if not 'rule tokens =' in line:
                        print('---------------------------------------')
                        print("ERROR: EXPRESIÓN DE TOKEN NO RECONOCIDA!!!")
                        print('---------------------------------------')
                        raise SystemExit
                if 'ids' in line:
                    print('---------------------------------------')
                    print("ERROR: TOKEN NO RECONOCIDO!!!")
                    print('---------------------------------------')
                    raise SystemExit
                    
                balance_score_paren = 0
                balance_score_mark = 0
                for c in [char for char in line]:
                    if not "'('" in line and not "')'" in line:
                        if c == '(' or c == ')':
                            balance_score_paren += 1
                    if c == "'":
                        balance_score_mark += 1
                if balance_score_mark%2 != 0 or balance_score_paren%2 != 0:
                    print('---------------------------------------')
                    print("ERROR: EXPRESIÓN DESBALANCEADA!!!")
                    print('---------------------------------------')
                    raise SystemExit
        
    def pre_fab(self):
        patterns_ax = { "'A'-'Z'": [chr(i) for i in range(ord('A'), ord('Z')+1)],
                              "'a'-'z'": [chr(i) for i in range(ord('a'), ord('z')+1)],
                              "'0'-'9'": [chr(i) for i in range(ord('0'), ord('9')+1)],
                              "(_)*":['_','_']}
        for i in patterns_ax:
            patterns_ax[i] = [letra + "|" for letra in patterns_ax[i]]
            patterns_ax[i][-1] = patterns_ax[i][-1][0]
        return patterns_ax
        
    def pattern_xtension(self, raw_pattern, previus_pattern):
        
        section = raw_pattern
        if previus_pattern + "+" in raw_pattern:
            section = "(" + previus_pattern + ")" + "(" + previus_pattern + "*)"
        
        if "?" in raw_pattern:
            raw_deconst = [char for char in raw_pattern]
            aux_constr = []
            for e in raw_deconst:
                # Si identifica un ?
                if e == '?':
                    internal = ""
                    prev = aux_constr.pop()
                    # Identifica si es un ) o un ]
                    if prev == ")":
                        par_finder = ""
                        # Buscara todo lo que haya dentro del paréntesis
                        while par_finder != "(":
                            par_finder = aux_constr.pop()
                            if par_finder != "(":
                                internal = par_finder + internal
                        # Modificará el contenido extraído
                        internal = "(" + "(" + internal + ")" + "|" + "ε)"
                        aux_constr.append(internal)
                        
                    elif prev == "]":
                        
                        par_finder = ""
                        # Buscara todo lo que haya dentro del corchete
                        while par_finder != "[":
                            par_finder = aux_constr.pop()
                            if par_finder != "[":
                                internal = par_finder + internal
                        # Modificará el contenido extraído
                        internal = internal.split("'")
                        internal = ''.join(internal)
                        aux = ""
                        for k in internal:
                            aux += k + "|"
                        internal = aux
                        internal = "(" + internal + "ε)"
                        aux_constr.append(internal)
                       
                else:
                    aux_constr.append(e)
                
                section = ''.join(aux_constr)
        
        
        return section
          
    def pattern_translation(self, raw_pattern, patterns):
        raw_pattern = raw_pattern.replace('\\s',' ')
        raw_pattern = raw_pattern.replace('\\t','\t')
        raw_pattern = raw_pattern.replace('\\n','\n')
        raw_pattern = raw_pattern.replace('(_)*','_|\_')
        pep = self.pre_exist_patterns
        aux_pattern = []
        section = ''
        # Si comienza con [ ] se los retira
        # if "'" in raw_pattern:
        #     raw_pattern = raw_pattern.replace("'","")
        if raw_pattern.startswith("[") and raw_pattern.endswith("]"):  
            raw_pattern = raw_pattern[1:-1]
            if raw_pattern.startswith('"') and raw_pattern.endswith('"'):
                raw_pattern = raw_pattern[1:-1]
                
                if '\\' in raw_pattern:
                    ax = ''
                    raw_pattern = [x for x in raw_pattern.split('\\') if x]
                    
                    for e in range(len(raw_pattern)):
                        ax = ax + '\\' + raw_pattern[e]
                        if e != len(raw_pattern) - 1:   
                            ax = ax + '|'
                    raw_pattern = ax
                else:
                    ax = ''
                    for e in range(len(raw_pattern)):
                        ax = ax + raw_pattern[e]
                        if e != len(raw_pattern) - 1:   
                            ax = ax + '|'
                    raw_pattern = ax
            
            

            # Si identifica un patron pre-existente lo traduce
            for i in pep.keys():
                if i in raw_pattern:
                    raw_pattern = raw_pattern.replace(i,'')
                    if len(aux_pattern) != 0:
                        aux_pattern.append('|')
                        aux_pattern = aux_pattern + pep[i]
                    elif len(aux_pattern) == 0:
                        aux_pattern = aux_pattern + pep[i]
        # Si identifica una patrón participe dentro de otro patrón
        for j in patterns.keys():
            if j in raw_pattern:
                section = self.pattern_xtension(raw_pattern, j)
                return section
        
        if "'" in raw_pattern:
            raw_pattern = (raw_pattern.split("'"))
            aux = []
            for i in raw_pattern:
                if i != '':
                    aux.append(i)
                    aux.append('|')
            aux.pop()
            section = ''.join(aux)
            return "("+section+")"
        
        
        section = list(filter(None,raw_pattern.split("'")))
        section = section + aux_pattern
        
        section = ''.join(section)
        
        return "("+section+")"
    
    def reader(self, path):
        

        with open(path) as file:
            rule_score = 0
            jump_score = 0
            patterns = {}
            tokens = {}
            # Inicializar lista vacía
            
            # Leer archivo línea por línea
            for line in file:
                # Buscar "let" en la línea
                if 'let' in line:
                    # Obtener la variable después de "let" eliminando los espacios en blanco y el salto de línea
                    var = line.split("let ")[1].strip()
                    pattern_name = var.split("=")[0].strip()
                    pattern = var.split("=")[1].strip()
                    
                    
                    pattern = self.pattern_translation(pattern, patterns)
                    
                    available_patterns = []
                    for l in patterns.keys():
                        if l in pattern:
                            available_patterns.append(l)
                    
                    for m in range(len(available_patterns)-1, -1, -1):
                        ava_aux = available_patterns[m]
                        pattern = pattern.replace(ava_aux, patterns[ava_aux])
                    
                    if "'" in pattern:
                        pattern = pattern.replace("'", '')
                    patterns[pattern_name] = pattern
                
                elif 'rule tokens' in line:
                    rule_score += 1
                
                elif rule_score != 0:
                    partes = []
                    # Verificar si la línea contiene un token

                    # Separar la línea en el token y su acción de retorno
                    if '|' in line:
                        partes = line.split('|')
                        partes = partes[1].split()
                        
                    else:
                        partes = line.split()
                    
                    
                    if len(line) == 1:
                        jump_score += 1
                    
                    if jump_score == 0:
                        try:
                            token = partes[0]
                            if "'" in token:
                                token = token.replace("'","")
                            elif '"' in pattern:
                                token = token.replace('"', '')
                            action = partes[3]
                            tokens[token] = action
                        except Exception:
                            token = partes[0]
                            action = ''
                            tokens[token] = action
                    # Agregar el token y su acción de retorno al diccionario
                # Imprimir el diccionario resultante
            
            return patterns, tokens

    def afn_union(self, patterns):
        afds = []
        for i in patterns:
            score = 0
            N = NFA()
            F = FDA()
            lib = Libs(patterns[i])
            postfix = lib.get_postfix()
            # print(postfix)
            N.thompson(postfix)
            a,b = F.subConstruct(N.AFN_transitions, N.get_acceptance_state()+1)
            
            afds.append(b)
            
        return afds, patterns

    def file_generator(self, afds, patterns, tokens):
        
        json_afds = json.dumps(afds, indent=4,ensure_ascii=False)
        json_patterns = json.dumps(patterns, indent=4)
        json_tokens = json.dumps(tokens)
        # print(tokens)
        
        with open("test.py", "w", encoding='utf-8') as archivo:
            archivo.write(f"from labB import *\n")
            archivo.write(f"afds = {json_afds}\n")
            archivo.write(f"patterns = {json_patterns}\n\n")
            archivo.write(f"tokens ={json_tokens}\n")
            archivo.write("class Test:\n")
            archivo.write("    def identifyer2(self, w):\n")
            # archivo.write("        print(w)\n")
            # archivo.write("        input('WAITING FOR APPROVAL')\n")
            archivo.write("        fda = FDA()\n")
            archivo.write("        identified_patterns = []\n")
            archivo.write("        printable = []\n")
            archivo.write("        pass_counter = 0\n")
            archivo.write("        stored_pattern = \"\"\n")
            archivo.write("        result = \"\"\n")
            archivo.write("        aux_flag = False\n")
            archivo.write("        aux_flag_dot = False\n")
            archivo.write('        aux_flag_d_dot = False\n')
            archivo.write("        for flag, i in enumerate(patterns):\n")
            archivo.write("            patterns[i] = afds[flag]\n")
            archivo.write("        w = list(w)\n")
            archivo.write("        aux_w = \"\"\n")
            archivo.write("        while w:\n")
            archivo.write("            pass_counter = 0\n")
            archivo.write("            aux_w += w.pop(0)\n")
            archivo.write("            for pattern in patterns:\n")
            archivo.write("                b = patterns[pattern]\n")
            archivo.write("                result = fda.afd_simulation(aux_w, b)\n")
            archivo.write("                if result == \"PASS\":\n")
            archivo.write("                    stored_pattern = pattern\n")
            archivo.write("                    pass_counter += 1\n")
            archivo.write("                elif result == \"FAIL\":\n")
            archivo.write("                    if (\n")
            archivo.write("                        \".\" in aux_w\n")
            archivo.write("                        and pattern == stored_pattern\n")
            archivo.write("                        and \"E\" not in aux_w\n")
            archivo.write("                        and aux_flag_dot == False\n")
            archivo.write("                    ):\n")
            archivo.write("                        try:\n")
            archivo.write("                            aux_future_w = aux_w + w[0]\n")
            archivo.write("                            for pattern in patterns:\n")
            archivo.write("                                b = patterns[pattern]\n")
            archivo.write("                                result = fda.afd_simulation(aux_future_w, b)\n")
            archivo.write("                                if result == \"PASS\":\n")
            archivo.write("                                    w.pop(0)\n")
            archivo.write("                                    aux_w = aux_future_w\n")
            archivo.write("                                    stored_pattern = pattern\n")
            archivo.write("                                    pass_counter += 1\n")
            archivo.write("                                    aux_flag_dot = True\n")
            archivo.write("                        except Exception:\n")
            archivo.write("                            pass\n")
            archivo.write("                    elif 'E' in aux_w and pattern == stored_pattern and aux_flag == False:\n")
            archivo.write("                        try:\n")
            archivo.write("                            aux_future_w = aux_w + w[0]\n")
            archivo.write("                            for pattern in patterns:\n")
            archivo.write("                                b = patterns[pattern]\n")
            archivo.write("                                result = fda.afd_simulation(aux_future_w, b)\n")
            archivo.write("                                if result == \"PASS\":\n")
            archivo.write("                                    w.pop(0)\n")
            archivo.write("                                    aux_w = aux_future_w\n")
            archivo.write("                                    stored_pattern = pattern\n")
            archivo.write("                                    pass_counter += 1\n")
            archivo.write("                                elif result == 'FAIL':\n")
            archivo.write("                                    aux_future_w = aux_w + w[0] + w[1]\n")
            archivo.write("                                    for pattern in patterns:\n")
            archivo.write("                                        b = patterns[pattern]\n")
            archivo.write("                                        result = fda.afd_simulation(aux_future_w, b)\n")
            archivo.write("                                        if result == \"PASS\":\n")
            archivo.write("                                            w.pop(0)\n")
            archivo.write("                                            w.pop(0)\n")
            archivo.write("                                            aux_w = aux_future_w\n")
            archivo.write("                                            stored_pattern = pattern\n")
            archivo.write("                                            pass_counter += 1\n")
            archivo.write("                                            aux_flag = True\n")
            archivo.write("                        except Exception:\n")
            archivo.write("                            pass\n")
            archivo.write("                    elif (\n")
            archivo.write("                        \":\" in aux_w\n")
            archivo.write("                        and aux_flag_d_dot == False\n")
            archivo.write("                        and len(aux_w) == 1\n")
            archivo.write("                    ):\n")
            archivo.write("                        try:\n")
            archivo.write("                            aux_future_w = aux_w + w[0]\n")
            archivo.write("                            if aux_future_w in tokens:\n")
            archivo.write("                                identified_patterns.append(aux_future_w)\n")
            archivo.write("                                printable.append({str(aux_future_w):str(tokens[aux_future_w])})\n")
            archivo.write("                                w.pop(0)\n")
            archivo.write('                                aux_w = ""\n')
            archivo.write('                                stored_pattern = ""\n')
            archivo.write('                                pass_counter += 1\n')
            archivo.write('                                aux_flag = False\n')
            archivo.write('                                aux_flag_dot = False\n')
            archivo.write('                                aux_flag_d_dot = False\n')
            archivo.write("                        except Exception:\n")
            archivo.write("                            pass\n")
            
            #  elif aux_w in tokens and not stored_pattern:\n')
            # archivo.write('                        identified_patterns.append(aux_w)\n')
            # archivo.write('                        if aux_w in tokens:\n')
            # archivo.write('                            printable.append(\'< \' + str(aux_w) + \'->\' + str(tokens[aux_w]) + \' >\')\n')
            
            
            
            archivo.write('                    elif pattern == stored_pattern:\n')
            archivo.write('                        identified_patterns.append(aux_w[:-1])\n')
            archivo.write('                        if pattern in tokens:\n')
            archivo.write('                            printable.append({str(aux_w[:-1]):str(tokens[pattern])})\n')
            archivo.write('                        w.insert(0, aux_w[-1])\n')
            archivo.write('                        aux_w = ""\n')
            archivo.write('                        stored_pattern = ""\n')
            archivo.write('                        pass_counter += 1\n')
            archivo.write('                        aux_flag = False\n')
            archivo.write('                        aux_flag_dot = False\n')
            archivo.write('                        aux_flag_d_dot = False\n')
            archivo.write('                    elif aux_w in tokens and not stored_pattern:\n')
            archivo.write('                        identified_patterns.append(aux_w)\n')
            archivo.write('                        if aux_w in tokens:\n')
            archivo.write('                            printable.append({str(aux_w):str(tokens[aux_w])})\n')
            archivo.write('                        aux_w = ""\n')
            archivo.write('                        stored_pattern = ""\n')
            archivo.write('                        pass_counter += 1\n')
            archivo.write('                        aux_flag = False\n')
            archivo.write('                        aux_flag_dot = False\n')
            archivo.write('                        aux_flag_d_dot = False\n')
            archivo.write('            if pass_counter == 0:\n')
            archivo.write('                aux_w = ""\n')
            archivo.write('        if aux_w:\n')
            archivo.write('            identified_patterns.append(aux_w)\n')
            archivo.write('            if stored_pattern in tokens:\n')
            archivo.write('                printable.append({str(aux_w):str(tokens[stored_pattern])})\n')
            
            archivo.write('        stored_pattern = ""\n')
            archivo.write('        for i in identified_patterns:\n')
            archivo.write('            for pattern in patterns:\n')
            archivo.write('                b = patterns[pattern]\n')
            archivo.write('                result = fda.afd_simulation(i, b)\n')
            archivo.write('                if result == "PASS":\n')
            archivo.write('                    stored_pattern = pattern\n')
            archivo.write('            try:\n')
            archivo.write('                if i not in tokens:\n')
            archivo.write('                    tokens[stored_pattern]\n')
            archivo.write('            except Exception:\n') 
            archivo.write('                print(f"------------------\\nERROR: {i} Token not found!!!\\n------------------")\n')
            archivo.write('                raise SystemExit\n')
            archivo.write('        return printable\n')
            
            # archivo.write('t = Test()\n')
            # archivo.write('with open("Testing/slr-1.1.yal.run", "r") as f:\n')
            # archivo.write('    for line in f:\n')
            # archivo.write('        print("------------W------------")\n')
            # archivo.write('        print(line)\n')
            # archivo.write('        print("-------------------------")\n')
            # archivo.write('        aux_list = t.identifyer2(line)\n')
            # archivo.write('        print(aux_list)\n')
            
            archivo.write('import json\n')
            archivo.write('values = tokens.values()\n')
            archivo.write('with open("YALex.json", "w") as file:\n')
            archivo.write('    json.dump(list(values), file)\n')
            

    
            


path = 'inputs/slr-1.yal'
L = Lexer()
patterns, tokens  = L.reader(path)
L.pre_load(path)
afds, patterns = L.afn_union(patterns)
L.file_generator(afds, patterns, tokens)
