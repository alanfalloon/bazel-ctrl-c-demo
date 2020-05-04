# Bazel Ctrl-C is broken

This is to demonstrate the Bazel issue with Ctrl-C handling.

If you run this test directly, but kill it early with Ctrl-C:

    $ ./my_test.py
    ^C
    $

Then the temporary file and child process are both cleaned up. This can be
confirmed by looking for the temporary file and process:

    $ ls /tmp | grep '^ctrl-c' || echo nope
    nope
    $ ps -u $(whoami) -o pid,ppid,pgid,args | grep '[w]hile sleep 1; do echo working' || echo nope
    nope

However, if you run this through Bazel and interrupt it:

    $ bazel test //:my_test --test_output=all
    INFO: Analyzed target //:my_test (0 packages loaded, 0 targets configured).
    INFO: Found 1 test target...
    [1 / 2] Testing //:my_test; 5s darwin-sandbox
    ^C
    Bazel caught interrupt signal; shutting down.
    Target //:my_test up-to-date:
    bazel-bin/my_test
    ERROR: build interrupted
    INFO: Elapsed time: 6.248s, Critical Path: 5.80s
    INFO: 0 processes.
    FAILED: Build did NOT complete successfully
    //:my_test                                                            NO STATUS

    FAILED: Build did NOT complete successfully

Then the temporary file and child process both still exist:

    $ ls /tmp | grep '^ctrl-c' || echo nope
    ctrl-c-vmixyju9
    $ ps -u $(whoami) -o pid,ppid,pgid,args | grep '[w]hile sleep 1; do echo working' || echo nope
    14739     1 14739 /bin/sh -c while sleep 1; do echo working ; done

This is because Bazel just sends a SIGKILL to the process group. This kills the
script immediately without allowing it to clean up. Also, because the child
process has a fresh session it does not receive the SIGKILL and runs forever.
