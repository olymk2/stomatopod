
class testset(object):
    count = 0

    def __init__(self, name='testset', success_msg='Great scott these tests passed !', failure_msg='This encounter could create a time paradox !', verbose=False):
        sys.stdout = StringIO()
        self.name = name
        self.success_message = success_msg
        self.failure_message = failure_msg
        self.results = []
        self.verbose = verbose
        self.count_tests = 0
        self.count_success = 0
        self.count_failures = 0

    def append(self, test, error='\033[94mGreat scott something is wrong in the universe!'):
        self.results.append((
            test,
            error
            ))

    def finish(self):
        sys.stdout = sys.__stdout__
        for result, error in self.results:
            if result is True:
                self.count_success += 1
            else:
                print('\t\033[94mError in test %s %s' % (self.count_tests, error))
                self.count_failures += 1
            self.count_tests += 1

        self.count += self.count_tests
        if self.count_tests == self.count_success:
            if self.verbose is True:
                print('\t\033[92m%s out of %s %s tests passed - %s\033[0m' % (self.count_success, self.count_tests, self.name, self.success_message))
        else:
            print('\t\033[93m%s out of %s %s tests failed  - %s\033[0m' % (self.count_failures, self.count_tests, self.name, self.failure_message))
        return self.count_failures
