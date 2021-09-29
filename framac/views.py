import datetime
import subprocess
import importlib.util
import pathlib
from .file_parser import make_sections, parse_framac

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, include, path

from django.views.generic.edit import UpdateView
from .models import Directory, File, FileSection, User, TimeValidity

from .forms import FileForm, DirectoryForm, DeleteDirForm, ProverForm, VeriFrorm, UserForm
from . import variables

import json
from django.template import RequestContext

main_html = None
framac_out = str()
code_content = str()

tab_content = None
current_tab = None
options = str()

name_now = str()
current_file = str()

prover = "alt-ergo"
prover_chosen = None


def test(request):
    return render(request, 'framac/test.html')


def get_real(path):
    ans = str()
    for i in path:
        if i == '/':
            del ans
            ans = ""
        else:
            ans += i
    return ans


def get_hierarchy(current, html_out):
    html_out += '<li class="directory">' + get_real(
        current.name) + '<span class="full-path">' + current.name + '</span>' + "</li>"
    html_out += "<ul>"
    dir_set = Directory.objects.filter(availability_flag=True, is_placed_in=current, owner=variables.user_model)
    for dir in dir_set.iterator():
        html_out += get_hierarchy(dir, "")

    file_set = File.objects.filter(availability_flag=True, is_placed_in=current, owner=variables.user_model)
    for file in file_set.iterator():
        html_out += '<li class="file"><a id="my' + file.name + '" href="/files' + file.name + '"> •' + get_real(
            file.name) + '<span class="full-path">' + file.name + '</span>' + "</a></li>"

    html_out += "</ul>"
    return html_out


def load_main():
    global main_html
    dir_set = Directory.objects.filter(availability_flag=True, is_placed_in=None, owner=variables.user_model)
    main_html = "<ul>"
    for dir in dir_set.iterator():
        main_html += get_hierarchy(dir, "")

    main_html += "</ul>"
    main_html += "<ul>"
    file_set = File.objects.filter(availability_flag=True, is_placed_in=None, owner=variables.user_model)
    for file in file_set.iterator():
        main_html += '<li class="file"><a id="my' + file.name + '" href="/files' + file.name + '"> •' + get_real(
            file.name) + '<span class="full-path">' + file.name + '</span>' + "</a></li>"
    main_html += "</ul>"


def index(request):
    global main_html
    global current_tab
    global framac_out
    global code_content
    global current_file

    if variables.user_now:
        if main_html is None:
            load_main()

        global tab_content

        context = {'directories': Directory.objects.filter(availability_flag=True),
                   'files': File.objects.filter(availability_flag=True),
                   'users': User.objects.all(),
                   'file_selection': main_html,
                   'focus_on_elems': framac_out,
                   'highlighted': code_content,
                   'tab_content': tab_content,
                   'prover_tab': current_tab,
                   'current_file': current_file,
                   'user_now': variables.user_now}
        return render(request, 'framac/index.html', context)

    else:
        global prover
        global options
        global prover_chosen
        options = ""
        code_content = ""
        tab_content = None
        framac_out = ""
        main_html = None
        current_tab = None
        prover = "alt-ergo"
        current_file = ""
        prover_chosen = None

        return HttpResponseRedirect('/login/')


def addFile(request):
    if request.method == 'POST':
        gForm = FileForm(request.POST, request.FILES)
        if gForm.is_valid():
            p = File()
            p.name = '/' + gForm.cleaned_data['name']
            p.description = request.POST.get('description', '')
            vOwner = request.POST.get('owner', '')
            p.code = request.FILES['file']
            vPlacedIn = request.POST.get('placed_in', '')

            p.owner = variables.user_model
            if vPlacedIn != '':
                try:
                    p.is_placed_in = Directory.objects.get(name=vPlacedIn)
                except Directory.DoesNotExist:
                    return render(request, 'framac/addFile.html',
                                  {'form': gForm, 'error': "Directory owner doesn't exist!"})
                p.name = p.is_placed_in.name + p.name

                try:
                    bulbul = Directory.objects.get(name=p.name)
                    return render(request, 'framac/addFile.html',
                                  {'form': gForm, 'error': "File has the same name as directory, that can't be!"})
                except Directory.DoesNotExist:
                    a = 1

            p.creation_date = datetime.date.today()
            p.availability_flag = True

            time_valid = TimeValidity()
            time_valid.creation_date = datetime.date.today()
            time_valid.is_valid = True

            time_valid.save()

            p.timestamp_validity = time_valid

            p.save()

            make_sections(p.code, p.owner, p)
            global main_html
            main_html = None
            return HttpResponseRedirect('/addedFile/')

    else:
        gForm = FileForm()

    return render(request, 'framac/addFile.html', {'form': gForm})


