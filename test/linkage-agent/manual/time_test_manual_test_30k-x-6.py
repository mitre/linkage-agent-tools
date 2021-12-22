# ------
#
# This test is not part of the automated test suite.  It is intended to be
# run manually after the data folder has been copied to C:\test.
#
# This module exists primarily to enable debugging of the process called by the cmd line
#
# ------

import time_test as tt

if __name__ == "__main__":
    tt.run_test("C:\\test\\test-set-30k-x-6")
