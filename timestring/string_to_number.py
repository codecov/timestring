import re

try:
    unicode
except NameError:
    unicode = str
    long = int

def string_to_number(text):
    '''
    Used to evaluate string that are numbers
    #### Examples
    1. `four hundred` == `4 * 100` == `400`
    2. `sixty three thousand` == `(60+3) * 1000` == `63000`
    3. `one hundred thirty five` == `1 * 100 + (30+5)` == 135`
    4. `three hundred fifty two thousand seven hundred sixty one` = `(3 * 100 + (50 + 2)) * 1000 + 7 * 100 + (60 + 1)` == `352,761`
    '''
    if type(text) is str:
        try:
            # the text may already be a number.
            float(text.replace(',', ''))
            return float(text)
        except ValueError:
            text = text.lower()
            r = dict(one=1, two=2, three=3, four=4, five=5, six=6, seven=7, eight=8, nine=9, ten=10, eleven=11, twelve=12, thirteen=13, fourteen=14, fifteen=15, sixteen=16, seventeen=17, eighteen=18, nineteen=19, twenty=20, thirty=30, fourty=40, fifty=50, sixty=60, seventy=70, eighty=80, ninety=90, hundred=100)
            s = re.sub('(?P<s>\s)(?P<n>hundred|thousand)', lambda m: ' * %s' % r.get(m.groupdict().get('n')), text)
            s = re.sub('((one|two|twenty|twelve|three|thirty|thirteen|four(teen|ty)?|five|fif(teen|ty)|six(teen|ty)?|seven(teen|ty)?|eight(een|y)?|nine(teen|ty)?|ten|eleven)\s?)+', lambda m: "(%s) " % '+'.join(map(lambda n: str(r.get(n)), m.group().strip().split(' '))), s)
            if re.search('/[a-z]/', s):
                raise ValueError("Invalid characters in number string.")
            try:
                return eval(s)
            except SyntaxError:
                raise ValueError("Invalid number string.")
    else:
        return text