def addDirectory(request):
    if request.method == 'POST':
        dForm = DirectoryForm(request.POST)

        if dForm.is_valid():
            p = Directory()
            p.name = '/' + dForm.cleaned_data['name']
            p.description = request.POST.get('description', '')
            vPlacedIn = request.POST.get('placed_in', '')

            p.owner = variables.user_model

            if vPlacedIn != '':
                try:
                    p.is_placed_in = Directory.objects.get(name=vPlacedIn)
                except Directory.DoesNotExist:
                    return render(request, 'framac/addDirectory.html',
                                  {'form': dForm, 'error': "Directory owner doesn't exist!"})
                p.name = p.is_placed_in.name + p.name

            p.creation_date = datetime.date.today()
            p.availability_flag = True

            time_valid = TimeValidity()
            time_valid.creation_date = datetime.date.today()
            time_valid.is_valid = True

            time_valid.save()

            p.timestamp_validity = time_valid

            p.save()
            global main_html
            main_html = None
            return render(request, 'framac/addDirectory.html', {'form': dForm})

    else:
        dForm = DirectoryForm()

    return render(request, 'framac/addDirectory.html', {'form': dForm})


def disable_avail(dir_now):
    dir_now.availability_flag = False
    dir_set = Directory.objects.filter(availability_flag=True, is_placed_in=dir_now)
    for dir in dir_set.iterator():
        disable_avail(dir)

    file_set = File.objects.filter(availability_flag=True, is_placed_in=dir_now)
    for file in file_set.iterator():
        file.availability_flag = False
        file.save()
    dir_now.save()


def delete(request):
    if request.method == 'POST':
        dForm = DeleteDirForm(request.POST)
        if dForm.is_valid():
            targetName = dForm.cleaned_data['choice']
            what = targetName[0]
            targetName = targetName[1:]
            if what == 'd':
                target = Directory.objects.get(name=targetName)
                disable_avail(target)
            else:
                target = File.objects.get(name=targetName)
                target.availability_flag = False
                target.save()

            global main_html
            main_html = None
            return HttpResponseRedirect('/deleteDone/')
    else:
        dForm = DeleteDirForm()

    return render(request, 'framac/delete.html', {'form': dForm})


def deleteDone(request):
    return render(request, 'framac/deleted.html')


def addedFile(request):
    return render(request, 'framac/addedFile.html')


def addedDirectory(request):
    return render(request, 'framac/addedDirectory.html')


keywords = {
    'requires',
    'ensures',
    'assert',
    'axiom',
    'predicate',
    'assumes',
    'invariant'
}

def check_key(reti, key):
    print(key)
    place = reti.find(key)

    if place != -1:
        real_ret = reti[:place] + '<b>' + reti[place:]
        reti = real_ret

        place = reti.find(key)

        real_ret = reti[:(place + len(key))] + '</b>' + reti[(place + len(key)):]

        reti = real_ret

    return reti


def regulate(line):
    reti = str()

    if line.find('@') != -1 or line.find('//') != -1:
        reti += '<span class="comment">'

    last_char = 'a'
    for char in line:
        if last_char == '<' and char != ' ':
            reti += ' '
        reti += char
        last_char = char

    if line.find('@') != -1 or line.find('//') != -1:
        reti += '</span>'

    real_ret = str()
    for key in keywords:
        reti = check_key(reti, key)

    reti = check_key(reti, 'variant')
    return reti + '\n'


def showFile(request, filePath):
    global main_html
    if main_html is None:
        load_main()

    global name_now
    global code_content
    global framac_out
    global current_file
    filePath = '/' + filePath
    file = File.objects.get(name=filePath)
    my_file = file.code.open()

    if my_file.name != name_now:
        current_file = filePath
        code_content = my_file.read()

        wurr = str(code_content)

        wurr = wurr.replace('"', "'")
        wurr = wurr[2:]
        wurr = wurr[:-1]

        code_content = wurr

        name_now = my_file.name

        global prover
        bashCmd = ["frama-c", "-wp", "-wp-print", "-wp-prover", prover, "media/" + name_now]
        process = subprocess.Popen(bashCmd, stdout=subprocess.PIPE)
        output, error = process.communicate()
        output = output.decode()

        if error is not None:
            framac_out = "<div class='main-text'>ERROR DURING PARSING FRAMA-C OUTPUT: </div><br>"
        else:
            framac_out = parse_framac(output)

    context = {'directories': Directory.objects.filter(availability_flag=True),
               'files': File.objects.filter(availability_flag=True),
               'users': User.objects.all(),
               'highlighted': code_content,
               'file_selection': main_html,
               'focus_on_elems': framac_out,
               'current_file': current_file}

    return render(request, 'framac/index.html', context)


