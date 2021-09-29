from django.test import TestCase
import datetime
import os
from django.core.files.uploadedfile import SimpleUploadedFile

from framac.models import Directory, File, FileSection, TimeValidity, User, SectionStatus, SectionCategory, StatusData
from . import variables


# //////////////////////////////////// MODELS TESTS ///////////////////////////////////////////

class SubDirectoryTestCase(TestCase):
    def setUp(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        usr = User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)
        r = Directory.objects.create(name="root", creation_date=datetime.date.today(), timestamp_validity=tv, owner=usr,
                                     availability_flag=True)
        Directory.objects.create(name="under root", creation_date=datetime.date.today(), is_placed_in=r,
                                 timestamp_validity=tv, owner=usr, availability_flag=True)

    def test_subs(self):
        """If directory is subdirectory of another"""
        root = Directory.objects.get(name="root")
        uroot = Directory.objects.get(name="under root")
        self.assertEqual(root.creation_date, datetime.date.today())
        self.assertEqual(uroot.creation_date, datetime.date.today())
        self.assertEqual(uroot.is_placed_in, root)
        print("#MODELS: DIRECTORY# SUBDIRECTORIES TEST: OK")


class UTFDirNamesTestCase(TestCase):
    def setUp(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        usr = User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)
        Directory.objects.create(name="ሾቕኟᙶ😁😍", description="😠😭🙎✨🚀", creation_date=datetime.date.today(),
                                 timestamp_validity=tv, owner=usr, availability_flag=True)

    def test_utfs(self):
        """If UTF characters are accepted as directory names and descriptions"""
        utf_dir = Directory.objects.get(name="ሾቕኟᙶ😁😍")
        self.assertEqual(utf_dir.name, "ሾቕኟᙶ😁😍")
        self.assertEqual(utf_dir.description, "😠😭🙎✨🚀")
        print("#MODELS: DIRECTORY# DIRECTORY UTF-8 NAMES TEST: OK")


class FileNotLostTestCase(TestCase):
    def setUp(self):
        actual_file = SimpleUploadedFile(
            "best_file_eva.txt",
            b"these are the file contents!"
        )
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        usr = User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)
        File.objects.create(name="file", creation_date=datetime.date.today(), code=actual_file,
                            timestamp_validity=tv, owner=usr, availability_flag=True)
        File.objects.create(name="empty", creation_date=datetime.date.today(),
                            timestamp_validity=tv, owner=usr, availability_flag=True)

    def test_file_handling(self):
        """Appropriate handling and saving given file"""

        actual_file = SimpleUploadedFile(
            "best_file_eva.txt",
            b"these are the file contents!"
        )
        file = File.objects.get(name="file")
        self.assertEqual(file.code.open().read(), actual_file.open().read())
        empty_file = File.objects.get(name="empty")
        if empty_file.code is None:
            raise EmptyFileError
        print("#MODELS: FILE# FILE NOT LOST TEST: OK")


class ValidSubsectionTestCase(TestCase):
    def setUp(self):
        actual_file = SimpleUploadedFile(
            "sample_file.txt",
            b"these are the file contents!"
        )
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        usr = User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)
        file = File.objects.create(name="file", creation_date=datetime.date.today(), code=actual_file,
                                   timestamp_validity=tv, owner=usr, availability_flag=True)

        stat = SectionStatus()
        stat.available_status = 'UC'
        stat.timestamp_validity = tv
        stat.save()

        sdata = StatusData()
        sdata.status_data_field = 'Not existant'
        sdata.user = usr
        sdata.timestamp_validity = tv
        sdata.save()

        scat = SectionCategory(category="PR")
        scat.save()

        fs = FileSection.objects.create(name="fs", creation_date=datetime.date.today(), status=stat, status_data=sdata,
                                        section_category=scat,
                                        timestamp_validity=tv, is_section_of=file)
        FileSection.objects.create(name="fss", creation_date=datetime.date.today(), status=stat, status_data=sdata,
                                   section_category=scat,
                                   timestamp_validity=tv, is_section_of=file, is_subsection_of=fs)

    def test_sections(self):
        """Valid handling of sections and subsections"""
        file = File.objects.get(name="file")
        section = FileSection.objects.get(name="fs")
        subsection = FileSection.objects.get(name="fss")
        self.assertEqual(file, section.is_section_of)
        self.assertEqual(section, subsection.is_subsection_of)
        print("#MODELS: FILE + DIRECTORY# VALID SUBSECTIONS TEST: OK")


