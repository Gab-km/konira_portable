from tokenize           import NAME, OP, STRING, generate_tokens
import re



def quote_remover(string):
    _string = string.replace(",", "").replace(".", "")
    return _string.replace("'", "")


def valid_method_name(token):
    transform = token.strip().replace(" ", "_").replace("\"","" )
    return "it_%s" % quote_remover(transform)


def valid_class_name(token):
    transform = token.strip().replace(" ", "_").replace("\"","" )
    return "Case_%s" % quote_remover(transform)


def valid_raises(value):
    if not value: 
        return True
    whitespace = re.compile(r'^\s*$')
    if whitespace.match(value):
        return True
    return False
    

def translate(readline):
    result     = []
    last_kw    = None
    last_token = None
    last_type  = None
    descr_obj  = False

    for tokenum, value, _, _, _ in generate_tokens(readline):

        # From Describe to class - includes inheritance
        if tokenum == NAME and value == 'describe':
            last_kw = 'describe'
            result.extend(([tokenum, 'class'],))
        elif tokenum == STRING and last_token == 'describe':
            last_kw   = 'describe'
            descr_obj = True
            result.extend(([NAME, valid_class_name(value)],))

        elif tokenum == OP and value == ',' and last_type == STRING and last_kw == 'describe':
            if descr_obj:
                result.extend(([OP, '('],))
                last_kw   = 'describe'
                descr_obj = True

        elif tokenum == NAME and last_type == OP and last_kw == 'describe':
            if descr_obj:
                result.extend(([NAME, value],
                               [OP, ')'],))
                last_kw   = None
                descr_obj = False

        elif last_type == STRING and last_kw == 'describe':
            if descr_obj:
                result.extend(([OP, '('],
                               [NAME, 'object'],
                               [OP, ')'],
                               [OP, ':'],))
                last_kw   = None
                descr_obj = False

        # Skip if Constructors
        elif tokenum == NAME and value == 'skip':
            result.extend(([tokenum, 'def'],))

        elif tokenum == NAME and last_token == 'skip' and value == 'if':
            result.extend(([tokenum, '_skip_if'],
                           [OP, '('],
                           [NAME, 'self'],
                           [OP, ')']))

        # Before Constructors
        elif tokenum == NAME and value == 'before':
            result.extend(([tokenum, 'def'],))

        elif tokenum == NAME and last_token == 'before':
            result.extend(([tokenum, '_before_%s' % value],
                           [OP, '('],
                           [NAME, 'self'],
                           [OP, ')']))

        # After Constructors
        elif tokenum == NAME and value == 'after':
            result.extend(([tokenum, 'def'],))

        elif tokenum == NAME and last_token == 'after':
            result.extend(([tokenum, '_after_%s' % value],
                           [OP, '('],
                           [NAME, 'self'],
                           [OP, ')']))

        # From it to def
        elif tokenum == NAME and value == 'it':
            result.extend(([tokenum, 'def'],))
        elif tokenum == STRING and last_token == 'it':
            result.extend(([tokenum, valid_method_name(value)],
                           [OP, '('],
                           [NAME, 'self'],
                           [OP, ')'],))

        # From raises to with konira.tools.raises
        elif tokenum == NAME and value == 'raises' and valid_raises(last_token):
            result.extend(([tokenum, 'with konira.tools.raises'],))

        elif tokenum == NAME and last_token == 'raises':
            result.extend(([OP, '('],
                           [NAME, value],
                           [OP, ')'],))

        else:
            result.append([tokenum, value])
        last_token = value
        last_type  = tokenum
    
    return result
