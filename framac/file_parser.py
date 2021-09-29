from .models import Directory, File, FileSection, User, TimeValidity, SectionCategory, SectionStatus, StatusData
import datetime

keywords = [('requires', 'PR'),
            ('ensures', 'PP'),
            ('assert', 'AS'),
            ('axiom', 'LM'),
            ('predicate', 'PO'),
            ('assumes', 'PR'),
            ('invariant', 'PC'),
            ('variant', 'PC')]

def make_sections(file, user, modelFile):

    global lines
    global i
    anwser = list()

    content = file.read()

    if isinstance(content, str) is False:
        normalized = content.decode()
    else:
        normalized = content

    lines = normalized.split('\n')

    def find_text(text):
        global i
        while True:
            if lines[i].find(text) != -1:
                return i
            i = i + 1

    for i in range(0, len(lines)):
        line = lines[i]
        if line.find('@') == -1:
            if line.find('/*') != -1:
                anwser.append(('comment', i + 1, find_text('*/') + 1))
            if line.find('//') != -1:
                anwser.append(('comment', i + 1, i + 1))
            continue

        for key in keywords:
            if line.find(key[0]) != -1:
                anwser.append((key[0], i + 1, find_text(";") + 1))
                break

    for elem in anwser:
        category = elem[0]
        cfrom, cto = elem[1], elem[2]

        section = FileSection()
        section.creation_date = datetime.date.today()
        section.line_from = cfrom
        section.line_to = cto

        scat = SectionCategory()

        for key in keywords:
            if key[0] == category:
                scat.category = key[1]
                break

        timeVal = TimeValidity()
        timeVal.creation_date = datetime.date.today()
        timeVal.is_valid = True
        timeVal.save()

        scat.timestamp_validity = timeVal

        stat = SectionStatus()
        stat.available_status = 'UC'
        stat.timestamp_validity = timeVal

        scat.status = stat

        sdata = StatusData()
        sdata.status_data_field = 'Not existant'
        sdata.user = user
        sdata.timestamp_validity = timeVal

        scat.status_data = sdata

        scat.timestamp_validity = timeVal
        scat.is_section_of = modelFile
        scat.is_subsection_of = None

        scat.save()
        section.save()


def parse_framac(input):
    lines = input.split('\n')

    def dash_lane(line):
        for k in range(0, len(line)):
            if line[k] != '-':
                return 0

        return 1

    global i
    for i in range(0, len(lines)):
        if dash_lane(lines[i]):
            break
    i = i + 1

    half_parsed = list()
    global j
    skip_to = -1
    for j in range(i, len(lines)):
        if not dash_lane(lines[j]) and skip_to <= j:
            tmp = j
            now = list()
            now.append(lines[j])
            for k in range(j + 1, len(lines)):
                if not dash_lane(lines[k]):
                    now.append(lines[k])
                else:
                    tmp = k
                    break

            skip_to = tmp
            half_parsed.append(now)

    anwser = list()
    gathered = list()
    function = str()

    for frag in half_parsed:
        if len(frag) == 1 and frag[0][0] == ' ':
            if len(gathered) != 0:
                anwser.append((function, gathered[:]))
            function = frag
            gathered.clear()
        else:
            idx = frag[0].find("line ") + 5
            str_num = str()
            for k in range(idx, len(frag[0])):
                sgn = ord(frag[0][k]) - 48
                if 0 <= sgn <= 9:
                    str_num += frag[0][k]
                else:
                    break

            idx = frag[-1].find("returns ") + 8
            ret = str()
            for k in range(idx, len(frag[-1])):
                if frag[-1][k] != ' ':
                    ret += frag[-1][k]
                else:
                    break

            if str_num is not None:
                gathered.append((str_num, ret, frag))

    anwser.append((function, gathered))

    html = str()
    func_nr = 0
    for func in anwser:
        func_nr += 1
        to_change = str(func[0])
        got_dash = False
        out = str()
        for i in to_change:
            if i == "'":
                if got_dash:
                    break
                got_dash = True
            else:
                out += i

        out = out[2:]

        func_str_nr = str(func_nr)


        html += '<div class="func-text">' + out + " section: </div><br>"
        goal_nr = 0
        for goal in func[1]:
            goal_nr += 1
            goal_uniq_name = '"' + "f" + func_str_nr + 'g' + str(goal_nr) + '"'
            checkbox = '<input type="checkbox" id=' + goal_uniq_name + 'name=' + goal_uniq_name + ' \
                                 checked onchange="hide_segment(this)"> Show Segment'
            html += checkbox

            goal_str_nr = '"' + "Gf" + func_str_nr + 'g' + str(goal_nr) + '"'

            if goal[1] == "Timeout":
                html += '<div class="interrupted" id = ' + goal_str_nr + '>'
            elif goal[1] == "Unknown":
                html += '<div class="unknown" id = ' + goal_str_nr + '>'
            elif goal[1] == "Failed":
                html += '<div class="failedH" id = ' + goal_str_nr + '>'
            elif goal[1] == 'Valid':
                html += '<div class="valid" id = ' + goal_str_nr + '>'
            else:
                html += '<div class="warning" id = ' + goal_str_nr + '>'

            for k in range(1, len(goal[2])):
                html += goal[2][k] + '<br>'

            name = str()
            for k in goal[2][0]:
                if k == '(':
                    break
                name += k

            if len(str(goal[0])) != 0:
                html += '<span class="code-number">' + name + ", line number " + str(goal[0]) + '</span>'

            html += "</div><br>"

            goal_str_nr = '"' + "Hf" + func_str_nr + 'g' + str(goal_nr) + '"'
            if goal[1] == "Timeout":
                html += '<div class="interruptedH" id = ' + goal_str_nr + '> Interrupted'
            elif goal[1] == "Unknown":
                html += '<div class="unknownH" id = ' + goal_str_nr + '> Unknown'
            elif goal[1] == "Failed":
                html += '<div class="failedH" id = ' + goal_str_nr + '> Failed'
            elif goal[1] == 'Valid':
                html += '<div class="validH" id = ' + goal_str_nr + '> Valid'
            else:
                html += '<div class="warningH" id = ' + goal_str_nr + '> Warning'

            if len(str(goal[0])) != 0:
                html += '<span class="code-number">' + name + ", line number " + str(goal[0]) + '</span>'

            html += "</div><br>"

    if html == "<div class='func-text'> section: </div><br>":
        return "None"
    return html