class ValidCategoryNamesTestCase(TestCase):
    def setUp(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        categories = [
            "PC",
            "PP",
            'LM',
            'AS',
            'IN',
            'PR',
            'PO',
        ]

        for cat in categories:
            SectionCategory.objects.create(category=cat, timestamp_validity=tv)

    def test_categories(self):
        """Valid shortcuts to full category names"""
        tv = TimeValidity.objects.get(creation_date=datetime.date.today(), is_valid=True)
        Vcategories = [
            ("PC", 'procedure'),
            ("PP", 'property'),
            ('LM', 'lemma'),
            ('AS', 'assertion'),
            ('IN', 'invariant'),
            ('PR', 'precondition'),
            ('PO', 'postcondition'),
        ]
        for cat in Vcategories:
            scat1 = SectionCategory.objects.get(category=cat[0], timestamp_validity=tv)
            self.assertEqual(scat1.get_full_name(), cat[1])

        print("#MODELS: SECTION CATEGORY# VALID CATEGORY NAMES TEST: OK")


class ValidSectionStatusNamesTestCase(TestCase):
    def setUp(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        SectionStatus.objects.create(status="PR", timestamp_validity=tv)
        SectionStatus.objects.create(status="IN", timestamp_validity=tv)
        SectionStatus.objects.create(status="CE", timestamp_validity=tv)
        SectionStatus.objects.create(status="UC", timestamp_validity=tv)

    def test_sections(self):
        """Valid shortcuts to full section status names"""
        tv = TimeValidity.objects.get(creation_date=datetime.date.today(), is_valid=True)
        secs1 = SectionStatus.objects.get(status="PR", timestamp_validity=tv)
        self.assertEqual(secs1.get_full_name(), "proved")
        secs1 = SectionStatus.objects.get(status="IN", timestamp_validity=tv)
        self.assertEqual(secs1.get_full_name(), "invalid")
        secs1 = SectionStatus.objects.get(status="CE", timestamp_validity=tv)
        self.assertEqual(secs1.get_full_name(), "counterexample")
        secs1 = SectionStatus.objects.get(status="UC", timestamp_validity=tv)
        self.assertEqual(secs1.get_full_name(), "unchecked")

        print("#MODELS: SECTION STATUS# VALID SECTION STATUS NAMES TEST: OK")


class StatusDataBigDataTestCase(TestCase):
    def setUp(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        usr = User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)
        StatusData.objects.create(
            status_data_field="😠😭🙎✨🚀AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            user=usr, timestamp_validity=tv)

    def test_big_data(self):
        """Handles big description and UTF-8 in status data field"""
        usr = User.objects.get(login="temp")
        stat = StatusData.objects.get(user=usr)
        self.assertEqual(stat.status_data_field,
                         "😠😭🙎✨🚀AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        print("#MODELS: STATUS DATA# LONG NAMES TEST: OK")


class UserCoherenceTestCase(TestCase):
    def setUp(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        User.objects.create(login="😠😭🙎✨🚀", name="😠😭🙎✨🚀😠😭🙎✨🚀", password="😠😭🙎✨🚀😠😭🙎✨🚀😠😭🙎✨🚀",
                            timestamp_validity=tv)

    def test_user_model(self):
        """Checking coherence between submited user data and data in the database"""
        usr = User.objects.get(login="😠😭🙎✨🚀")
        self.assertEqual(usr.login, "😠😭🙎✨🚀")
        self.assertEqual(usr.name, "😠😭🙎✨🚀😠😭🙎✨🚀")
        self.assertEqual(usr.password, "😠😭🙎✨🚀😠😭🙎✨🚀😠😭🙎✨🚀")
        print("#MODELS: USER# USER CREATING AND UTF-8 NAMES TEST: OK")


class TimeValCoherenceTestCase(TestCase):
    def setUp(self):
        TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)

    def test_timeval_model(self):
        """Checking coherence between submited timeValidity data and data in the database"""
        tv = TimeValidity.objects.get(creation_date=datetime.date.today())
        self.assertEqual(tv.creation_date, datetime.date.today())
        self.assertEqual(tv.is_valid, True)
        print("#MODELS: TIME VALIDITY# TIME VALIDITY COHERENCE TEST: OK")


# ///////////////////////////////////////// FORMS TESTS ///////////////////////////////////////////

from framac.forms import FileForm, DirectoryForm, DeleteDirForm, ProverForm, VeriFrorm


class DirectoryFormTestCase(TestCase):
    def test_valid_form(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        usr = User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)
        test_dir = Directory.objects.create(name="rootąąążżż", creation_date=datetime.date.today(),
                                            timestamp_validity=tv,
                                            owner=usr,
                                            availability_flag=True)

        data = {'name': test_dir.name, 'owner': test_dir.owner, 'placed_in': test_dir.is_placed_in}
        form = DirectoryForm(data=data)
        self.assertTrue(form.is_valid())

        print("#FORM: DIRECTORY# VALID DIRECTORIES: OK")

    def test_invalid_form(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        usr = User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)
        test_dir = Directory.objects.create(name="   ", creation_date=datetime.date.today(), timestamp_validity=tv,
                                            owner=usr,
                                            availability_flag=True)

        data = {'name': test_dir.name, 'owner': test_dir.owner, 'placed_in': test_dir.is_placed_in}
        form = DirectoryForm(data=data)
        self.assertFalse(form.is_valid())
        print("#FORM: DIRECTORY# INVALID DIRECTORIES: OK")


class FileFormTestCase(TestCase):
    def test_invalid_form(self):
        actual_file = SimpleUploadedFile(
            "best_file_eva.txt",
            b"these are the file contents!"
        )
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        usr = User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)
        test_file = File.objects.create(name="file", creation_date=datetime.date.today(), code=actual_file,
                                        timestamp_validity=tv, owner=usr, availability_flag=True)

        data = {'name': test_file.name, 'owner': test_file.owner.name, 'file': actual_file}
        form = FileForm(data=data)
        self.assertFalse(form.is_valid())

        data = {'name': test_file.name, 'owner': test_file.owner.name}
        form = FileForm(data=data)
        self.assertFalse(form.is_valid())

        data = {'name': "", 'owner': test_file.owner.name}
        form = FileForm(data=data)
        self.assertFalse(form.is_valid())
        print("#FORM: FILE# INVALID FILE: OK")


class DeleteTargetFormTestCase(TestCase):
    def test_valid_form(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        usr = User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)
        variables.user_model = usr
        test_dir = Directory.objects.create(name="rootąąążżż", creation_date=datetime.date.today(),
                                            timestamp_validity=tv,
                                            owner=usr,
                                            availability_flag=True)

        data = {'choice': 'd' + test_dir.name}
        form = DeleteDirForm(data=data)
        self.assertTrue(form.is_valid())

        actual_file = SimpleUploadedFile(
            "best_file_eva.txt",
            b"these are the file contents!"
        )

        test_file = File.objects.create(name="file", creation_date=datetime.date.today(), code=actual_file,
                                        timestamp_validity=tv, owner=usr, availability_flag=True)

        data = {'choice': 'f' + test_file.name}
        form = DeleteDirForm(data=data)
        self.assertTrue(form.is_valid())
        print("#FORM: DELETE# VALID DELETE: OK")

    def test_invalid_form(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        usr = User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)
        variables.user_model = User.objects.create(login="temp1", name="temp1", password="temp1", timestamp_validity=tv)
        test_dir = Directory.objects.create(name="rootąąążżż", creation_date=datetime.date.today(),
                                            timestamp_validity=tv,
                                            owner=usr,
                                            availability_flag=True)

        data = {'choice': 'd' + test_dir.name}
        form = DeleteDirForm(data=data)
        self.assertFalse(form.is_valid())

        actual_file = SimpleUploadedFile(
            "best_file_eva.txt",
            b"these are the file contents!"
        )

        variables.user_model = usr
        test_file = File.objects.create(name="file", creation_date=datetime.date.today(), code=actual_file,
                                        timestamp_validity=tv, owner=usr, availability_flag=True)

        data = {'choice': test_file.name}
        form = DeleteDirForm(data=data)
        self.assertFalse(form.is_valid())
        print("#FORM: DELETE# INVALID DELETE: OK")


class ProverFormTestCase(TestCase):
    def test_valid_form(self):
        data = {'Provers': 'alt-ergo'}
        form = ProverForm(data=data)
        self.assertTrue(form.is_valid())

        data = {'Provers': 'Z3'}
        form = ProverForm(data=data)
        self.assertTrue(form.is_valid())

        data = {'Provers': 'cvc4'}
        form = ProverForm(data=data)
        self.assertTrue(form.is_valid())
        print("#FORM: PROVERS# VALID PROVERS: OK")

    def test_invalid_form(self):
        data = {'Provers': 'Alt-Ergo'}
        form = ProverForm(data=data)
        self.assertFalse(form.is_valid())

        data = {'Provers': 'z3'}
        form = ProverForm(data=data)
        self.assertFalse(form.is_valid())

        data = {'Provers': 'CVC4'}
        form = ProverForm(data=data)
        self.assertFalse(form.is_valid())

        data = {'Provers': 'cvc4:1.6'}
        form = ProverForm(data=data)
        self.assertFalse(form.is_valid())
        print("#FORM: PROVERS# INVALID PROVERS: OK")


class VeriFormTestCase(TestCase):
    def test_valid_form(self):
        CHOICES = [
            ' -wp-rte',
            '-@lemma',
            '-@requires',
            '-@assigns',
            '-@ensures',
            '-@exits',
            '-@assert',
            '-@check',
            '-@invariant',
            '-@variant',
            '-@breaks',
            '-@continues',
            '-@returns',
            '-@complete_behaviors',
            '-@disjoint_behaviors'
        ]

        for choice in CHOICES:
            data = {'Provers': choice}
            form = VeriFrorm(data=data)
            self.assertTrue(form.is_valid())
        print("#FORM: VERIFICATION CONDITIONS# VALID VS'S: OK")

    def test_invalid_form(self):
        CHOICES = [
            ('-wp- dasdasdasdarte', 'abb'),
            '-@ lemma',
            '@requires',
            '-assigns',
            '-@ensure',
            '-@',
            '-',
            '-@c',
            '-@inv',
            'riant',
            '-ks',
            '-@-@',
            '-@retu rns',
            '- @complete_behaviors',
            '-@ disjoint_behaviors'
        ]

        for choice in CHOICES:
            data = {'Properties': choice}
            form = VeriFrorm(data=data)
            self.assertFalse(form.is_valid())
        print("#FORM: VERIFICATION CONDITIONS# INVALID VS'S: OK")


# /////////////////////////////////////////////// VIEWS TESTS ////////////////////////////////////////////////////////

from django.urls import reverse


class AddFileViewsTest(TestCase):
    def setUp(self):
        response = self.client.post(reverse('addDirectory'), {
            'name': 'root',
            'description': 'test_description',
            'placed_in': ''
        })
        self.assertEqual(response.status_code, 200)

    def testPageOpening(self):
        response = self.client.get(reverse('addFile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/addFile.html')

    def testValidFile(self):
        actual_file = SimpleUploadedFile(
            "best_file_eva.txt",
            b"these are the file contents!"
        )

        response = self.client.post(reverse('addFile'), {
            'name': 'test_file1',
            'description': 'test_description',
            'owner': 'delavock',
            'file': actual_file,
            'placed_in': '/root'
        })
        self.assertEqual(response.status_code, 302)

    def testInvalidFiles(self):
        actual_file = SimpleUploadedFile(
            "best_file_eva.txt",
            b"these are the file contents!"
        )

        response = self.client.post(reverse('addFile'), {
            'name': 'test_file',
            'description': 'test_description',
            'owner': '',
            'file': actual_file,
            'placed_in': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaax'
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('addFile'), {
            'name': 'root',
            'description': 'test_description',
            'owner': '',
            'file': actual_file,
            'placed_in': 'root'
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('addedFile'))
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        response = self.client.post(reverse('delete'), {
            'choice': 'd/root',
        })
        self.assertEqual(response.status_code, 302)

        print("#VIEWS: ADDING FILES#: OK")


class DirectoryViewsTest(TestCase):
    def setUp(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)

        response = self.client.post(reverse('login'), {
            'login': 'temp',
            'password': 'temp'
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('addDirectory'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/addDirectory.html')

    def testMainPageText(self):
        response = self.client.post(reverse('addDirectory'), {
            'name': 'root',
            'description': 'test_description',
            'placed_in': ''
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('addDirectory'), {
            'name': 'subroot',
            'description': 'test_description',
            'placed_in': '/root'
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('addedDirectory'))
        self.assertEqual(response.status_code, 200)

    def testInvalidDirectory(self):
        response = self.client.post(reverse('addDirectory'), {
            'name': 'rootaa',
            'description': 'test_description',
            'placed_in': '/dasdasdasdasdsa'
        })
        self.assertEqual(response.status_code, 200)

        print("#VIEWS: ADDING DIRECTORIES#: OK")


def universalSetUp(self):
    actual_file = SimpleUploadedFile(
        "test.c",
        b"int max(int *a, int len) {}"
    )

    tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
    User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)

    response = self.client.post(reverse('login'), {
        'login': 'temp',
        'password': 'temp'
    })
    self.assertEqual(response.status_code, 302)

    response = self.client.post(reverse('addDirectory'), {
        'name': 'root',
        'description': 'test_description',
        'placed_in': ''
    })
    self.assertEqual(response.status_code, 200)

    response = self.client.post(reverse('addFile'), {
        'name': 'test_file',
        'description': '',
        'owner': 'Neofine',
        'file': actual_file,
        'placed_in': '/root'
    })
    self.assertEqual(response.status_code, 302)


class DeleteTargetTest(TestCase):
    def setUp(self):
        universalSetUp(self)

        response = self.client.get(reverse('delete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/delete.html')

        response = self.client.get(reverse('deleteDone'))
        self.assertEqual(response.status_code, 200)

    def testMainPageText(self):
        response = self.client.post(reverse('delete'), {
            'choice': 'f/root/test_file',
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('delete'), {
            'choice': 'd/root',
        })
        self.assertEqual(response.status_code, 302)

        print("#VIEWS: DELETING FILES AND DIRECTORIES#: OK")


class ShowFileViewsTest(TestCase):
    def setUp(self):
        universalSetUp(self)

    def testMainPageText(self):
        response = self.client.get('/files/root/test_file')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/index.html')

        print("#VIEWS: SHOWING FILES#: OK")


class ProversTabViewsTest(TestCase):
    def testMainPageText(self):
        response = self.client.get(reverse('provers'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/index.html')

        response = self.client.post(reverse('provers'), {
            'Provers': 'Z3'
        })
        self.assertContains(response, 'Submit saved!')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/index.html')

        print("#VIEWS: SETTING PROVERS#: OK")


class VerificationTabViewsTest(TestCase):
    def testMainPageText(self):
        response = self.client.get(reverse('verification'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/index.html')

        response = self.client.post(reverse('verification'), {
            'Properties': [' -wp-rte', '-@requires', '-@exits']
        })
        self.assertContains(response, 'Submit saved!')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/index.html')

        print("#VIEWS: SETTING VERIFICATIONS#: OK")


class ResultTabViewsTest(TestCase):
    def setUp(self):
        universalSetUp(self)

    def testMainPageText(self):
        response = self.client.post(reverse('verification'), {
            'Properties': [' -wp-rte', '-@requires', '-@exits']
        })
        self.assertContains(response, 'Submit saved!')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/files/root/test_file')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/index.html')

        response = self.client.get(reverse('result'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/index.html')

        print("#VIEWS: RESULT BUTTON#: OK")


class RerunViewsTest(TestCase):
    def setUp(self):
        universalSetUp(self)

    def testMainPageText(self):
        response = self.client.post(reverse('verification'), {
            'Properties': [' -wp-rte', '-@requires', '-@exits']
        })
        self.assertContains(response, 'Submit saved!')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/files/root/test_file')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/index.html')

        response = self.client.get(reverse('rerun'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/index.html')

        print("#VIEWS: RERUN BUTTON#: OK")


class LoginViewsTest(TestCase):
    def setUp(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)

    def testMainPageText(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'framac/login.html')

        response = self.client.post(reverse('login'), {
            'login': 'temp',
            'password': 'temp'
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('login'), {
            'login': 'temp111',
            'password': 'temp111'
        })
        self.assertEqual(response.status_code, 200)

        print("#VIEWS: LOGIN#: OK")


class LogoutViewsTest(TestCase):
    def testMainPageText(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

        print("#VIEWS: LOGOUT#: OK")


import os
from .file_parser import make_sections, parse_framac

class TestFileSectionParser(TestCase):
    def testMainPageText(self):
        f = open("framac/testing/valid.c", "r")
        good = open("framac/testing/valid.out", "r")

        self.assertEqual(parse_framac(f.read()), good.read())

        print("#VIEWS: FILE PARSER#: OK")


class TestSectionMaking(TestCase):

    def testMainPageText(self):
        tv = TimeValidity.objects.create(creation_date=datetime.date.today(), is_valid=True)
        usr = User.objects.create(login="temp", name="temp", password="temp", timestamp_validity=tv)

        f = open("framac/testing/valid.c", "r")
        make_sections(f, usr, None)

        self.assertEqual(4, len(SectionCategory.objects.all()))

        print("#VIEWS: SECTION MAKER#: OK")


import unittest
import os
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from webdriver_manager.firefox import GeckoDriverManager
import time


class TestLoggingIn(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())

    def test_signup_fire(self):
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.find_element_by_id('id_login').send_keys("Neofine")
        self.driver.find_element_by_id('id_password').send_keys("Neofine")
        self.driver.find_element_by_id('submit').click()
        try:
            self.driver.find_element_by_id('id_login')
            self.assertFalse(True)
        except:
            self.driver.find_element_by_id('logout').click()

    def tearDown(self):
        self.driver.quit()
        print("#VIEWS: LOGGING IN + OUT# OK")


class TestFileManagement(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.find_element_by_id('id_login').send_keys("Neofine")
        self.driver.find_element_by_id('id_password').send_keys("Neofine")
        self.driver.find_element_by_id('submit').click()

    def test_signup_fire(self):
        self.driver.find_element_by_id('addFile').click()
        self.driver.find_element_by_id('id_name').send_keys("selenium_test_file")
        self.driver.find_element_by_id('id_file').send_keys(os.getcwd() + "/valid1fast.c")
        self.driver.find_element_by_id('submit').click()

        self.driver.find_element_by_id('addFile')
        self.driver.find_element_by_id('menu').click()

        self.driver.find_element_by_id('delete').click()
        self.driver.find_element_by_id('id_choice').send_keys("/selenium_test_file")
        self.driver.find_element_by_id('submit').click()

        self.driver.find_element_by_id('delete')
        self.driver.find_element_by_id('menu').click()

    def tearDown(self):
        self.driver.find_element_by_id('logout').click()
        self.driver.quit()
        print("#VIEWS: ADDING AND DELETING FILES# OK")


class TestFileVisibility(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.find_element_by_id('id_login').send_keys("Neofine")
        self.driver.find_element_by_id('id_password').send_keys("Neofine")
        self.driver.find_element_by_id('submit').click()

    def test_signup_fire(self):
        self.driver.find_element_by_id('addFile').click()
        self.driver.find_element_by_id('id_name').send_keys("selenium_test_file")
        self.driver.find_element_by_id('id_file').send_keys(os.getcwd() + "/valid1fast.c")
        self.driver.find_element_by_id('submit').click()

        self.driver.find_element_by_id('addFile')
        self.driver.find_element_by_id('menu').click()

        self.driver.find_element_by_xpath('//a[@href="' + "/files/selenium_test_file" + '"]').click()
        time.sleep(15)
        self.driver.find_element_by_id('f1g1').click()

        self.driver.find_element_by_id('delete').click()
        self.driver.find_element_by_id('id_choice').send_keys("/selenium_test_file")
        self.driver.find_element_by_id('submit').click()

        self.driver.find_element_by_id('delete')
        self.driver.find_element_by_id('menu').click()

    def tearDown(self):
        self.driver.find_element_by_id('logout').click()
        self.driver.quit()
        print("#VIEWS: SHOWING ADDED FILES + FOCUS ON PROGRAM ELEMENTS + HIDING SEGMENTS# OK")


class TestAddingFileToDirectory(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.find_element_by_id('id_login').send_keys("Neofine")
        self.driver.find_element_by_id('id_password').send_keys("Neofine")
        self.driver.find_element_by_id('submit').click()

    def test_signup_fire(self):
        self.driver.find_element_by_id('addDir').click()
        self.driver.find_element_by_id('id_name').send_keys("selenium_root")
        self.driver.find_element_by_id('submit').click()

        self.driver.find_element_by_id('addDir')
        self.driver.find_element_by_id('menu').click()

        self.driver.find_element_by_id('addFile').click()
        self.driver.find_element_by_id('id_name').send_keys("selenium_test_file")
        self.driver.find_element_by_id('id_file').send_keys(os.getcwd() + "/valid1fast.c")
        self.driver.find_element_by_id('id_placed_in').send_keys("/selenium_root")
        self.driver.find_element_by_id('submit').click()

        self.driver.find_element_by_id('addFile')
        self.driver.find_element_by_id('menu').click()

        self.driver.find_element_by_xpath('//a[@href="' + "/files/selenium_root/selenium_test_file" + '"]')

        self.driver.find_element_by_id('delete').click()
        self.driver.find_element_by_id('id_choice').send_keys("/selenium_root")
        self.driver.find_element_by_id('submit').click()

        self.driver.find_element_by_id('delete')
        self.driver.find_element_by_id('menu').click()
        self.driver.find_element_by_id('color').click()

    def tearDown(self):
        self.driver.find_element_by_id('logout').click()
        self.driver.quit()
        print("#VIEWS: VALID FILE SELECTION DIALOG VIEW + CHANGING COLOR# OK")


class TestVerificationConditions(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.find_element_by_id('id_login').send_keys("Neofine")
        self.driver.find_element_by_id('id_password').send_keys("Neofine")
        self.driver.find_element_by_id('submit').click()

    def test_signup_fire(self):
        self.driver.find_element_by_id('addFile').click()
        self.driver.find_element_by_id('id_name').send_keys("selenium_test_file")
        self.driver.find_element_by_id('id_file').send_keys(os.getcwd() + "/valid1fast.c")
        self.driver.find_element_by_id('submit').click()

        self.driver.find_element_by_id('addFile')
        self.driver.find_element_by_id('menu').click()

        self.driver.find_element_by_xpath('//a[@href="' + "/files/selenium_test_file" + '"]').click()
        time.sleep(15)

        self.driver.find_element_by_id('vcs').click()
        self.driver.find_element_by_id('id_Properties_0').click()
        self.driver.find_element_by_id('submitP').click()

        self.driver.find_element_by_id('rerun').click()
        time.sleep(15)

        self.driver.find_element_by_id('Gf1g11')

    def tearDown(self):
        self.driver.find_element_by_id('logout').click()
        self.driver.quit()
        print("#VIEWS: VERIFICATION CONDITIONS# OK")


class TestResults(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.find_element_by_id('id_login').send_keys("Neofine")
        self.driver.find_element_by_id('id_password').send_keys("Neofine")
        self.driver.find_element_by_id('submit').click()

    def test_signup_fire(self):
        self.driver.find_element_by_id('addFile').click()
        self.driver.find_element_by_id('id_name').send_keys("selenium_test_file")
        self.driver.find_element_by_id('id_file').send_keys(os.getcwd() + "/valid1fast.c")
        self.driver.find_element_by_id('submit').click()

        self.driver.find_element_by_id('addFile')
        self.driver.find_element_by_id('menu').click()

        self.driver.find_element_by_xpath('//a[@href="' + "/files/selenium_test_file" + '"]').click()
        time.sleep(15)

        default = self.driver.find_element_by_id('fope').text

        self.driver.find_element_by_id('result').click()
        time.sleep(15)

        self.assertEqual(self.driver.find_element_by_id('prover_tab').text[:4], '[wp]')

        self.driver.find_element_by_id('provers').click()
        self.driver.find_element_by_id('id_Provers_1').click()
        self.driver.find_element_by_id('submitP').click()

        self.driver.find_element_by_id('rerun').click()
        time.sleep(15)

        prover_altered = self.driver.find_element_by_id('fope').text

        self.assertNotEqual(default, prover_altered)

    def tearDown(self):
        self.driver.find_element_by_id('logout').click()
        self.driver.quit()
        print("#VIEWS: RESULTS AND PROVERS# OK")