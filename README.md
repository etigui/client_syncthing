<h1>Syncthing client <img src="/images/syg.png"></h1>

Syncthing is a free, open-source peer-to-peer file synchronization application available for Windows, Mac, Linux, Android, Solaris, Darwin, and BSD. It can sync files between devices on a local network, or between remote devices over the Internet. Data security and data safety are built into the design of the software. In this project, we only implemented the client which can downaload file from an other Syncthing node. The client only works with Python 3.6, cause we did not check with any other version yet. The client works without LZ4 compression. We had many problem to find the right version and make it works.

## Library (Ubuntu, Python)
To compile the protobuf3 struct file, you need to install protoc:  

    $> sudo apt-get install protobuf-compiler  
<br/>
You also need to install protobuf3 and google:

    $> sudo pip3 install google
    $> sudo pip3 install google-apputils
    $> sudo pip3 install protobuf3 
<br/>
If error with protobuf3  
`sudo pip3 install —upgrade protobuf==3.5.1`  

## Execution
You can run the client normal mode:  

    $> python3.6 main.py -d /home/<user>/Documents/syncthing/ -c cert.pem -k key.pem -i x.x.x.x -p 22000
<br/>
You can run the client with verbose mode (with the `-v` at the end):  
    
    $> python3.6 main.py -d /home/<user>/Documents/syncthing/ -c cert.pem -k key.pem -i x.x.x.x -p 22000 -v  
<br/>
Client help (argparse):  

    usage: Syncthing client [-h] -d SYNC_DIRECTORY -c CERT -k KEY -i IP -p PORT [-v]
    optional arguments:
      -h, --help            Show this help message and exit
      -d SYNC_DIRECTORY, --directory SYNC_DIRECTORY 
                            Main sync directory
      -c CERT, --cert CERT  Certificate file
      -k KEY, --key KEY     Private key file
      -i IP, --ip IP        Server IP
      -p PORT, --port PORT  Server port
      -v, --verbose         Increase output verbosity


## Execution test
**Test 1:**
- Console output of client execution in verbose mode for the folder `guizell` (own local Syncthing node) => [HERE](test/test1_output.txt)
- Execution `ls -R -l` to get all file info about this test => [HERE](test/test1_ls.txt)

**Test 2:**
- Console output of client execution in verbose mode for the folder `facile` and `moins_facile` (Heardt Syncthing node) => [HERE](test/test2_output.txt)
- Execution `ls -R -l` to get all file info about this test => [HERE](test/test2_ls.txt)

**Test 3:**
- Console output of client execution in verbose mode for the folder `facile` (Heardt Syncthing node) => [HERE](test/test3_output.txt)
- Execution `ls -R -l` to get all file info about this test => [HERE](test/test3_ls.txt)

**Test 4:**
- Console output of client execution in verbose mode for the folder `moins_facile` (Heardt Syncthing node) => [HERE](test/test4_output.txt)
- Execution `ls -R -l` to get all file info about this test => [HERE](test/test4_ls.txt)


This screen is like the test n°3 but not in verbose mode. We cannot have all the output cause there are too much file to process.   
<img src="/test/test_output.png" width="70%" >