def provers(request):
    global main_html
    if main_html is None:
        load_main()
    global tab_content

    nice_prover = ""
    if request.method == 'POST':
        pForm = ProverForm(request.POST)
        if pForm.is_valid():
            choice = pForm.cleaned_data['Provers']

            global prover
            prover = choice

            nice_prover = "<p>Prover successfully chosen!<p>"

    pForm = ProverForm()
    tab_content = pForm

    global current_tab
    current_tab = 'provers'

    context = {'directories': Directory.objects.filter(availability_flag=True),
               'files': File.objects.filter(availability_flag=True),
               'users': User.objects.all(),
               'file_selection': main_html,
               'focus_on_elems': framac_out,
               'highlighted': code_content,
               'tab_content': tab_content,
               'tab_info': nice_prover,
               'prover_tab': current_tab,
               'current_file': current_file}

    return render(request, 'framac/index.html', context)


def verification(request):
    global main_html
    if main_html is None:
        load_main()

    global tab_content

    nice_prover = ""
    if request.method == 'POST':
        pForm = VeriFrorm(request.POST)
        if pForm.is_valid():
            choice = pForm.cleaned_data['Properties']

            global options
            options = ""
            got_prop = False
            for prop in choice:
                if prop == " -wp-rte":
                    options += prop
                    continue
                elif not got_prop:
                    options += ' -wp-prop="'
                    got_prop = True
                options += prop

            if got_prop:
                options += '"'

            nice_prover = "<p>Properties successfully chosen!<p>"
    else:
        pForm = VeriFrorm()

    tab_content = pForm

    global current_tab
    current_tab = 'verification'

    context = {'directories': Directory.objects.filter(availability_flag=True),
               'files': File.objects.filter(availability_flag=True),
               'users': User.objects.all(),
               'file_selection': main_html,
               'focus_on_elems': framac_out,
               'highlighted': code_content,
               'tab_content': tab_content,
               'tab_info': nice_prover,
               'prover_tab': current_tab,
               'current_file': current_file}

    return render(request, 'framac/index.html', context)


def result(request):
    global main_html
    if main_html is None:
        load_main()

    global name_now
    global tab_content
    global current_tab
    if len(name_now) != 0:
        res = 'r:result.txt'
        bashCmd = ["frama-c", "-wp", '-wp-log=' + res, "media/" + name_now]
        process = subprocess.Popen(bashCmd, stdout=subprocess.PIPE)
        output, error = process.communicate()
        file = open("result.txt", "r").read().replace('\n', '<br>')

        tab_content = file
    else:
        tab_content = "<p>You haven't chosen any file!<p>"

    current_tab = 'result'

    context = {'directories': Directory.objects.filter(availability_flag=True),
               'files': File.objects.filter(availability_flag=True),
               'users': User.objects.all(),
               'file_selection': main_html,
               'focus_on_elems': framac_out,
               'highlighted': code_content,
               'tab_content': tab_content,
               'prover_tab': current_tab,
               'current_file': current_file}

    return render(request, 'framac/index.html', context)


def rerun(request):
    global main_html
    if main_html is None:
        load_main()

    global name_now
    global tab_content
    global current_tab

    if len(name_now) != 0:
        global options

        if len(options) != 0:
            bashCmd = 'frama-c -wp -wp-print' + options + ' media/' + name_now
            bashCmd = bashCmd.split()
        else:
            global prover
            bashCmd = ["frama-c", "-wp", "-wp-print", "-wp-prover", prover, "media/" + name_now]

        process = subprocess.Popen(bashCmd, stdout=subprocess.PIPE)
        output, error = process.communicate()
        output = output.decode()

        global framac_out
        framac_out = parse_framac(output)
        if framac_out == "None":
            framac_out = "<div class='main-text'>ERROR DURING PARSING FRAMA-C OUTPUT: </div><br>"
            framac_out += output
    else:
        framac_out = "<div class='main-text'>Select a file first, then run verification!</div>"

    context = {'directories': Directory.objects.filter(availability_flag=True),
               'files': File.objects.filter(availability_flag=True),
               'users': User.objects.all(),
               'highlighted': code_content,
               'file_selection': main_html,
               'focus_on_elems': framac_out,
               'tab_content': tab_content,
               'prover_tab': current_tab,
               'current_file': current_file}

    return render(request, 'framac/index.html', context)


def login(request):
    if request.method == 'POST':
        uForm = UserForm(request.POST)
        if uForm.is_valid():

            uLogin = uForm.cleaned_data['login']
            uPass = request.POST.get('password', '')

            try:
                variables.user_model = User.objects.get(login=uLogin, password=uPass)
            except User.DoesNotExist:
                return render(request, 'framac/login.html',
                              {'form': uForm, 'error': "User doesn't exist!"})


            variables.user_now = uLogin
            return HttpResponseRedirect('/')

    else:
        uForm = UserForm()

    return render(request, 'framac/login.html', {'form': uForm})


def logout(request):
    global main_html
    variables.user_now = None
    variables.user_model = None
    main_html = None

    return HttpResponseRedirect('/')