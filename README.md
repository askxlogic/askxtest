# askxtest

This is simple Python script for running only one Xcode test method from command line.

### Requirements:
  All your tests should be in separate folder. All your tests should have same list of test methods. You should have shared build scheme for test target. Currently this script does not support workspaces (only projects), but you can extend it as you want for your goals.
  
### Using:
  Look at examlple_of _using folder. Use 
  ```bash
  $ ./askxtest.py -h
  ```
  for get help.
