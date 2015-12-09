#!/usr/bin/python

from config import Config
import os
import xml.etree.ElementTree as ElementTree
import subprocess
import argparse


class XCTestManager(object):
    def __init__(self):
        config_file = file('askxtest.cfg')
        config_object = Config(config_file)
        self.__default_method_alias = config_object.default_test_method_alias
        self.__test_methods = dict(config_object.test_methods)
        self.__project_path = config_object.project_path
        self.__project = config_object.project
        self.__schemes_path = config_object.schemes_path
        self.__tests_path = config_object.tests_path
        self.__current_test_method = self.__test_methods[self.__default_method_alias]
        self.__current_test_method_alias = self.__default_method_alias
        self.__test_list = None
        self.__test_scheme_file_name = 'temptest.xcscheme'
        self.__source_scheme_file_name = config_object.source_scheme_filename
        self.__test_run_destination = config_object.test_run_destination
        self.__external_files = dict(config_object.external_files)
        config_file.close()

    ###################################

    def __update_test_list(self):
        """
        Reload list of tests from testsPath
        :return:
        """
        testsPath = self.__project_path + self.__tests_path
        self.__test_list = [os.path.splitext(testList)[0] for testList in os.listdir(testsPath)]

    def get_test_list(self):
        """
        :return: List of tests
        """
        self.__update_test_list()
        return self.__test_list

    def get_methods_list(self):
        """
        :return: List of environments
        """
        return self.__test_methods.keys()

    def get_current_test_method(self):
        """
        :return: Current environment
        """
        return self.__current_test_method_alias

    def set_current_test_method(self, current_test_method_alias):
        """
        Set current environment value
        :raise XCTestManagerError if value is wrong
        :param current_test_method_alias:
        :return:
        """
        if current_test_method_alias in self.__test_methods.keys():
            self.__current_test_method_alias = current_test_method_alias
            self.__current_test_method = self.__test_methods[current_test_method_alias]
        else:
            self.__current_test_method_alias = self.__default_method_alias
            self.__current_test_method = self.__test_methods[self.__default_method_alias]
            raise XCTestManagerError("Wrong environment value")

    def __create_temp_scheme_for_test(self, test):
        """
        Prepare xcscheme file for test
        :param test: File name of integration test without extention
        :return:
        """
        os.chdir(self.__project_path + self.__schemes_path)
        scheme_tree = ElementTree.parse(self.__source_scheme_file_name)
        root = scheme_tree.getroot()
        skipped_tests_element = root.findall('./TestAction/Testables/TestableReference/SkippedTests')
        if len(skipped_tests_element) == 0:
            testable_reference_element = root.findall('./TestAction/Testables/TestableReference')[0]
            skipped_tests_element = ElementTree.SubElement(testable_reference_element, "SkippedTests")
        else:
            skipped_tests_element = skipped_tests_element[0]

        # Delete all OUR tests
        if len(skipped_tests_element) > 0:
            for test_element in root.findall('./TestAction/Testables/TestableReference/SkippedTests/Test'):
                for legal_test_name in self.__test_list:
                    if legal_test_name in test_element.attrib['Identifier']:
                        skipped_tests_element.remove(test_element)

        # Add skipped tests from test list
        unused_tests_list = list(self.__test_list)
        unused_tests_list.remove(test)

        for unused_test in unused_tests_list:
            test_element = ElementTree.SubElement(skipped_tests_element, "Test", {'Identifier': unused_test})
            ElementTree.SubElement(test_element, None)

        # Add skipped methods from methods list
        unused_test_methods_list = list(self.__test_methods.values())
        unused_test_methods_list.remove(self.__current_test_method)

        for unused_test_method in unused_test_methods_list:
            unused_test = test + "/" + unused_test_method
            test_element = ElementTree.SubElement(skipped_tests_element, "Test", {'Identifier': unused_test})
            ElementTree.SubElement(test_element, None)

        scheme_tree.write(self.__test_scheme_file_name)

    def __build_and_run_test(self):
        """
        Run build and test and remove xcscheme file after complition
        :return: Test output
        """
        os.chdir(self.__project_path)
        scheme = self.__test_scheme_file_name.split(".")[0]
        destination = self.__test_run_destination
        run_test_command = ["xcodebuild", "-project", self.__project,
                            "-scheme", scheme, '-destination', destination,
                            "-sdk", "iphonesimulator", "test"]
        try:
            test_output = subprocess.check_output(run_test_command)
        except subprocess.CalledProcessError, exception:
            test_output = exception.output

        os.chdir(self.__project_path + self.__schemes_path)
        os.remove(self.__test_scheme_file_name)
        return test_output

    def test(self, test):
        """
        Create temporary xcscheme file, run test and remove this file
        :param test: Name of test from __testList
        :return: Test output
        """
        self.__update_test_list()
        if test in self.__test_list:
            self.__create_temp_scheme_for_test(test)
            return self.__build_and_run_test()
        else:
            raise XCTestManagerError("Wrong testName value")

    def get_external_files_aliases(self):
        """
        :return: Aliases for all supported external files
        """
        return self.__external_files.keys()

    def write_external_file(self, external_file_alias, data):
        """
        Set date for external file
        :param external_file_alias: Alias for external file which will be changed
        :param data: Data which will be saved in file as text
        :return:
        """
        if external_file_alias in self.__external_files.keys():
            ext_file_dict = dict(self.__external_files[external_file_alias])
            os.chdir(self.__project_path + ext_file_dict['path'])
            external_file = open(ext_file_dict['filename'], 'w')
            external_file.write(data)
            external_file.close()
        else:
            raise XCTestManagerError("Wrong file alias")

    def read_external_file(self, external_file_alias):
        """
        Read external file with alias
        :param external_file_alias: Alias for external file which will be read
        :return: File data as string
        """
        if external_file_alias in self.__external_files.keys():
            ext_file_dict = dict(self.__external_files[external_file_alias])
            os.chdir(self.__project_path + ext_file_dict['path'])
            external_file = open(ext_file_dict['filename'], 'r')
            file_data = external_file.read()
            external_file.close()
            return file_data
        else:
            raise XCTestManagerError("Wrong file alias")


class XCTestManagerError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


if __name__ == "__main__":
    tester = XCTestManager()
    test_list = list(tester.get_test_list())
    methods_list = list(tester.get_methods_list())
    file_list = list(tester.get_external_files_aliases())

    parser = argparse.ArgumentParser(description='Run xcode unit tests.')
    parser.add_argument('-t', choices=test_list, required=False,
                        help='Name of running test. Allowed values are: ' + ', '.join(test_list),
                        metavar='test_name')
    parser.add_argument('-m', choices=methods_list, required=False,
                        help='Name of method in running test. \
                              Without this argument will be run \
                              default method \"' + tester.get_current_test_method() + '\". ' +
                             'Allowed values are: ' + ', '.join(methods_list),
                        default=tester.get_current_test_method(),
                        metavar='method_name')
    parser.add_argument('-rf', choices=file_list, required=False,
                        help='Read external file. Allowed values are: ' + ', '.join(file_list),
                        metavar='file')
    parser.add_argument('-wf', nargs=2,
                        help='Write value to external file. Allowed files are: ' + ', '.join(file_list),
                        metavar=('file', 'value'))
    args = parser.parse_args()

    if args.rf is not None:
        print tester.read_external_file(args.rf)

    if args.wf is not None:
        tester.write_external_file(args.wf[0], args.wf[1])

    if args.t is not None:
        tester.set_current_test_method(args.m)
        print tester.test(args.t)

    exit(0)
